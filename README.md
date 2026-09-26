# TamagoChatty Mobile v0.1 — GitHub Ready

Versión plana preparada para subir desde el navegador de GitHub sin carpetas.

Archivos esperados en la raíz del repositorio:
- app.py
- index.html
- icon.svg
- manifest.webmanifest
- sw.js
- requirements.txt
- README.md

El backend mantiene la API key fuera del navegador. Para desplegar, configurar `OPENAI_API_KEY` como variable de entorno en el hosting y ejecutar:

`uvicorn app:app --host 0.0.0.0 --port $PORT`

La app es voice-first: todas las respuestas se reproducen por voz. El texto queda como debug.
