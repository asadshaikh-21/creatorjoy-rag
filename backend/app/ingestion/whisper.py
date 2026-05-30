# app/ingestion/whisper.py

from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(audio_path: str) -> str:
    segments, info = model.transcribe(audio_path)

    transcript = " ".join(
        segment.text.strip()
        for segment in segments
    )

    return transcript