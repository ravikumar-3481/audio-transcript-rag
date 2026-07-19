import os
import re
import json
import shutil


class FileSaver:
    def remove_a_dir(self, DIRECTORY : str = None):
        if not DIRECTORY:
            raise ValueError("No Directory Provided")
        if os.path.exists(DIRECTORY):
            shutil.rmtree(DIRECTORY)
            print(f"Directory {DIRECTORY} has been removed")
        else:
            print(f"Directory {DIRECTORY} does not exist")

    def save_to_dir(self, data : str, DIRECTORY : str, filename : str = "untitled.txt") -> str :
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


class JsonRepairer:
    def repair_json_snippet(self, raw: str) -> str:
        repaired = re.sub(r",\s*([}\]])", r"\1", raw)
        repaired = re.sub(r"^```(?:json)?\s*|\s*```$", "", repaired.strip())
        return repaired

    def parse_concatenated_json(self, raw_summary: str) -> list:
        if not raw_summary:
            return []

        decoder = json.JSONDecoder()
        idx = 0
        records = []
        text = raw_summary.strip()

        while idx < len(text):
            while idx < len(text) and text[idx] in " \t\n\r":
                idx += 1
            if idx >= len(text):
                break

            try:
                obj, end_idx = decoder.raw_decode(text, idx)
                records.append(obj)
                idx = end_idx
            except json.JSONDecodeError:
                next_start = text.find("{", idx + 1)
                if next_start == -1:
                    print(f"Could not recover from malformed JSON at position {idx}, stopping parse")
                    break
                print(f"Skipping malformed JSON object between position {idx} and {next_start}")
                idx = next_start

        if not records:
            raise ValueError("No valid JSON objects could be parsed from summary output")

        return records


class RecordMerger:
    def merge_notes_records_notes(self, records : list) -> dict:
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

    def merge_notes_records_summary(self, records : list) -> dict:
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

    def merge_pdf_analysis_records(self, records: list) -> dict:
        short_summaries = []
        detailed_summaries = []
        key_points = []
        important_facts = []
        additional_knowledge = []
        rag_ready_content = []
        document_types = []
        title = ""
    
        for record in records:
            if not isinstance(record, dict):
                continue
    
            doc_type = record.get("document_type", "")
            if doc_type:
                document_types.append(doc_type)
    
            if not title:
                title = record.get("title", "")
    
            short_summary = record.get("short_summary", "")
            if short_summary:
                short_summaries.append(short_summary)
    
            detailed_summary = record.get("detailed_summary", "")
            if detailed_summary:
                detailed_summaries.append(detailed_summary)
    
            chunk_key_points = record.get("key_points", [])
            if isinstance(chunk_key_points, list):
                key_points.extend(chunk_key_points)
    
            chunk_important_facts = record.get("important_facts", [])
            if isinstance(chunk_important_facts, list):
                important_facts.extend(chunk_important_facts)
    
            chunk_additional_knowledge = record.get("additional_knowledge", [])
            if isinstance(chunk_additional_knowledge, list):
                additional_knowledge.extend(chunk_additional_knowledge)
    
            chunk_rag_content = record.get("rag_ready_content", "")
            if chunk_rag_content:
                rag_ready_content.append(chunk_rag_content)
    
        final_type = max(set(document_types), key=document_types.count) if document_types else "other"
    
        return {
            "document_type": final_type,
            "title": title,
            "short_summary": "\n ".join(short_summaries),
            "detailed_summary": "\n ".join(detailed_summaries),
            "key_points": self.duplicate_preserve_order(key_points),
            "important_facts": self.duplicate_preserve_order(important_facts),
            "additional_knowledge": self.duplicate_preserve_order(additional_knowledge),
            "rag_ready_content": "\n\n".join(rag_ready_content),
        }
    
    def duplicate_preserve_order(self, items: list) -> list:
        seen = set()
        result = []
        for item in items:
            key = item.strip().lower() if isinstance(item, str) else item
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
        


class SummaryJsonStore:
    def __init__(self):
        self.repairer = JsonRepairer()
        self.merger = RecordMerger()

    def save_to_json(self, summary : str, DIRECTORY : str = "agent/memory/data", filename : str = "summary.json", purpose : str = "summarize" , type : str = None) -> str:
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
            records = self.repairer.parse_concatenated_json(raw_summary)
        except ValueError as e:
            print(f"Failed to parse summary output as JSON: {e}")
            raise

        if purpose == "notes":
            merged = self.merger.merge_notes_records_notes(records)
            filename = "notes.json"
        elif purpose == "pdf_notes":
            merged = self.merger.merge_pdf_analysis_records(records)
            filename = "pdf_analysis.json"
        else:
            merged = self.merger.merge_notes_records_summary(records)
            filename = "summary.json"


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

    def read_json_file(self, DIRECTORY : str = "agent/memory/data", filename : str = None):
        for filename in os.listdir(DIRECTORY):
            if filename.endswith(".json"):
                input_path = os.path.join(DIRECTORY, filename)

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file {input_path} not found")

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except (OSError, json.JSONDecodeError) as e:
            print(f"Failed to read input file {input_path}: {e}")
            raise

    def get_data(self, purpose: str = "summarize") -> str :
        data = self.read_json_file()
        if purpose == "notes" :
            quick_summary = data.get("quick_summary", "")
            detailed_explanation = data.get("detailed_explanation", "")
            key_definitions = {}
            chunk_definitions = data.get("key_definitions", [])
            if isinstance(chunk_definitions, list):
                for items in chunk_definitions:
                    key_definitions[(items["term"])] = (items["definition"])
            notes = data.get("notes", [])

            return quick_summary, detailed_explanation, key_definitions, notes

        else:
            short_summary = data.get("short_summary", "")
            detailed_summary = data.get("detailed_summary", "")
            important_notes = data.get("important_notes", [])
            remember_points = data.get("remember_points", [])
            important_points = data.get("important_points", [])

            return short_summary, detailed_summary, important_notes, remember_points, important_points
        
    def get_pdf_analysis_data(self) -> tuple:
        data = self.read_json_file(filename="pdf_analysis.json")
    
        document_type = data.get("document_type", "")
        title = data.get("title", "")
        short_summary = data.get("short_summary", "")
        detailed_summary = data.get("detailed_summary", "")
        key_points = data.get("key_points", [])
        important_facts = data.get("important_facts", [])
        additional_knowledge = data.get("additional_knowledge", [])
        rag_ready_content = data.get("rag_ready_content", "")
    
        return (
            document_type,
            title,
            short_summary,
            detailed_summary,
            key_points,
            important_facts,
            additional_knowledge,
            rag_ready_content,
        )


_file_saver = FileSaver()
_json_repairer = JsonRepairer()
_record_merger = RecordMerger()
_summary_store = SummaryJsonStore()


def remove_a_dir(DIRECTORY : str = None):
    return _file_saver.remove_a_dir(DIRECTORY)

def save_to_dir(data : str, DIRECTORY : str, filename : str = "untitled.txt") -> str :
    return _file_saver.save_to_dir(data, DIRECTORY, filename)

def save_to_json(summary : str, DIRECTORY : str = "agent/memory/data", filename : str = "summary.json", purpose : str = "summarize") -> str:
    return _summary_store.save_to_json(summary, DIRECTORY, filename, purpose)

def _repair_json_snippet(raw: str) -> str:
    return _json_repairer.repair_json_snippet(raw)

def parse_concatenated_json(raw_summary: str) -> list:
    return _json_repairer.parse_concatenated_json(raw_summary)

def merge_notes_records_notes(records : list) -> dict:
    return _record_merger.merge_notes_records_notes(records)

def merge_notes_records_summary(records : list) -> dict:
    return _record_merger.merge_notes_records_summary(records)

def merge_pdf_analysis_records(records : list) -> dict:
    return _record_merger.merge_pdf_analysis_records(records)

def read_json_file(DIRECTORY : str = "agent/memory/data"):
    return _summary_store.read_json_file(DIRECTORY)

def get_data(purpose: str = "summarize") -> str :
    return _summary_store.get_data(purpose)