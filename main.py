from core.summary import summarize
from utils.tools import get_data, remove_a_dir



if __name__ == "__main__":
    path = "https://youtu.be/KRhvlB1mOts?si=fSb6Oa2oE-KGPgkJ"
    language = "hinglish"
    purpose = "notes"
    remove_a_dir("data")
    remove_a_dir("agent/memory/data")
    summary = summarize(source=path, language=language, purpose=purpose)
    print(f"\n\nProcessed transcript saved...\n\n")
    quick_summary, detailed_explanation, key_definitions, notes = get_data(purpose=purpose)