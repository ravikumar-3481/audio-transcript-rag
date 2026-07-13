from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from agent.llm import get_llm
from agent.system.prompts import summary_prompt, title_prompt, study_notes_prompt
from utils.text_process import get_transcript
from utils.tools import save_to_json
from core.chunking import chunk_transcript



def get_summary(transcript : str, purpose : str = "summarize") -> str:
    if not transcript:
        print("No transcript to summarize")
        return ""
    llm = get_llm()
    if not llm:
        raise ValueError("No LLM available")
    
    if purpose == "summarize":
        prompt = summary_prompt()
    elif purpose == "notes":
        prompt = study_notes_prompt()


    try:
        prompt_template = ChatPromptTemplate.from_messages([("system", prompt), ("human", "{text}")])
        chain = (
            {"text": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )
        chunks_context = chunk_transcript(transcript)
        if not chunks_context:
            raise ValueError("No chunks to summarize")
        
        chunk_summaries = []
        for chunk in chunks_context:
            summary = chain.invoke({"text": chunk})
            chunk_summaries.append(summary)

        combined_summary = "\n\n".join(chunk_summaries)
        return combined_summary
    

    except (ModuleNotFoundError, RuntimeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Failed to summarize transcript: {e}") from e


def get_title(summary : str) -> str:
    if not summary:
        print("No summary to generate title from")
        return ""
    try:
        llm = get_llm()
        if not llm:
            raise ValueError("No LLM available")
        prompt = title_prompt()
        prompt_template = ChatPromptTemplate.from_messages([("system", prompt), ("human", "{text}")])
        chain = (
            {"text": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )
        title = chain.invoke({"text": summary})
        return title
    except Exception as e:
        print(f"Failed to generate title: {e}")
        raise

def summarizer(transcript : str, purpose : str = "summarize") -> str:
    if not transcript:
        print("No transcript to summarize")
        return ""
    
    try:
        if purpose == "notes":
            print("Generating notes....")
        else:
            print("Summarizing transcript...")
             
        summary = get_summary(transcript, purpose=purpose)
        if not summary:
            raise ValueError("No summary to generate title from")
        print("Generating title...")
        title = get_title(summary)
        print(f"Title: {title}\n")
        if not title:
            raise ValueError("No title to generate")
        return summary, title
    

    except (ModuleNotFoundError, RuntimeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Failed to summarize transcript: {e}") from e
    
def summarize(source : str, language : str = "english", purpose : str = "summarize"):
    transcript = get_transcript(source , language=language)
    if not transcript:
        raise ValueError("No transcript to summarize")
    
    try:
        summary, title = summarizer(transcript, purpose=purpose)
        
    except Exception as e:
        print(f"Failed to summarize transcript: {e}")
        raise
    
    if purpose == "notes":
        save_to_json(summary, purpose=purpose)
    else:
        save_to_json(summary, purpose=purpose)
    
    return summary, title