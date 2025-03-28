from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from script.basic import Key
from datetime import timedelta
import os
import whisper
import re
from moviepy.audio.io.AudioFileClip import AudioFileClip  # Import for MP3 duration

from whisper.utils import get_writer


class TTS:
    _client: ElevenLabs
    _output: str

    def __init__(self, output):
        self._client = ElevenLabs(api_key=Key.get("elevenlabs"))
        self._output = output

    def generate_mp3(self, text, output_audio_file):
        load_dotenv()
        audio = self._client.text_to_speech.convert(
            text=text,
            voice_id="TxGEqnHWrfWFTfGW9XjX",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        with open(output_audio_file, "wb") as f:
            for (
                chunk
            ) in audio:  # Iterate over the generator and write chunks to the file
                f.write(chunk)

    def generate_subs(self, path_mp3):
        model = whisper.load_model("base")  # Change this to your desired model
        print("Whisper model loaded.")
        transcribe = model.transcribe(
            audio=path_mp3,
            word_timestamps=True,
        )
        segments = transcribe["segments"]

        for segment in segments:
            startTime = str(0) + str(timedelta(seconds=int(segment["start"]))) + ",000"
            endTime = str(0) + str(timedelta(seconds=int(segment["end"]))) + ",000"
            text = segment["text"]
            segmentId = segment["id"] + 1
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"

            srtFilename = path_mp3.replace(".mp3", ".srt")
            with open(srtFilename, "a", encoding="utf-8") as srtFile:
                srtFile.write(segment)

        return srtFilename

    def generate_str_v2(self, path_mp3):
        model = whisper.load_model("base")  # Change this to your desired model
        print("Whisper model loaded.")
        result = model.transcribe(
            audio=path_mp3, language="en", word_timestamps=True, task="transcribe"
        )

        # Set VTT Line and words width
        word_options = {
            "highlight_words": False,
            "max_line_count": 1,
            "max_line_width": 42,
        }
        vtt_writer = get_writer(output_format="vtt", output_dir="./")
        vtt_writer(result, path_mp3, word_options)
