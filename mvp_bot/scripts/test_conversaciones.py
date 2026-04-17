"""Simulador de conversaciones: corre escenarios contra Gemini real.

Imita el comportamiento del handler.mensaje_libre (historial + ultimo_sku)
sin necesidad de Telegram. Imprime el JSON devuelto por Gemini en cada turno
y al final un checklist simple de aserciones por escenario.

Uso: python -m scripts.test_conversaciones
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from src import db  # noqa: E402
from src.gemini_client import interpretar_mensaje  # noqa: E402


@dataclass
class Estado:
    historial: list[dict[str, str]] = field(default_factory=list)
    ultimo_sku: str | None = None

    def registrar(self, role: str, text: str) -> None:
        self.historial.append({"role": role, "text": text})
        if len(self.historial) > 12:
            del self.historial[: len(self.historial) - 12]


@dataclass
class Turno:
    mensaje: str
    aserciones: list[Callable[[dict], bool]] = field(default_factory=list)
    descripcion: str = ""


@dataclass
class Escenario:
    nombre: str
    turnos: list[Turno]


def intent_es(esperado: str) -> Callable[[dict], bool]:
    f = lambda r: r.get("intent") == esperado
    f.__name__ = f"intent=={esperado}"  # type: ignore
    return f


def sku_es(esperado: str) -> Callable[[dict], bool]:
    f = lambda r: r.get("sku") == esperado
    f.__name__ = f"sku=={esperado}"  # type: ignore
    return f


def sku_no_null() -> Callable[[dict], bool]:
    f = lambda r: r.get("sku") is not None
    f.__name__ = "sku_no_null"  # type: ignore
    return f


def texto_menciona(sub: str) -> Callable[[dict], bool]:
    f = lambda r: sub.lower() in (r.get("texto_respuesta") or "").lower()
    f.__name__ = f"menciona({sub!r})"  # type: ignore
    return f


def texto_sin_sku() -> Callable[[dict], bool]:
    """El texto al cliente no debe contener códigos SKU (son internos)."""
    import re
    patron = re.compile(r"\b(?:M|SW|H|MO|SM|T|N|DB)-[A-Z]{1,3}\d{3}\b", re.IGNORECASE)
    f = lambda r: not patron.search(r.get("texto_respuesta") or "")
    f.__name__ = "texto_sin_sku"  # type: ignore
    return f


def categoria_es(esperada: str) -> Callable[[dict], bool]:
    f = lambda r: r.get("categoria") == esperada
    f.__name__ = f"categoria=={esperada}"  # type: ignore
    return f


ESCENARIOS = [
    Escenario(
        "1. Vegeta: consulta -> crítica de precio -> pide alternativa",
        [
            Turno("¿Tienes Vegeta?", [intent_es("consultar_producto"), sku_es("DB-DB007")],
                  "pide un producto específico"),
            Turno("¿Por qué tan caro?", [],
                  "crítica de precio sobre Vegeta (debería referirse a Vegeta/Dragon Ball)"),
            Turno("No me gusta, muéstrame algo más barato de Dragon Ball", [categoria_es("Dragon Ball")],
                  "pide alternativa en misma categoría"),
        ],
    ),
    Escenario(
        "2. Iron Man ambiguo -> aclaración -> pedido",
        [
            Turno("Quiero un Iron Man", [intent_es("consultar_producto"), texto_sin_sku()],
                  "nombre ambiguo, NO debe fijar SKU ni mencionar códigos al cliente"),
            Turno("El del guantelete del infinito", [sku_es("M-IM005"), texto_sin_sku()],
                  "aclara versión específica"),
            Turno("Perfecto, me llevo 2", [intent_es("hacer_pedido"), sku_es("M-IM005")],
                  "pedido con cantidad 2"),
        ],
    ),
    Escenario(
        "3. Harry Potter: saludo -> regalo -> Hermione",
        [
            Turno("Hola", [intent_es("saludo")],
                  "saludo simple"),
            Turno("Busco un regalo para un fan de Harry Potter", [categoria_es("Harry Potter")],
                  "consulta por categoría"),
            Turno("¿Cuánto cuesta Hermione?", [sku_es("H-HP002")],
                  "pregunta precio producto específico"),
        ],
    ),
    Escenario(
        "4. Naruto: ver catálogo -> Pain -> ese mismo",
        [
            Turno("Muéstrame los Naruto", [categoria_es("Naruto")],
                  "lista por categoría"),
            Turno("Tienen a Pain Camino Deva?", [sku_es("N-PA001")],
                  "producto específico"),
            Turno("Ese, lo quiero", [intent_es("hacer_pedido"), sku_es("N-PA001")],
                  "referencia anafórica 'ese'"),
        ],
    ),
    Escenario(
        "6. Flujo abierto: hola -> rara -> más rara -> starwars",
        [
            Turno("hola", [], "saludo inicial"),
            Turno("la más rara", [], "pregunta abierta tras la respuesta del bot"),
            Turno("quiero la figura más rara que tengas", [], "pide rareza explícita"),
            Turno("starwars", [categoria_es("Star Wars")], "debe cambiar a categoría Star Wars"),
        ],
    ),
    Escenario(
        "5. Fuera de alcance -> retoma",
        [
            Turno("¿Qué opinas del clima en Bogotá?", [intent_es("fuera_alcance")],
                  "mensaje sin relación con la tienda"),
            Turno("Okey, muéstrame Spider-Man Miles Morales", [sku_es("M-SM006"), texto_sin_sku()],
                  "vuelve al catálogo sin filtrar códigos internos"),
        ],
    ),
]


def correr_escenario(esc: Escenario) -> tuple[int, int]:
    estado = Estado()
    print(f"\n{'='*60}\n{esc.nombre}\n{'='*60}")
    total = 0
    pasan = 0
    for i, turno in enumerate(esc.turnos, 1):
        print(f"\n[{i}] USER: {turno.mensaje}")
        if turno.descripcion:
            print(f"    ({turno.descripcion})")
        try:
            resultado = interpretar_mensaje(
                turno.mensaje,
                historial=estado.historial,
                ultimo_sku=estado.ultimo_sku,
            )
        except Exception as e:
            print(f"    ERROR: {e}")
            total += len(turno.aserciones)
            continue
        print(f"    BOT  -> intent={resultado.get('intent')!r} sku={resultado.get('sku')!r} "
              f"categoria={resultado.get('categoria')!r} cant={resultado.get('cantidad')!r}")
        print(f"    TXT  -> {resultado.get('texto_respuesta')!r}")
        for aserc in turno.aserciones:
            total += 1
            ok = False
            try:
                ok = aserc(resultado)
            except Exception as e:
                print(f"      ✗ {aserc.__name__} (error: {e})")
                continue
            if ok:
                pasan += 1
                print(f"      ✓ {aserc.__name__}")
            else:
                print(f"      ✗ {aserc.__name__}")
        estado.registrar("user", turno.mensaje)
        if resultado.get("sku"):
            estado.ultimo_sku = resultado["sku"]
        # Simular lo que el handler guardaría como respuesta
        estado.registrar("model", resultado.get("texto_respuesta") or "")
    return pasan, total


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("Falta GEMINI_API_KEY en .env")
    db.init_db()
    total_pasan = 0
    total_aserc = 0
    for esc in ESCENARIOS:
        p, t = correr_escenario(esc)
        total_pasan += p
        total_aserc += t
    print(f"\n{'='*60}\nRESUMEN: {total_pasan}/{total_aserc} aserciones pasan ({100*total_pasan/max(total_aserc,1):.0f}%)")


if __name__ == "__main__":
    main()
