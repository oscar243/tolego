# Tolego MVP — Bot de Telegram con Gemini

Bot conversacional en Telegram que demuestra el flujo E2E propuesto para Tolego: consulta de catálogo, comprensión de lenguaje natural con Gemini, consulta de stock y registro de pedidos. Corre en local, sin costos fijos.

## Qué hace

- **/start** — saludo y guía rápida
- **/catalogo** — navegación por categorías con botones inline
- **/pedidos** — historial de pedidos del usuario actual
- **Mensajes libres** — Gemini interpreta frases como "¿tienes Iron Man?", "quiero 2 Naruto", "cuánto cuesta el diorama". Si identifica un producto, muestra ficha con precio y stock y permite pedirlo.

La base de datos es SQLite local (`tolego.db`). El catálogo inicial se carga desde `data/catalogo.json` (~40 productos reales del catálogo 2025).

## Requisitos previos

1. **Python 3.11+** (ya lo tienes: `python --version` debe decir 3.11.9 o superior)
2. **Token de Telegram**
   - Abre Telegram y busca `@BotFather`
   - Envía `/newbot`, elige un nombre (ej: `Tolego MVP`) y un username que termine en `bot` (ej: `tolego_mvp_bot`)
   - BotFather te devuelve un token tipo `123456789:ABC-DEF...`
3. **API key de Gemini**
   - Entra a https://aistudio.google.com/apikey
   - Haz clic en **Create API key**
   - Copia la key

## Setup

Abre una terminal dentro de `mvp_bot/`:

```bash
cd mvp_bot
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

Luego copia el archivo de ejemplo y pon tus claves:

```bash
cp .env.example .env            # o simplemente duplica el archivo en Windows
```

Edita `.env` y reemplaza los valores:

```
TELEGRAM_BOT_TOKEN=123456789:ABC-DEF...
GEMINI_API_KEY=AIza...
```

## Correr el bot

Desde `mvp_bot/`:

```bash
python -m src.bot
```

La primera vez crea `tolego.db` y carga el catálogo automáticamente. Verás en consola:

```
Base de datos lista en ...\tolego.db
Bot Tolego iniciado. Esperando mensajes...
```

Ahora abre Telegram, busca tu bot por el username que le diste y envíale `/start`.

## Probar el flujo (guión para la demo)

1. `/start` — saludo
2. `/catalogo` — mostrar categorías
3. Click en **Marvel** → ver productos
4. Click en **Iron Man MK1** → ficha con precio y stock
5. Click en **🛒 Pedir 1 unidad** → confirmación del pedido
6. Mensaje libre: `¿tienes Naruto modo sabio?` → Gemini lo encuentra por nombre
7. Mensaje libre: `quiero 2 Goku` → Gemini detecta intent de pedido y cantidad
8. `/pedidos` → ver historial

## Estructura del proyecto

```
mvp_bot/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── catalogo.json       # catálogo semilla con 40+ productos
└── src/
    ├── __init__.py
    ├── bot.py              # entrypoint del bot
    ├── db.py               # SQLite: productos + pedidos
    ├── gemini_client.py    # interpretación con Gemini
    └── handlers.py         # comandos y mensajes libres
```

## Costos reales

- **Telegram Bot API**: gratis, sin límites relevantes
- **Gemini 1.5 Flash**: free tier de 15 requests/min y 1.500 requests/día (más que suficiente para la demo)
- **SQLite**: local, sin costo

Costo total para esta demo: **$0 USD**.

## Cómo se porta a producción

Este mismo código corre en Cloud Run o Cloud Functions con mínimos cambios:
- SQLite → Cloud SQL o Firestore
- Polling de Telegram → webhook público (Cloud Run endpoint)
- Para WhatsApp: se cambia el transport de `python-telegram-bot` por un cliente de WhatsApp Business Cloud API, manteniendo intactos `db.py`, `gemini_client.py` y la lógica de handlers.

## Troubleshooting

- **`Falta TELEGRAM_BOT_TOKEN`**: revisa que `.env` exista en la carpeta `mvp_bot/` (no en la raíz) y tenga el token.
- **Gemini devuelve 429**: el free tier tiene 15 req/min. Espera un minuto o sube a pay-as-you-go.
- **El bot no responde**: verifica que solo una instancia esté corriendo (dos instancias se roban los mensajes).
- **Error de permisos SQLite**: borra `tolego.db` y deja que se recree.
