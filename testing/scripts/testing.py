from utils.text_process import clean_text
from utils.tools import save_to_dir, save_to_json, get_data
from core.summary import summarizer
import os, shutil


def clear_dir():
    password = str(input("Enter password to Delete Directory:  "))
    if password == "Ravi09":
        shutil.rmtree("data", ignore_errors=True)
        shutil.rmtree("testing/transcripts", ignore_errors=True)
        shutil.rmtree("testing/summary", ignore_errors=True)
        shutil.rmtree("testing/notes", ignore_errors=True)
    else:
        print("Incorrect Password")


def load_transcript_from_file() -> str:
    DIR ="data/transcripts"
    transcript_path = os.path.join(DIR, "transcript.txt")
    path = transcript_path 
    try:
        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read()
        if not transcript.strip():
            raise ValueError(f"Transcript file {path} is empty")
        return clean_text(transcript)
    except FileNotFoundError:
        print(f"Transcript file not found at {path}")
        raise
    except (OSError, ValueError) as e:
        print(f"Could not read transcript file {path}: {e}")
        raise


def summarize(purpose : str = "summarize"):
    transcript = load_transcript_from_file()
    if not transcript:
        raise ValueError("No transcript to summarize")
    
    try:
        summary, title = summarizer(transcript, purpose=purpose)
        
    except Exception as e:
        print(f"Failed to summarize transcript: {e}")
        raise
    
    if purpose == "notes":
        save_to_json(summary, purpose=purpose)
    else:
        save_to_json(summary, purpose=purpose)
    
    return summary, title

    
