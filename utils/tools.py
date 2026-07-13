import os
import json
import shutil


def clear_dir():
    password = str(input("Enter password to Delete Directory:  "))
    if password == "Ravi09":
        shutil.rmtree("data", ignore_errors=True)
        shutil.rmtree("testing/transcripts", ignore_errors=True)
        shutil.rmtree("testing/summary", ignore_errors=True)
        shutil.rmtree("testing/notes", ignore_errors=True)
    else:
        print("Incorrect Password")

def remove_a_dir(DIRECTORY : str = None):
    if not DIRECTORY:
        raise ValueError("No Directory Provided")
    if os.path.exists(DIRECTORY):
        shutil.rmtree(DIRECTORY)
        print(f"Directory {DIRECTORY} has been removed")
    else:
        print(f"Directory {DIRECTORY} does not exist")



def save_to_dir(transcript : str, DIRECTORY : str = "agent/memory/data", filename : str = "untitled.txt") -> str :
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


def parse_concatenated_json(raw : str) -> list:
    if not raw or not raw.strip():
        raise ValueError("Empty summary output, nothing to parse")

    decoder = json.JSONDecoder()
    records = []
    idx = 0
    length = len(raw)

    while idx < length:
        while idx < length and raw[idx].isspace():
            idx += 1
        if idx >= length:
            break
        try:
            obj, end_idx = decoder.raw_decode(raw, idx)
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON in summary output at position {idx}: {e}") from e
        records.append(obj)
        idx = end_idx

    if not records:
        raise ValueError("No valid JSON objects found in summary output")

    return records


def merge_notes_records(records : list) -> dict:
    quick_summaries = []
    detailed_explanations = []
    key_definitions = []
    notes = []

    for record in records:
        if not isinstance(record, dict):
            continue

        quick_summary = record.get("quick_summary", "")
        if quick_summary:
            quick_summaries.append(quick_summary)

        detailed_explanation = record.get("detailed_explanation", "")
        if detailed_explanation:
            detailed_explanations.append(detailed_explanation)

        chunk_definitions = record.get("key_definitions", [])
        if isinstance(chunk_definitions, list):
            key_definitions.extend(chunk_definitions)

        chunk_notes = record.get("notes", [])
        if isinstance(chunk_notes, list):
            notes.extend(chunk_notes)

    return {
        "quick_summary": "\n ".join(quick_summaries),
        "detailed_explanation": "\n ".join(detailed_explanations),
        "key_definitions": key_definitions,
        "notes": notes,
    }


def save_to_json(summary : str, DIRECTORY : str = "agent/memory/data", filename : str = "untitled.json") -> str:
    os.makedirs(DIRECTORY, exist_ok=True)
    output_path = os.path.join(DIRECTORY, filename)


    if not summary:
        raise ValueError("No transcript provided, nothing to summarize")

    try:
        raw_summary = summary 
    except (ModuleNotFoundError, RuntimeError, TypeError, ValueError) as e:
        print(f"Failed to generate summary: {e}")
        raise

    if not raw_summary:
        raise ValueError("No summary generated, nothing to save")

    try:
        records = parse_concatenated_json(raw_summary)
    except ValueError as e:
        print(f"Failed to parse summary output as JSON: {e}")
        raise

    merged = merge_notes_records(records)

    try:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Failed to save summary json to {output_path}: {e}")
        raise

    print(f"Summary saved to {output_path}")
    return output_path