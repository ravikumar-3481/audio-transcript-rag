from deepgram import DeepgramClient
from utils.audio_processor import process_audio
from dotenv import load_dotenv
from utils.tools import save_to_dir, remove_a_dir
import requests
import json
import os

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = "saaras:v2.5"

_client = None

def get_client():
    global _client
    if _client is None:
        try:
            api_key = os.getenv("DEEPGRAM_API_KEY")
            if not api_key:
                raise ValueError("DEEPGRAM_API_KEY is not set")
            _client = DeepgramClient(api_key=api_key)
        except Exception as e:
            print(f"Failed to initialize Deepgram client: {e}")
            raise
    return _client

def transcribe_chunk_deepgram(chunk_path : str, translate : bool = False) -> str:
    try:
        client = get_client()
    except Exception as e:
        print(f"Deepgram client unavailable: {e}")
        return ""

    try:
        with open(chunk_path, "rb") as audio:
            buffer_data = audio.read()
    except (FileNotFoundError, OSError) as e:
        print(f"Could not read audio chunk {chunk_path}: {e}")
        return ""

    kwargs = {
        "model": "nova-3",
        "smart_format": True,
    }

    if translate:
        kwargs["detect_language"] = True

    try:
        response = client.listen.v1.media.transcribe_file(request=buffer_data, **kwargs)
        return response.results.channels[0].alternatives[0].transcript
    except (AttributeError, IndexError, KeyError) as e:
        print(f"Unexpected Deepgram response format for {chunk_path}: {e}")
        return ""
    except Exception as e:
        print(f"Deepgram transcription failed for {chunk_path}: {e}")
        return ""



def transcribe_chunk_sarvam(chunk_path : str) -> str:
    if not SARVAM_API_KEY:
        print("SARVAM_API_KEY is not set\nShifting To Deepgram")
        return transcribe_chunk_deepgram(chunk_path)

    headers = {"api-subscription-key": SARVAM_API_KEY}
    data = {"model": SARVAM_MODEL, "with_diarization": "false"}

    try:
        with open(chunk_path, "rb") as audio:
            files = {"file" : (os.path.basename(chunk_path), audio, "audio/wav")}
            response = requests.post(
                SARVAM_STT_TRANSLATE_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=300,
            )
        response.raise_for_status()
    except (FileNotFoundError, OSError) as e:
        print(f"Could not read audio chunk {chunk_path}: {e}")
        return ""
    except requests.exceptions.Timeout:
        print(f"Sarvam request timed out for {chunk_path}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"Sarvam request failed for {chunk_path}: {e}")
        return ""

    try:
        transcript = response.json().get("transcript", "")
    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        print(f"Could not parse Sarvam response for {chunk_path}: {e}")
        return ""

    return transcript



def transcribe_chunk(chunk_path : str, language: str = "english") -> str:
    try:
        if language.lower() =="hinglish":
            return transcribe_chunk_sarvam(chunk_path)
        return transcribe_chunk_deepgram(chunk_path)
    except Exception as e:
        print(f"Unexpected error transcribing chunk {chunk_path}: {e}")
        return ""


def transcribe_all(chunks : list, language: str = "english") -> str:
    full_transcribe = ""
    engine = "Sarvam Ai" if language.lower() == "hinglish" else "Deepgram"
    print(f"Using {engine} for transcription...")

    for i , chunk in enumerate(chunks):
        print(f'Transcribing Chunk {i + 1}/{len(chunks)}...')
        try:
            text = transcribe_chunk(chunk, language=language)
        except Exception as e:
            print(f"Skipping chunk {chunk} due to error: {e}")
            text = ""
        full_transcribe += text + "\n"
        print("Transcription Complete...", "\n")
    return full_transcribe


def transcribe(source : str, language: str = "english"):
    try:
        chunks = process_audio(source, language=language)
    except Exception as e:
        print(f"Audio processing failed for {source}: {e}")
        raise 

    transcript = transcribe_all(chunks, language=language)
    save_to_dir(transcript, DIRECTORY = "data/transcripts", filename = "transcript.txt")
    remove_a_dir("data/downloads")
    return transcript

