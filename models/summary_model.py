from agent.llm import LLM
from agent.system.prompts import SystemPrompts
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from core.chunking import Chunking

sp = SystemPrompts()
llm_model = LLM()
chunk = Chunking()


class TranscriptSummarizer:
    def __init__(self, llm=None):
        self._llm = llm or llm_model.get_llm()
        if not self._llm:
            raise ValueError("No LLM available")
        self._prompt_strategies = {
            "summarize": sp.summary_prompt,
            "notes": sp.study_notes_prompt,
            "pdf_notes": sp.pdf_analysis_prompt,
        }
        self.chunk = Chunking()


    def _build_chain(self, system_prompt: str):
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{text}")]
        )
        return (
            {"text": RunnablePassthrough()}
            | prompt_template
            | self._llm
            | StrOutputParser()
        )

    def get_summary(self, transcript: str, purpose: str = "summarize") -> str:
        if not transcript:
            print("No transcript to summarize")
            return ""

        if purpose == "summarize":
            prompt = self._prompt_strategies["summarize"]()
        elif purpose == "notes":
            prompt = self._prompt_strategies["notes"]()
        


        try:
            chain = self._build_chain(prompt)
            chunks_context = self.chunk.chunk_transcript(transcript)
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

    def get_title(self, summary: str) -> str:
        if not summary:
            print("No summary to generate title from")
            return ""
        try:
            prompt = sp.title_prompt()
            chain = self._build_chain(prompt)
            title = chain.invoke({"text": summary})
            return title
        except Exception as e:
            print(f"Failed to generate title: {e}")
            raise

    def get_pdf_summary(self, raw_text: str) -> str:
        if not raw_text:
            print("No transcript to summarize")
            return ""
        prompt = self._prompt_strategies["pdf_notes"]()
        try:
            chain = self._build_chain(prompt)
            chunks_context = self.chunk.chunk_transcript(raw_text)
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