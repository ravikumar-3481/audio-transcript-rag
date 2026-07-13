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



def save_to_dir(data : str, DIRECTORY : str, filename : str = "untitled.txt") -> str :
    try:
        os.makedirs(DIRECTORY, exist_ok=True)
        transcript_path = os.path.join(DIRECTORY, filename)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(data)
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


def merge_notes_records_notes(records : list) -> dict:
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

def merge_notes_records_summary(records : list) -> dict:
    short_summaries = []
    detailed_summaries = []
    remember_points = []
    important_points = []
    important_notes = []

    for record in records:
        if not isinstance(record, dict):
            continue

        short_summary = record.get("short_summary", "")
        if short_summary:
            short_summaries.append(short_summary)

        detailed_explanation = record.get("detailed_summary", "")
        if detailed_explanation:
            detailed_summaries.append(detailed_explanation)

        chunk_remember_points = record.get("remember_points", [])
        if isinstance(chunk_remember_points, list):
            remember_points.extend(chunk_remember_points)

        chunk_important_points = record.get("important_points", [])
        if isinstance(chunk_important_points, list):
            important_points.extend(chunk_important_points)

        chunk_important_notes = record.get("important_notes", [])
        if isinstance(chunk_important_notes, list):
            important_notes.extend(chunk_important_notes)

    return {
        "short_summary": "\n ".join(short_summaries),
        "detailed_summary": "\n ".join(detailed_summaries),
        "remember_points": remember_points,
        "important_points": important_points,
        "important_notes": important_notes,
    }


def save_to_json(summary : str, DIRECTORY : str = "agent/memory/data", filename : str = "summary.json", purpose : str = "summarize") -> str:

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

    if purpose == "notes":
        merged = merge_notes_records_notes(records)
        filename = "notes.json"
    else:
        merged = merge_notes_records_summary(records)

    try:
        os.makedirs(DIRECTORY, exist_ok=True)
        output_path = os.path.join(DIRECTORY, filename)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Failed to save summary json to {output_path}: {e}")
        raise

    print(f"Summary saved to {output_path}")
    return output_path 