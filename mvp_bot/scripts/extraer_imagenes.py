"""Extrae una imagen por SKU del Catalogo_ToleGo_2025.pdf.

Para cada página del catálogo:
1. Identifica los códigos 'CÓDIGO XX-XXX000' con su posición.
2. Detecta las imágenes embedidas de tamaño 'producto' para ubicar dónde
   está cada figura en la página.
3. Asigna cada imagen al SKU cuyo centro está más cerca, uno a uno.
4. Toma la imagen embedida completa (aplicando su smask si tiene alpha),
   la compone sobre fondo blanco y la escala a ~2x con Lanczos.
5. Guarda cada imagen como data/productos/{SKU}.jpeg.

Uso: python -m scripts.extraer_imagenes
"""

from __future__ import annotations

import io
import json
import re
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT.parent / "Catalogo_ToleGo_2025.pdf"
OUT_DIR = ROOT / "data" / "productos"
CATALOGO_JSON = ROOT / "data" / "catalogo.json"

SKU_RE = re.compile(r"CÓDIGO([A-Z]{1,3}-[A-Z]{1,3}\d{3})")

TARGET_WIDTH = 600     # ancho final deseado en píxeles (upscale con Lanczos)
PADDING_PX = 20        # margen blanco alrededor de la figura


def find_skus(page: fitz.Page) -> list[tuple[float, float, str]]:
    """Devuelve (cx, cy, sku) leyendo líneas del dict del PDF."""
    out: list[tuple[float, float, str]] = []
    d = page.get_text("dict")
    for block in d.get("blocks", []):
        for line in block.get("lines", []):
            text = "".join(s["text"] for s in line["spans"])
            compact = re.sub(r"\s+", "", text)
            m = SKU_RE.search(compact)
            if m:
                bbox = line["bbox"]
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2
                out.append((cx, cy, m.group(1)))
    return out


def get_product_images(doc: fitz.Document, page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
    """Devuelve (bbox, xref) de las imágenes tamaño producto."""
    result: list[tuple[fitz.Rect, int]] = []
    seen_xrefs: set[int] = set()
    for img in page.get_images(full=True):
        xref = img[0]
        if xref in seen_xrefs:
            continue
        info = doc.extract_image(xref)
        if info["width"] < 150 or info["height"] < 150:
            continue
        for r in page.get_image_rects(xref):
            if r.width < 60 or r.height < 80:
                continue
            result.append((r, xref))
        seen_xrefs.add(xref)
    return result


def assign_images_to_skus(
    skus: list[tuple[float, float, str]],
    imgs: list[tuple[fitz.Rect, int]],
) -> dict[str, int]:
    """Asignación greedy uno-a-uno por distancia mínima entre centros."""
    pairs = []
    for i, (r, xref) in enumerate(imgs):
        icx, icy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        for j, (sx, sy, sku) in enumerate(skus):
            d2 = (icx - sx) ** 2 + (icy - sy) ** 2
            pairs.append((d2, i, j, sku, xref))
    pairs.sort()
    used_imgs: set[int] = set()
    used_skus: set[int] = set()
    out: dict[str, int] = {}
    for _, i, j, sku, xref in pairs:
        if i in used_imgs or j in used_skus or sku in out:
            continue
        out[sku] = xref
        used_imgs.add(i)
        used_skus.add(j)
    return out


def render_sku_image(doc: fitz.Document, xref: int) -> bytes:
    """Toma la imagen embedida (con smask si tiene), la compone sobre blanco,
    recorta al contenido no-blanco, agrega padding uniforme y escala a TARGET_WIDTH."""
    info = doc.extract_image(xref)
    smask = info.get("smask", 0)
    base = Image.open(io.BytesIO(info["image"])).convert("RGB")
    if smask:
        mask_info = doc.extract_image(smask)
        mask = Image.open(io.BytesIO(mask_info["image"])).convert("L")
        if mask.size != base.size:
            mask = mask.resize(base.size, Image.LANCZOS)
        bg = Image.new("RGB", base.size, (255, 255, 255))
        bg.paste(base, mask=mask)
    else:
        bg = base

    bbox = _content_bbox(bg)
    if bbox:
        bg = bg.crop(bbox)

    padded = Image.new("RGB", (bg.width + 2 * PADDING_PX, bg.height + 2 * PADDING_PX), (255, 255, 255))
    padded.paste(bg, (PADDING_PX, PADDING_PX))

    if padded.width < TARGET_WIDTH:
        ratio = TARGET_WIDTH / padded.width
        new_size = (TARGET_WIDTH, round(padded.height * ratio))
        padded = padded.resize(new_size, Image.LANCZOS)

    out = io.BytesIO()
    padded.save(out, format="JPEG", quality=92, optimize=True)
    return out.getvalue()


def _content_bbox(im: Image.Image, threshold: int = 245) -> tuple[int, int, int, int] | None:
    """Bbox de píxeles no-blancos (útil para recortar márgenes transparentes convertidos)."""
    gray = im.convert("L")
    # invertir: contenido oscuro pasa a claro
    import numpy as np
    arr = np.array(gray)
    mask = arr < threshold
    if not mask.any():
        return None
    ys, xs = np.where(mask)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def main() -> None:
    if not PDF_PATH.exists():
        raise SystemExit(f"No existe {PDF_PATH}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CATALOGO_JSON, encoding="utf-8") as f:
        catalogo = json.load(f)
    skus_catalogo = {p["sku"] for p in catalogo}

    # Remapeos para SKUs colisionados en el PDF real:
    # clave = (pagina_0indexada, sku_en_pdf) -> sku_en_catalogo
    REMAPEOS_POR_PAGINA: dict[tuple[int, str], str] = {
        (9, "M-GR001"): "SW-GR001",   # Grogu en página Star Wars
        (5, "M-SW001"): "M-WZ001",    # Wanda Maximoff Zombie en página zombies
    }

    doc = fitz.open(PDF_PATH)
    asignaciones: dict[str, bytes] = {}
    total_pages_processed = 0

    for pnum in range(len(doc)):
        page = doc[pnum]
        skus = find_skus(page)
        if not skus:
            continue
        imgs = get_product_images(doc, page)
        if not imgs:
            print(f"p{pnum+1}: {len(skus)} SKUs pero 0 imágenes")
            continue
        mapping = assign_images_to_skus(skus, imgs)
        total_pages_processed += 1
        print(f"p{pnum+1}: {len(skus)} SKUs, {len(imgs)} imgs, {len(mapping)} asignadas")
        for sku, xref in mapping.items():
            sku_final = REMAPEOS_POR_PAGINA.get((pnum, sku), sku)
            asignaciones[sku_final] = render_sku_image(doc, xref)

    print(f"\n{total_pages_processed} páginas procesadas, {len(asignaciones)} SKUs con imagen.")

    # Escribir archivos
    for sku, data in asignaciones.items():
        out_path = OUT_DIR / f"{sku}.jpeg"
        out_path.write_bytes(data)

    no_image = skus_catalogo - set(asignaciones.keys())
    sin_match = set(asignaciones.keys()) - skus_catalogo

    print(f"\nSKUs del catálogo sin imagen: {len(no_image)}")
    for s in sorted(no_image):
        print(f"  - {s}")
    if sin_match:
        print(f"\nImágenes extraídas que no están en el catálogo: {len(sin_match)}")
        for s in sorted(sin_match):
            print(f"  - {s}")


if __name__ == "__main__":
    main()
