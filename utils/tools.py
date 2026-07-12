import os

def save_to_dir(transcript : str, DIRECTORY : str, filename : str) -> str :
    try:
        os.makedirs(DIRECTORY, exist_ok=True)
        transcript_path = os.path.join(DIRECTORY, filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_path}")
        return transcript_path
    except OSError as e:
        print(f"Failed to save transcript: {e}")
        raise