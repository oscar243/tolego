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
- NUNCA menciones códigos SKU (tipo M-IM001, SW-BF001, etc.) en texto_respuesta: son internos. Refiérete a los productos por su nombre.
- Si el cliente quiere ver el catálogo completo, intent = "ver_catalogo" y texto_respuesta sugiere ver las categorías.
- Si el cliente pregunta precio o disponibilidad de un producto, intent = "consultar_producto".
- Si el cliente quiere comprar un producto específico ya identificado, intent = "hacer_pedido".
- TIENES HISTORIAL de los últimos mensajes. Úsalo para mantener contexto: si el cliente acaba de ver un producto (ej. Vegeta) y luego pregunta "¿por qué tan caro?" o "no me gusta", refiérete a ese producto y mantén el SKU si aplica. Si pregunta por alternativas ("¿hay otro?", "muéstrame algo más barato"), sugiere productos de la misma categoría.

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


def interpretar_mensaje(
    mensaje_usuario: str,
    historial: list[dict[str, str]] | None = None,
    ultimo_sku: str | None = None,
) -> dict[str, Any]:
    """Llama a Gemini con el catálogo + historial y devuelve JSON estructurado.

    historial: lista de turnos previos [{"role": "user"|"model", "text": str}, ...].
    ultimo_sku: último SKU mostrado al cliente (para resolver referencias como "ese producto").
    """
    model = _get_model()
    prompt = PROMPT_SISTEMA.format(catalogo=_catalogo_como_texto())

    contenidos: list[dict[str, Any]] = [{"role": "user", "parts": [prompt]}]
    if ultimo_sku:
        contenidos.append(
            {
                "role": "user",
                "parts": [
                    f"[CONTEXTO] El último producto que el cliente vio fue el SKU {ultimo_sku}. "
                    "Si el mensaje actual parece referirse a ese producto (precio, crítica, alternativa), manténlo como referencia."
                ],
            }
        )
    for turno in historial or []:
        rol = "model" if turno.get("role") == "model" else "user"
        contenidos.append({"role": rol, "parts": [turno.get("text", "")]})
    contenidos.append({"role": "user", "parts": [f"Mensaje del cliente: {mensaje_usuario}"]})

    respuesta = model.generate_content(contenidos)
    return _parsear_json(respuesta.text or "")
