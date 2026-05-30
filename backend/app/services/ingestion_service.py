from app.ingestion.instagram import fetch_instagram_info
from app.ingestion.audio_extractor import extract_audio
from app.ingestion.whisper import transcribe_audio

def process_instagram(url: str):
    metadata = fetch_instagram_info(url)

    audio_path = extract_audio(url)

    transcript = transcribe_audio(audio_path)

    return {
        "metadata": metadata,
        "transcript": transcript
    }