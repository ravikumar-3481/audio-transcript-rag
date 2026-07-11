from core.transcriber import transcribe
import shutil

def clear_dir():
    shutil.rmtree("data", ignore_errors=True)

if __name__ == "__main__":
    clear_dir()
    print('Old Directory Removed Successfully...')
    path = "https://youtu.be/KRhvlB1mOts?si=XfAA5d24iuWV_yD6"
    language = "hinglish"
    transcribe(path, language=language)