import json, os, sqlite3, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT=Path(__file__).parent
DB=Path(os.environ.get('TAMAGO_DB', ROOT/'tamago_mobile.sqlite3'))
MODEL=os.environ.get('OPENAI_MODEL','gpt-5.6')
KEY=os.environ.get('OPENAI_API_KEY','')

app=FastAPI(title='TamagoChatty Mobile')
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')

def db():
    c=sqlite3.connect(DB)
    c.execute('CREATE TABLE IF NOT EXISTS turns(id INTEGER PRIMARY KEY, user TEXT, reply TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
    c.commit(); return c

def setting(key,default=''):
    c=db(); r=c.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone(); c.close(); return r[0] if r else default

def save_setting(key,value):
    c=db(); c.execute('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,value)); c.commit(); c.close()

def recent(n=10):
    c=db(); rows=c.execute('SELECT user,reply FROM turns ORDER BY id DESC LIMIT ?',(n,)).fetchall(); c.close(); return list(reversed(rows))

SYSTEM='''Sos TamagoChatty, un compañero virtual voice-first. Hablás en español rioplatense, natural, cálido y conciso. Tu respuesta será leída en voz alta: evitá markdown, URLs largas, listas innecesarias y símbolos difíciles de pronunciar. Tenés memoria resumida y conversaciones recientes como contexto. No afirmes consciencia ni capacidades que no tenés. Si el usuario corrige un recuerdo, la corrección actual manda. Respondé como conversación oral. Devolvé JSON estricto con reply y memory. memory es un resumen breve de hechos/preferencias duraderos expresados por el usuario; conservá lo útil de la memoria anterior y no inventes hechos.'''

class ChatIn(BaseModel): message:str

@app.get('/')
def home(): return FileResponse(ROOT/'static'/'index.html')

@app.get('/api/status')
def status(): return {'ok':True,'model':MODEL,'has_key':bool(KEY)}

@app.post('/api/chat')
def chat(body:ChatIn):
    msg=body.message.strip()
    if not msg: raise HTTPException(400,'Mensaje vacío')
    if not KEY: raise HTTPException(500,'Falta OPENAI_API_KEY en el servidor')
    mem=setting('memory','')
    inp=[{'role':'user','content':'Contexto local: '+json.dumps({'hora_local_servidor':datetime.now().astimezone().isoformat(),'memoria':mem},ensure_ascii=False)}]
    for u,a in recent():
        inp += [{'role':'user','content':u},{'role':'assistant','content':a}]
    inp.append({'role':'user','content':msg})
    schema={'type':'object','properties':{'reply':{'type':'string'},'memory':{'type':'string'}},'required':['reply','memory'],'additionalProperties':False}
    payload={'model':MODEL,'instructions':SYSTEM,'input':inp,'store':False,'max_output_tokens':1200,'text':{'format':{'type':'json_schema','name':'voice_reply','strict':True,'schema':schema}}}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=90) as r: data=json.load(r)
    except urllib.error.HTTPError as e:
        raise HTTPException(502,f'OpenAI respondió {e.code}')
    except Exception:
        raise HTTPException(502,'No pude conectar con OpenAI')
    chunks=[]
    for item in data.get('output',[]):
        if item.get('type')=='message':
            for content in item.get('content',[]):
                if content.get('type')=='output_text': chunks.append(content.get('text',''))
    try: out=json.loads(''.join(chunks))
    except Exception: raise HTTPException(502,'Respuesta inesperada del modelo')
    c=db(); c.execute('INSERT INTO turns(user,reply) VALUES (?,?)',(msg,out['reply'])); c.commit(); c.close()
    save_setting('memory',out.get('memory',mem))
    return {'reply':out['reply']}
