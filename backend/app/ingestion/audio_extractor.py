import os
import uuid
import subprocess

def extract_audio(url: str, output_dir="temp"):
    os.makedirs(output_dir, exist_ok=True)

    audio_path = os.path.join(output_dir, f"{uuid.uuid4()}.mp3")

    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", audio_path,
        url
    ]

    subprocess.run(command, check=True)

    return audio_path