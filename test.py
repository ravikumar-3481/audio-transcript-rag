from utils.text_process import process_transcript
import shutil
import os


shutil.rmtree("data", ignore_errors=True)



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
