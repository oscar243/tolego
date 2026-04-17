"""Entrypoint del bot de Telegram."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Importamos después de cargar el .env para que los módulos vean las variables.
from . import db, handlers  # noqa: E402


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
    )

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit("Falta TELEGRAM_BOT_TOKEN en .env")
    if not os.getenv("GEMINI_API_KEY"):
        sys.exit("Falta GEMINI_API_KEY en .env")

    db.init_db()
    logging.info("Base de datos lista en %s", db.DB_PATH)

    app = (
        ApplicationBuilder()
        .token(token)
        .connect_timeout(20)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(20)
        .build()
    )
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("catalogo", handlers.catalogo))
    app.add_handler(CommandHandler("pedidos", handlers.pedidos))
    app.add_handler(CallbackQueryHandler(handlers.callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.mensaje_libre))

    logging.info("Bot Tolego iniciado. Esperando mensajes...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
