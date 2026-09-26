# TamagoChatty Mobile v0.1

Primer prototipo móvil voice-first. No expone la API key al navegador: el backend hace la llamada a OpenAI. La interfaz usa el micrófono/reconocimiento de voz del navegador cuando está disponible y `speechSynthesis` para hablar **todas** las respuestas.

## Ejecutar en PC
1. Instalar Python 3.11+.
2. `pip install -r requirements.txt`
3. Definir `OPENAI_API_KEY` en el entorno.
4. `python -m uvicorn app:app --host 0.0.0.0 --port 8000`
5. En PC: abrir `http://127.0.0.1:8000`.

## iPhone
Para micrófono y modo instalable en iPhone se necesita servir la web por HTTPS. El siguiente paso es desplegar esta carpeta en un host HTTPS o usar un túnel HTTPS hacia la PC. Luego se abre la URL en Safari y se usa Compartir > Agregar a pantalla de inicio.

## Alcance v0.1
- Voz obligatoria para respuestas.
- Botón de micrófono + reconocimiento de voz si Safari lo permite.
- Memoria resumida + últimas conversaciones en SQLite.
- UI móvil/pixel inicial.
- Debug de texto oculto.

Todavía no porta objetivos, recordatorios/autonomía ni toda la base SQLite de Pixel v1.2; eso corresponde a Mobile v0.2 después de validar voz/micrófono en el iPhone.
