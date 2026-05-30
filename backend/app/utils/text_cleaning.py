import re

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[.*?\]", "", text)  # remove noise like [music]
    return text.strip()