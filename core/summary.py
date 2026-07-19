from utils.text_process import GetTranscript
from utils.tools import SummaryJsonStore
from models.summary_model import TranscriptSummarizer


Ts = TranscriptSummarizer()
fs = SummaryJsonStore()
gt = GetTranscript()





def summarizer(transcript : str, purpose : str = "summarize") -> str:
    if not transcript:
        print("No transcript to summarize")
        return ""
    
    try:
        if purpose == "notes":
            print("Generating notes....")
        else:
            print("Summarizing transcript...")
             
        summary = Ts.get_summary(transcript, purpose=purpose)
        if not summary:
            raise ValueError("No summary to generate title from")
        print("Generating title...")
        title = Ts.get_title(summary)
        print(f"Title: {title}\n")
        if not title:
            raise ValueError("No title to generate")
        return summary, title
    

    except (ModuleNotFoundError, RuntimeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Failed to summarize transcript: {e}") from e
    
def summarize(source : str, language : str = "english", purpose : str = "summarize"):
    transcript = gt.get_transcript(source , language=language)
    if not transcript:
        raise ValueError("No transcript to summarize")
    
    try:
        summary, title = summarizer(transcript, purpose=purpose)
        
    except Exception as e:
        print(f"Failed to summarize transcript: {e}")
        raise
    
    if purpose == "notes":
        fs.save_to_json(summary, purpose=purpose)
    else:
        fs.save_to_json(summary, purpose=purpose)
    
    return summary, title