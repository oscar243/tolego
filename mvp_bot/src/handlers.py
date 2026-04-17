"""Handlers del bot de Telegram: comandos y mensajes libres."""

from __future__ import annotations

import logging
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from . import db
from .gemini_client import interpretar_mensaje

log = logging.getLogger(__name__)

PRODUCTOS_DIR = Path(__file__).resolve().parent.parent / "data" / "productos"


def _imagen_producto(sku: str) -> Path | None:
    for ext in ("jpeg", "jpg", "png"):
        p = PRODUCTOS_DIR / f"{sku}.{ext}"
        if p.exists():
            return p
    return None

MENSAJE_BIENVENIDA = (
    "👋 ¡Hola! Soy el asistente de *Tolego*, tu tienda de minifiguras coleccionables.\n\n"
    "Puedes escribirme como si hablaras con una persona, por ejemplo:\n"
    "• _\"¿Tienes Iron Man?\"_\n"
    "• _\"Quiero pedir 2 Naruto\"_\n"
    "• _\"¿Cuánto cuesta el diorama de Star Wars?\"_\n\n"
    "También puedes usar /catalogo para ver las categorías o /pedidos para ver tu historial."
)


def _moneda(valor: int) -> str:
    return f"${valor:,.0f} COP".replace(",", ".")


def _teclado_categorias() -> InlineKeyboardMarkup:
    botones = [
        [InlineKeyboardButton(cat, callback_data=f"cat:{cat}")]
        for cat in db.get_categorias()
    ]
    return InlineKeyboardMarkup(botones)


def _teclado_productos(productos: list[dict]) -> InlineKeyboardMarkup:
    botones = [
        [InlineKeyboardButton(f"{p['nombre']} — {_moneda(p['precio'])}", callback_data=f"prod:{p['sku']}")]
        for p in productos
    ]
    botones.append([InlineKeyboardButton("⬅️ Volver a categorías", callback_data="menu:categorias")])
    return InlineKeyboardMarkup(botones)


def _teclado_producto(sku: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛒 Pedir 1 unidad", callback_data=f"pedir:{sku}:1")],
            [InlineKeyboardButton("🛒 Pedir 2 unidades", callback_data=f"pedir:{sku}:2")],
            [InlineKeyboardButton("⬅️ Volver a categorías", callback_data="menu:categorias")],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(MENSAJE_BIENVENIDA, parse_mode="Markdown")


async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📦 *Categorías disponibles:*", parse_mode="Markdown", reply_markup=_teclado_categorias()
    )


async def pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lista = db.pedidos_del_usuario(update.effective_user.id)
    if not lista:
        await update.message.reply_text(
            "Aún no tienes pedidos registrados. Escribe /catalogo para explorar."
        )
        return
    lineas = ["🧾 *Tus pedidos recientes:*"]
    for p in lista:
        lineas.append(
            f"• #{p['id']} — {p['cantidad']}× {p['nombre']} — {_moneda(p['total'])} ({p['estado']}) — {p['creado_en']}"
        )
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")


MAX_HISTORIAL = 12  # turnos (user+model combinados) que le pasamos a Gemini

_STOPWORDS = {
    "quiero", "dame", "muestrame", "muéstrame", "tienes", "hay", "busco", "pedir",
    "un", "una", "unos", "unas", "el", "la", "los", "las", "de", "del", "y", "o",
    "por", "favor", "me", "con", "sin", "para", "es", "ese", "esa", "eso",
}


def _filtrar_por_mensaje(productos: list[dict], mensaje: str) -> list[dict]:
    """Filtra la lista a los productos cuyo nombre contiene alguna palabra del mensaje
    (excluyendo stopwords y palabras cortas)."""
    import re
    palabras = {
        w for w in re.findall(r"[\wáéíóúñ]+", mensaje.lower())
        if len(w) >= 3 and w not in _STOPWORDS
    }
    if not palabras:
        return productos
    return [
        p for p in productos
        if any(w in p["nombre"].lower() for w in palabras)
    ]


def _registrar_turno(context: ContextTypes.DEFAULT_TYPE, role: str, text: str) -> None:
    historial = context.user_data.setdefault("historial", [])
    historial.append({"role": role, "text": text})
    if len(historial) > MAX_HISTORIAL:
        del historial[: len(historial) - MAX_HISTORIAL]


async def mensaje_libre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pipeline: mensaje -> Gemini (con historial) -> lógica de base -> respuesta."""
    texto = update.message.text or ""
    try:
        await update.message.chat.send_action("typing")
    except Exception:
        log.debug("send_action falló, se ignora", exc_info=True)

    historial = context.user_data.get("historial", [])
    ultimo_sku = context.user_data.get("ultimo_sku")

    try:
        resultado = interpretar_mensaje(texto, historial=historial, ultimo_sku=ultimo_sku)
    except Exception:
        log.exception("Fallo llamando a Gemini")
        await update.message.reply_text(
            "Tuve un problema entendiendo el mensaje. ¿Puedes intentar de nuevo?"
        )
        return

    intent = resultado.get("intent")
    respuesta = resultado.get("texto_respuesta") or ""
    sku = resultado.get("sku")
    categoria = resultado.get("categoria")
    cantidad = resultado.get("cantidad") or 1

    _registrar_turno(context, "user", texto)

    if intent == "ver_catalogo":
        if categoria:
            productos = db.get_productos_por_categoria(categoria)
            if productos:
                await update.message.reply_text(
                    respuesta or f"Estos son los productos en *{categoria}*:",
                    parse_mode="Markdown",
                    reply_markup=_teclado_productos(productos),
                )
                _registrar_turno(context, "model", f"Mostré productos de categoría {categoria}.")
                return
        await update.message.reply_text(
            respuesta or "Estas son nuestras categorías:", reply_markup=_teclado_categorias()
        )
        _registrar_turno(context, "model", respuesta or "Categorías disponibles.")
        return

    if intent == "consultar_producto" and sku:
        producto = db.get_producto_por_sku(sku)
        if producto:
            await _enviar_ficha_con_foto(update, producto, sku)
            context.user_data["ultimo_sku"] = sku
            _registrar_turno(context, "model", f"Mostré ficha de {producto['nombre']} (SKU {sku}).")
            return

    if intent == "consultar_producto" and categoria:
        productos = db.get_productos_por_categoria(categoria)
        if productos:
            filtrados = _filtrar_por_mensaje(productos, texto)
            if 0 < len(filtrados) < len(productos):
                await update.message.reply_text(
                    f"Encontré estas opciones en *{categoria}*:",
                    parse_mode="Markdown",
                    reply_markup=_teclado_productos(filtrados),
                )
                _registrar_turno(context, "model", f"Mostré {len(filtrados)} productos filtrados de {categoria}.")
                return
            await update.message.reply_text(
                f"Estos son los productos en *{categoria}*:",
                parse_mode="Markdown",
                reply_markup=_teclado_productos(productos),
            )
            _registrar_turno(context, "model", f"Mostré productos de categoría {categoria}.")
            return

    if intent == "consultar_producto":
        coincidencias = db.buscar_productos(texto)
        if coincidencias:
            await update.message.reply_text(
                "Encontré estas opciones que pueden servirte:",
                reply_markup=_teclado_productos(coincidencias),
            )
            _registrar_turno(context, "model", "Mostré resultados de búsqueda.")
            return

    if intent == "hacer_pedido" and sku:
        await _registrar_pedido(update, sku, cantidad)
        _registrar_turno(context, "model", f"Registré pedido de SKU {sku}.")
        return

    texto_salida = respuesta or "No estoy seguro de haberte entendido. Escribe /catalogo para ver productos."
    await update.message.reply_text(texto_salida)
    _registrar_turno(context, "model", texto_salida)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""

    if data == "menu:categorias":
        await query.edit_message_text(
            "📦 *Categorías disponibles:*", parse_mode="Markdown", reply_markup=_teclado_categorias()
        )
        return

    if data.startswith("cat:"):
        categoria = data.split(":", 1)[1]
        productos = db.get_productos_por_categoria(categoria)
        if not productos:
            await query.edit_message_text(f"No hay productos en {categoria} por ahora.")
            return
        await query.edit_message_text(
            f"*{categoria}* — elige un producto:",
            parse_mode="Markdown",
            reply_markup=_teclado_productos(productos),
        )
        return

    if data.startswith("prod:"):
        sku = data.split(":", 1)[1]
        producto = db.get_producto_por_sku(sku)
        if not producto:
            await query.edit_message_text("Ese producto ya no está disponible.")
            return
        img = _imagen_producto(sku)
        if img:
            with img.open("rb") as f:
                await query.message.reply_photo(
                    photo=f,
                    caption=_ficha_producto(producto),
                    parse_mode="Markdown",
                    reply_markup=_teclado_producto(sku),
                )
        else:
            await query.message.reply_text(
                _ficha_producto(producto),
                parse_mode="Markdown",
                reply_markup=_teclado_producto(sku),
            )
        context.user_data["ultimo_sku"] = sku
        _registrar_turno(context, "model", f"Mostré ficha de {producto['nombre']} (SKU {sku}).")
        return

    if data.startswith("pedir:"):
        _, sku, cantidad_str = data.split(":", 2)
        cantidad = int(cantidad_str)
        producto = db.get_producto_por_sku(sku)
        if not producto:
            await query.message.reply_text("Ese producto ya no está disponible.")
            return
        user = update.effective_user
        pedido = db.crear_pedido(user.id, user.username, sku, cantidad)
        if pedido is None:
            await query.message.reply_text(
                f"😕 No hay stock suficiente de {producto['nombre']} ({producto['stock']} disponibles)."
            )
            return
        await query.message.reply_text(
            _confirmacion_pedido(pedido), parse_mode="Markdown"
        )
        return


async def _enviar_ficha_con_foto(update: Update, producto: dict, sku: str) -> None:
    img = _imagen_producto(sku)
    if img:
        with img.open("rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=_ficha_producto(producto),
                parse_mode="Markdown",
                reply_markup=_teclado_producto(sku),
            )
    else:
        await update.message.reply_text(
            _ficha_producto(producto),
            parse_mode="Markdown",
            reply_markup=_teclado_producto(sku),
        )


async def _registrar_pedido(update: Update, sku: str, cantidad: int) -> None:
    producto = db.get_producto_por_sku(sku)
    if not producto:
        await update.message.reply_text("No encontré ese producto en el catálogo.")
        return
    user = update.effective_user
    pedido = db.crear_pedido(user.id, user.username, sku, cantidad)
    if pedido is None:
        await update.message.reply_text(
            f"😕 Solo tengo {producto['stock']} unidades de {producto['nombre']} disponibles."
        )
        return
    await update.message.reply_text(_confirmacion_pedido(pedido), parse_mode="Markdown")


def _ficha_producto(producto: dict) -> str:
    disponibilidad = "✅ Disponible" if producto["stock"] > 0 else "❌ Agotado"
    descripcion = producto.get("descripcion") or ""
    return (
        f"*{producto['nombre']}*\n"
        f"_{producto['categoria']} — SKU {producto['sku']}_\n\n"
        f"{descripcion}\n\n"
        f"💰 Precio: *{_moneda(producto['precio'])}*\n"
        f"📦 Stock: *{producto['stock']}*\n"
        f"{disponibilidad}"
    )


def _confirmacion_pedido(pedido: dict) -> str:
    return (
        "✅ *Pedido registrado*\n\n"
        f"Pedido #{pedido['id']}\n"
        f"{pedido['cantidad']}× {pedido['nombre']}\n"
        f"Total: *{_moneda(pedido['total'])}*\n\n"
        "Pronto te contactaremos para coordinar pago y envío. Gracias por comprar en Tolego."
    )
