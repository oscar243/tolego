"""Cliente de Gemini para comprender mensajes del cliente y estructurarlos como JSON."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import google.generativeai as genai

from .db import resumen_catalogo


_MODEL: genai.GenerativeModel | None = None


def _get_model() -> genai.GenerativeModel:
    global _MODEL
    if _MODEL is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta GEMINI_API_KEY en el entorno")
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        _MODEL = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"},
        )
    return _MODEL


PROMPT_SISTEMA = """Eres el asistente conversacional de Tolego, un emprendimiento colombiano de minifiguras coleccionables tipo Lego. Tu tarea es interpretar el mensaje de un cliente y devolver SIEMPRE un JSON con esta estructura:

{{
  "intent": "saludo" | "ver_catalogo" | "consultar_producto" | "hacer_pedido" | "ayuda" | "fuera_alcance",
  "categoria": null o el nombre EXACTO de una categoría del catálogo si el cliente la menciona,
  "sku": null o el SKU EXACTO del producto si puedes identificarlo sin ambigüedad del catálogo,
  "cantidad": entero >=1 si el cliente mencionó cantidad, o null,
  "texto_respuesta": respuesta breve y cálida en español colombiano que el bot debería enviar al cliente
}}

Reglas importantes:
- Usa SOLAMENTE SKUs y categorías que existan en el catálogo que recibirás abajo.
- Si el cliente menciona un personaje con varias versiones (ej. "Iron Man"), no fijes sku y pide aclaración en texto_respuesta.
- Si el mensaje no tiene nada que ver con minifiguras o pedidos, usa intent "fuera_alcance".
- Mantén texto_respuesta corto (máximo 3 frases) y amable. No inventes productos ni precios.
- Si el cliente quiere ver el catálogo completo, intent = "ver_catalogo" y texto_respuesta sugiere ver las categorías.
- Si el cliente pregunta precio o disponibilidad de un producto, intent = "consultar_producto".
- Si el cliente quiere comprar un producto específico ya identificado, intent = "hacer_pedido".

CATÁLOGO DISPONIBLE (úsalo como única fuente de verdad):
{catalogo}
"""


def _catalogo_como_texto() -> str:
    productos = resumen_catalogo()
    lineas = [
        f"- {p['sku']} | {p['nombre']} | {p['categoria']} | ${p['precio']:,} COP | stock={p['stock']}"
        for p in productos
    ]
    return "\n".join(lineas)


def _parsear_json(texto: str) -> dict[str, Any]:
    """Intenta parsear JSON del modelo, con fallback a regex si viene con ruido."""
    texto = texto.strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", texto, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {
        "intent": "fuera_alcance",
        "categoria": None,
        "sku": None,
        "cantidad": None,
        "texto_respuesta": "No te entendí bien, ¿puedes reformularlo? También puedes escribir /catalogo.",
    }


def interpretar_mensaje(mensaje_usuario: str) -> dict[str, Any]:
    """Llama a Gemini con el catálogo como contexto y devuelve el JSON estructurado."""
    model = _get_model()
    prompt = PROMPT_SISTEMA.format(catalogo=_catalogo_como_texto())
    respuesta = model.generate_content(
        [
            {"role": "user", "parts": [prompt]},
            {"role": "user", "parts": [f"Mensaje del cliente: {mensaje_usuario}"]},
        ]
    )
    return _parsear_json(respuesta.text or "")
