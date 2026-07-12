import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPT_DIR = os.path.join(BASE_DIR, "data", "transcripts")
TRANSCRIPT_PATH = os.path.join(TRANSCRIPT_DIR, "transcript.txt")


def load_transcript(path: str | None = None) -> str:
    path = path or TRANSCRIPT_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Transcript file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        transcript = f.read()

    if not transcript.strip():
        raise ValueError(f"Transcript file {path} is empty")

    return transcript


def main() -> None:
    transcript = load_transcript()
    print(transcript)


if __name__ == "__main__":
    main()