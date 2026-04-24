import os
import subprocess
import uuid

import whisper

AUDIO_DIR = "media/audio"

model = whisper.load_model("small")


def convert_to_wav(input_file, output_file):
    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-ar", "16000",
        "-ac", "1",
        output_file
    ])


def transcribe_audio(file_path: str) -> str:
    wav_filename = f"{uuid.uuid4()}.wav"
    wav_path = os.path.join(AUDIO_DIR, wav_filename)

    convert_to_wav(file_path, wav_path)

    result = model.transcribe(
        wav_path,
        language="ru",
        temperature=0.0
    )

    return result["text"]
