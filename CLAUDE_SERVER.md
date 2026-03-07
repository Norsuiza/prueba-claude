# Servidor ChatPoli — PythonAnywhere

## URL de producción
```
https://Norsuiza.pythonanywhere.com
```

## Verificar estado
```
GET https://Norsuiza.pythonanywhere.com/api/health
→ {"status": "ok", "message": "Servidor IPH activo"}
```

## Archivos del servidor
Alojados en PythonAnywhere bajo el usuario `Norsuiza`:
- `~/app.py` — Flask API
- `~/requirements.txt`
- `~/iph_app.db` — SQLite (persiste entre reinicios)

## Reiniciar el servidor
Dashboard → Web → botón **Reload** (necesario tras cambios en app.py)

## Ver logs de errores
Dashboard → Web → **Error log**

## Actualizar el código
1. Modificar `server/app.py` localmente
2. Subir el archivo en Dashboard → Files → reemplazar `app.py`
3. Web → Reload

## Nota importante
PythonAnywhere free tier reinicia la app si está inactiva por mucho tiempo,
pero la base de datos SQLite persiste en disco.
Si la app "despierta" lento en la primera petición, es normal (cold start ~2s).
