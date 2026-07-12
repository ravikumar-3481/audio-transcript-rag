from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_transcript(transcript : str) -> list:
    try:
        if not transcript:
            return []
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 3000,
            chunk_overlap = 240,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(transcript)
    except Exception as e:
        print(f"Failed to chunk transcript: {e}")
        return []



   

    