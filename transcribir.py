"""Transcribe las grabaciones de clase con AssemblyAI (modo económico: Nano, sin diarización)."""

import os
import sys
from pathlib import Path

import assemblyai as aai
from dotenv import load_dotenv

ROOT = Path(__file__).parent
GRABACIONES = ROOT / "grabaciones"
AUDIO = GRABACIONES / "audio"
SALIDA = GRABACIONES / "transcripciones"

load_dotenv(ROOT / ".env")
api_key = os.getenv("ASSEMBLY_API_KEY")
if not api_key:
    sys.exit("Falta ASSEMBLY_API_KEY en .env")

aai.settings.api_key = api_key

config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.nano,
    language_code="es",
    punctuate=True,
    format_text=True,
)

transcriber = aai.Transcriber(config=config)

SALIDA.mkdir(exist_ok=True)
audios = sorted(AUDIO.glob("*.mp3"))
if not audios:
    sys.exit(f"No se encontraron .mp3 en {AUDIO}/ (corre primero extraer_audio.py)")

print(f"Encontrados {len(audios)} audios. Salida: {SALIDA}\n")

for i, audio in enumerate(audios, 1):
    destino = SALIDA / f"{audio.stem}.txt"
    if destino.exists() and destino.stat().st_size > 0:
        print(f"[{i}/{len(audios)}] ya existe, saltando: {audio.name}")
        continue

    size_mb = audio.stat().st_size / 1024 / 1024
    print(f"[{i}/{len(audios)}] transcribiendo ({size_mb:.1f} MB): {audio.name}")

    try:
        transcript = transcriber.transcribe(str(audio))
    except Exception as e:
        print(f"  ERROR: {e}\n")
        continue

    if transcript.status == aai.TranscriptStatus.error:
        print(f"  ERROR de AssemblyAI: {transcript.error}\n")
        continue

    destino.write_text(transcript.text or "", encoding="utf-8")
    duracion = (transcript.audio_duration or 0) / 60
    print(f"  OK -> {destino.name} ({duracion:.1f} min de audio)\n")

print("Listo.")
