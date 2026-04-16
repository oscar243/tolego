"""Capa de datos SQLite para el MVP del bot Tolego."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "tolego.db"
CATALOGO_JSON = ROOT / "data" / "catalogo.json"


SCHEMA = """
CREATE TABLE IF NOT EXISTS productos (
    sku TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    telegram_username TEXT,
    sku TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    total INTEGER NOT NULL,
    estado TEXT NOT NULL DEFAULT 'nuevo',
    creado_en TEXT NOT NULL,
    FOREIGN KEY (sku) REFERENCES productos(sku)
);

CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_pedidos_user ON pedidos(telegram_user_id);
"""


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Crea las tablas si no existen y carga el catálogo si la base está vacía."""
    with _conn() as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    if count == 0:
        seed_from_json()


def seed_from_json() -> int:
    """Carga el catálogo desde data/catalogo.json. Devuelve cantidad de productos insertados."""
    productos = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
    with _conn() as conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO productos (sku, nombre, categoria, precio, stock, descripcion)
            VALUES (:sku, :nombre, :categoria, :precio, :stock, :descripcion)
            """,
            productos,
        )
    return len(productos)


def get_categorias() -> list[str]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT categoria FROM productos ORDER BY categoria"
        ).fetchall()
    return [r["categoria"] for r in rows]


def get_productos_por_categoria(categoria: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM productos WHERE categoria = ? ORDER BY nombre",
            (categoria,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_producto_por_sku(sku: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM productos WHERE sku = ?", (sku,)
        ).fetchone()
    return dict(row) if row else None


def buscar_productos(texto: str, limite: int = 5) -> list[dict]:
    """Búsqueda difusa por nombre, categoría o SKU (LIKE insensitive)."""
    patron = f"%{texto.strip()}%"
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM productos
            WHERE nombre LIKE ? COLLATE NOCASE
               OR categoria LIKE ? COLLATE NOCASE
               OR sku LIKE ? COLLATE NOCASE
               OR descripcion LIKE ? COLLATE NOCASE
            ORDER BY stock DESC
            LIMIT ?
            """,
            (patron, patron, patron, patron, limite),
        ).fetchall()
    return [dict(r) for r in rows]


def resumen_catalogo() -> list[dict]:
    """Vista compacta del catálogo para pasar a Gemini como contexto."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT sku, nombre, categoria, precio, stock FROM productos ORDER BY categoria, nombre"
        ).fetchall()
    return [dict(r) for r in rows]


def crear_pedido(
    telegram_user_id: int,
    telegram_username: str | None,
    sku: str,
    cantidad: int,
) -> dict | None:
    """Valida stock, descuenta inventario y registra el pedido. Devuelve el pedido o None si no hay stock."""
    if cantidad <= 0:
        return None
    with _conn() as conn:
        producto = conn.execute(
            "SELECT * FROM productos WHERE sku = ?", (sku,)
        ).fetchone()
        if producto is None or producto["stock"] < cantidad:
            return None

        total = producto["precio"] * cantidad
        creado_en = datetime.now().isoformat(timespec="seconds")

        cursor = conn.execute(
            """
            INSERT INTO pedidos (telegram_user_id, telegram_username, sku, cantidad, total, estado, creado_en)
            VALUES (?, ?, ?, ?, ?, 'nuevo', ?)
            """,
            (telegram_user_id, telegram_username, sku, cantidad, total, creado_en),
        )
        pedido_id = cursor.lastrowid

        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE sku = ?",
            (cantidad, sku),
        )

    return {
        "id": pedido_id,
        "sku": sku,
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "total": total,
        "creado_en": creado_en,
    }


def pedidos_del_usuario(telegram_user_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT p.id, p.sku, pr.nombre, p.cantidad, p.total, p.estado, p.creado_en
            FROM pedidos p
            JOIN productos pr ON p.sku = pr.sku
            WHERE p.telegram_user_id = ?
            ORDER BY p.id DESC
            LIMIT 10
            """,
            (telegram_user_id,),
        ).fetchall()
    return [dict(r) for r in rows]
