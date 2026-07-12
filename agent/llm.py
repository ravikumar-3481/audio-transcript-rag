from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os

load_dotenv()

_llm = None

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_llm():

    global _llm
    if _llm is None:
        try:    
            if not MISTRAL_API_KEY:
                raise ValueError("MISTRAL_API_KEY is not set")
            _llm = ChatMistralAI(model="mistral-small-latest", MISTRAL_API_KEY=MISTRAL_API_KEY, temperature=0.3)
        except Exception as e:
            print(f"Failed to initialize Mistral AI client: {e}")
            raise
    return _llm


    