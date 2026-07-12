from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from agent.llm import get_llm
from agent.prompts import summary_prompt, title_prompt, combine_summary_prompt
from core.chunking import chunk_transcript



def get_summary(transcript : str) -> str:
    if not transcript:
        print("No transcript to summarize")
        return ""
    llm = get_llm()
    if not llm:
        raise ValueError("No LLM available")
    prompt = summary_prompt()
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

        combine_summary = combine_summary_prompt()

        combined_prompt = ChatPromptTemplate.from_messages(
            [("system", combine_summary), ("human", "{text}")]
        )

        combine_chain = (
            {"text": RunnablePassthrough()}
            | combined_prompt
            | llm
            | StrOutputParser()
        )
        print("Combining summaries...")
        final_summary = combine_chain.invoke({"text": combined_summary})
        return final_summary
    

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

def summarizer(transcript : str) -> str:
    if not transcript:
        print("No transcript to summarize")
        return ""
    
    try:
        print("Summarizing transcript...")
        summary = get_summary(transcript)
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