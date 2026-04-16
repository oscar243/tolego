"""Extrae audio de los .mp4 a .mp3 con nombres sin espacios (mucho más liviano para subir)."""

import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).parent
GRABACIONES = ROOT / "grabaciones"
SALIDA = GRABACIONES / "audio"

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def slugify(nombre: str) -> str:
    base = Path(nombre).stem
    base = re.sub(r"[^\w\-]+", "_", base, flags=re.UNICODE)
    base = re.sub(r"_+", "_", base).strip("_")
    return base


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    videos = sorted(GRABACIONES.glob("*.mp4"))
    if not videos:
        sys.exit("No se encontraron .mp4 en grabaciones/")

    print(f"Extrayendo audio de {len(videos)} archivos -> {SALIDA}\n")

    for i, video in enumerate(videos, 1):
        destino = SALIDA / f"{slugify(video.name)}.mp3"
        if destino.exists() and destino.stat().st_size > 0:
            print(f"[{i}/{len(videos)}] ya existe: {destino.name}")
            continue

        size_mb = video.stat().st_size / 1024 / 1024
        print(f"[{i}/{len(videos)}] {video.name} ({size_mb:.0f} MB) -> {destino.name}")

        cmd = [
            FFMPEG,
            "-y",
            "-i", str(video),
            "-vn",              # sin video
            "-ac", "1",         # mono
            "-ar", "16000",     # 16 kHz (suficiente para voz)
            "-b:a", "48k",      # bitrate bajo
            # quita todos los silencios > 1.5s por debajo de -35 dB
            "-af", "silenceremove=stop_periods=-1:stop_duration=1.5:stop_threshold=-35dB",
            str(destino),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERROR ffmpeg: {result.stderr[-300:]}\n")
            continue

        nuevo_mb = destino.stat().st_size / 1024 / 1024
        print(f"  OK ({nuevo_mb:.1f} MB)\n")

    print("Listo.")


if __name__ == "__main__":
    main()
