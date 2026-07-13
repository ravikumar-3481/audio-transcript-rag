from core.transcriber import transcribe
from utils.tools import save_to_dir
import re


def clean_text(text : str) -> str:
    try:
        cleaned = remove_punctuation_symbols(text)
        cleaned = re.sub(r"\[.*?\]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.strip()
        return cleaned if cleaned else text
    except Exception as e:
        print(f"Text cleaning failed, using raw text: {e}")
        return text


def remove_punctuation_symbols(text : str) -> str:
    try:
        if not text:
            return ""
        cleaned = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
        cleaned = re.sub(r"_", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned if cleaned else text
    except Exception as e:
        print(f"Punctuation removal failed, using raw text: {e}")
        return text
    

def get_transcript(source : str , language : str = "english") -> str:
    if not source:
        raise ValueError("No Source Has Provided. Try Again...")
 
    try:
        transcript = transcribe(source, language=language)
        return transcript
    except Exception as e:
        print(f"Failed to generate transcript from source {source}: {e}")
        raise


def process_transcript(source : str = None, language : str = "english") -> str:
    try:
        raw_transcript = get_transcript(source=source, language=language)
    except Exception as e:
        print(f"Could not obtain a transcript: {e}")
        raise

    cleaned = clean_text(raw_transcript)

    if not cleaned or not cleaned.strip():
        raise ValueError("Cleaned transcript is empty, nothing to process")

    print(f"Transcript processed successfully ({len(cleaned)} characters)")
    save_to_dir(cleaned, DIRECTORY = "data/transcripts", filename = "processed_text.txt")
    return cleaned

