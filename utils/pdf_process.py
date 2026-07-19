from pypdf import PdfReader
from pypdf.errors import PdfReadError
from models.summary_model import TranscriptSummarizer
from utils.tools import RecordMerger
import os


class PdfParser:

    def __init__(self):
        self.rm = RecordMerger()
        self.model = TranscriptSummarizer()

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes, password: str = None, max_pages: int = None) -> str:
        if not pdf_bytes or not isinstance(pdf_bytes, (bytes, bytearray)):
            print("No valid PDF bytes provided")
            return ""
    
        try:
            from io import BytesIO
            reader = PdfReader(BytesIO(pdf_bytes))
        except PdfReadError as e:
            print(f"Corrupt or unreadable PDF bytes: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error opening PDF from bytes: {e}")
            return ""
    
        if reader.is_encrypted:
            try:
                result = reader.decrypt(password or "")
                if result == 0:
                    print("PDF bytes are encrypted and could not be decrypted")
                    return ""
            except Exception as e:
                print(f"Failed to decrypt PDF bytes: {e}")
                return ""
    
        try:
            total_pages = len(reader.pages)
        except Exception as e:
            print(f"Could not determine page count: {e}")
            return ""
    
        if total_pages == 0:
            print("PDF bytes contain no pages")
            return ""
    
        page_limit = min(total_pages, max_pages) if max_pages else total_pages
        text_parts = []
        failed_pages = 0
    
        for i in range(page_limit):
            try:
                page_text = reader.pages[i].extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text)
            except Exception as e:
                failed_pages += 1
                print(f"Failed to extract text from page {i + 1}/{total_pages}: {e}")
                continue
    
        if failed_pages == page_limit:
            print(f"All {page_limit} pages failed extraction")
            return ""
    
        full_text = "\n\n".join(text_parts)
    
        if not full_text.strip():
            print("No extractable text found in PDF bytes (likely scanned/image-based)")
            return ""
    
        print(f"Extracted text from {page_limit - failed_pages}/{page_limit} pages")
        
        return full_text
    
    def summarize_pdf(self, full_text : str) :
        print("Summarizing PDF......")
        if not full_text:
            print("No text to summarize")
            return ""
        summary = self.model.get_pdf_summary(full_text)
        if not summary:
            print("No summary generated")
            return ""
        return summary
    

    