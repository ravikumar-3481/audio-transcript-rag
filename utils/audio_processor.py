import os
import shutil
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = "data/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFMPEG_LOCATION = os.environ.get("FFMPEG_LOCATION")


def resolve_ffmpeg_location() -> str | None:
    def locate_executable(path: str, name: str) -> bool:
        if os.path.isfile(path):
            return True
        if os.path.isdir(path):
            return os.path.exists(os.path.join(path, name))
        return False

    if FFMPEG_LOCATION:
        ffmpeg_path = FFMPEG_LOCATION
        ffprobe_path = FFMPEG_LOCATION

        if os.path.isdir(FFMPEG_LOCATION):
            ffmpeg_path = os.path.join(FFMPEG_LOCATION, "ffmpeg.exe")
            ffprobe_path = os.path.join(FFMPEG_LOCATION, "ffprobe.exe")

        if locate_executable(ffmpeg_path, "ffmpeg.exe") and locate_executable(ffprobe_path, "ffprobe.exe"):
            return FFMPEG_LOCATION

        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if ffmpeg and ffprobe:
            return None

        raise FileNotFoundError(
            f"FFMPEG_LOCATION is set to '{FFMPEG_LOCATION}', but ffmpeg/ffprobe were not found there or on PATH."
        )

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return None

    raise FileNotFoundError(
        "ffmpeg and ffprobe were not found on PATH. Install them or set the FFMPEG_LOCATION environment variable."
    )


def download_youtube_audio(url: str) -> str:
    ffmpeg_location = resolve_ffmpeg_location()
    output_path = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    if ffmpeg_location:
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace('.webm', '.wav').replace('.m4a', '.wav')
        return filename

def fix_audio_format(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + '_converted.wav'
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format='wav')
    return output_path

def chunk_audio(wav_path : str, chunk_seconds : int = 25) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_length_ms = chunk_seconds * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[start : start + chunk_length_ms]
        chunk_path = f"{wav_path.replace('.wav', '')}_chunk_{i+1}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks

def process_audio(url : str, language: str = "english") -> list :
    if url.startswith("https://") or url.startswith("http://"):
        print("Downloading audio...", "\n")
        wav_path = download_youtube_audio(url)
        print("Audio Download Complete...", "\n", "Fixing Audio Format.....")
        wav = fix_audio_format(wav_path)
        os.remove(wav_path)
        print("Original Audio File Has Been Removed...", "\n")
        wav_path = wav
    else :
        print("Detected Local File... Converting to wav.....", "\n")
        wav_path = fix_audio_format(url)

    print("Chunking Audio...", "\n")
    chunk_seconds = 25 if language.lower() == "hinglish" else 600
    chunks = chunk_audio(wav_path, chunk_seconds)
    print(f"Audio ready -- {len(chunks)} Chunks Created", "\n")
    os.remove(wav_path)
    return chunks

