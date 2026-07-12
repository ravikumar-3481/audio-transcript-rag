from utils.text_process import clean_text
from utils.tools import save_to_dir
import os

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




text = load_transcript_from_file()
save_to_dir(text, DIRECTORY = "testing/transcripts", filename = "process(testing).txt")
