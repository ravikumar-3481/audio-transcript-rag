from utils.text_process import process_transcript
import shutil



if __name__ == "__main__":
    shutil.rmtree("data", ignore_errors=True)
    shutil.rmtree("testing/transcripts", ignore_errors=True)
    path = "https://youtu.be/KRhvlB1mOts?si=fSb6Oa2oE-KGPgkJ"
    language = "hinglish"
    result = process_transcript(source=path, language=language)
    print(f"Processed transcript saved...")
    print(f"total letters {len(result)}")

