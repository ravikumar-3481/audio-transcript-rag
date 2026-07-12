from utils.text_process import process_transcript
import shutil
import os


shutil.rmtree("data", ignore_errors=True)

def save_to_dir(transcript : str):
    TRANSCRIPT_DIR = "data/transcripts"
    try:
        os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
        transcript_path = os.path.join(TRANSCRIPT_DIR, "transcript.txt")
        with open(transcript_path, "w") as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_path}")
        return transcript_path
    except OSError as e:
        print(f"Failed to save transcript: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error saving transcript: {e}")
        raise

path = "https://youtu.be/KRhvlB1mOts?si=fSb6Oa2oE-KGPgkJ"
language = "hinglish" 

result = process_transcript(source=path, language=language)

dir = "data/transcripts"
os.makedirs(dir, exist_ok=True)
out_put = os.path.join(dir, "process.txt")
with open(out_put, "w", encoding="utf-8") as f:
    f.write(result)
print(f"Processed transcript saved...")
print(f"total letters {len(result)}")

