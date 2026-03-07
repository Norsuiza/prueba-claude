# ChatPoli — Sistema IPH

App Android para Oficiales de Tránsito de Culiacán, Sinaloa.
Chatbot que guía al oficial para llenar el IPH-Delitos (Informe Policial Homologado 2019) y genera el PDF oficial con datos sobreimpresos sobre la plantilla original.

## Stack
- **Mobile**: Kivy 2.3.0 + Python (compilado a APK con buildozer)
- **Backend**: Flask + SQLAlchemy + JWT + SQLite
- **PDF**: PyMuPDF (fitz) — overlay sobre `formatos/IPH-DELITOS.pdf`
- **Servidor**: Railway (gratuito, sin sleep)

## Estructura
```
prueba-claude/
├── CLAUDE.md
├── CLAUDE_SERVER.md         ← instrucciones de deploy Railway
├── server/
│   ├── app.py               ← Flask API (auth + perfiles)
│   ├── Procfile             ← para Railway
│   └── requirements.txt
├── mobile/
│   ├── main.py              ← IPHApp entry point, Window.size para desktop
│   ├── config.py            ← get/save server URL (server_config.json)
│   ├── buildozer.spec       ← config APK (title=ChatPoli, package=chatpoli)
│   ├── screens/
│   │   ├── login_screen.py
│   │   ├── register_screen.py
│   │   ├── home_screen.py   ← grid de módulos + drawer hamburguesa
│   │   └── iph_screen.py    ← chatbot IPH con progreso y generación PDF
│   ├── utils/
│   │   ├── api_client.py    ← HTTP requests + token storage (keystore/archivo)
│   │   ├── pdf_generator.py ← overlay PyMuPDF por página/sección
│   │   └── widgets.py       ← RoundedButton, HamburgerButton, rounded_btn
│   └── data/
│       └── iph_questions.py ← ~88 preguntas con lógica condicional
└── formatos/
    └── IPH-DELITOS.pdf      ← plantilla oficial (NO modificar)
```

## Flujo principal
1. Login/Registro → JWT guardado localmente
2. Home → grid de módulos (solo IPH·Delitos activo)
3. IPHScreen → chatbot pregunta a pregunta → form_data dict
4. Al terminar → `generate_iph_pdf(form_data, user, path)` sobreimprime el PDF

## Colores (Gobierno de México)
- Verde: `#006847` → `(0.0, 0.408, 0.278, 1)`
- Rojo:  `#CE1126` → `(0.808, 0.067, 0.149, 1)`

## Convenciones
- Todas las pantallas heredan de `kivy.uix.screenmanager.Screen`
- Navegación: `self.manager.current = 'nombre_pantalla'`
- Llamadas HTTP siempre en hilo separado (`threading.Thread`), resultado vía `Clock.schedule_once`
- `dp()` para todas las medidas (adaptación a densidad de pantalla)
- El idioma del proyecto es **español**

## Pendientes clave
- Calibrar coordenadas exactas del PDF (actualmente aproximadas)
- Cubrir páginas 3, 6-7, 7-8 del PDF (testigos, continuación detenido, evidencias)
- Validación de formato fecha/hora/coordenadas
- Opción compartir PDF (WhatsApp/correo)
- Compilar y probar APK real en dispositivo Android
