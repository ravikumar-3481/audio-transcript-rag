import os
from core.transcriber import transcribe
import shutil
import re

TRANSCRIPT_DIR = "data/transcripts"



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
    


def load_transcript_from_file(transcript_path : str = None) -> str:
    path = transcript_path or os.path.join(TRANSCRIPT_DIR, "transcript.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read()
        if not transcript.strip():
            raise ValueError(f"Transcript file {path} is empty")
        return transcript
    except FileNotFoundError:
        print(f"Transcript file not found at {path}")
        raise
    except (OSError, ValueError) as e:
        print(f"Could not read transcript file {path}: {e}")
        raise


def get_transcript(transcript_path : str = None, source : str = None, language : str = "english", use_file : bool = True) -> str:
    if use_file:
        try:
            return load_transcript_from_file(transcript_path)
        except Exception as e:
            print(f"Falling back to live transcription due to: {e}")
 
    if not source:
        raise ValueError("No transcript file available and no source provided for transcription")
 
    try:
        transcript = transcribe(source, language=language)
        return transcript
    except Exception as e:
        print(f"Failed to generate transcript from source {source}: {e}")
        raise








def process_transcript(transcript_path : str = None, source : str = None, language : str = "english", use_file : bool = True) -> str:
    try:
        raw_transcript = get_transcript(transcript_path=transcript_path, source=source, language=language, use_file=use_file)
    except Exception as e:
        print(f"Could not obtain a transcript: {e}")
        raise

    cleaned = clean_text(raw_transcript)

    if not cleaned or not cleaned.strip():
        raise ValueError("Cleaned transcript is empty, nothing to process")

    print(f"Transcript processed successfully ({len(cleaned)} characters)")

    return cleaned

