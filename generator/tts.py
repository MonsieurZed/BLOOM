import os, json, time, whisper
from dotenv import load_dotenv
from pathlib import Path
from elevenlabs import VoiceSettings
from whisper.utils import get_writer
from elevenlabs.client import ElevenLabs
from tools.utility import Utility, Key


class TTSGen:
    _client: ElevenLabs
    _output: str

    def __init__(self):
        print("Loading TTS Gen ...")
        self._client = ElevenLabs(api_key=Key.get("elevenlabs"))

    def generate_mp3(self, text, output_audio_file) -> Path:
        timer = time.time()
        print("Generating MP3 ...", end="")

        load_dotenv()

        audio = self._client.text_to_speech.convert(
            text=text,
            voice_id="TxGEqnHWrfWFTfGW9XjX",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                speed=1.13,
            ),
        )

        with open(output_audio_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        print(f"{round(time.time() - timer, 2)} seconds.")
        return output_audio_file

    def generate_subs(self, audio_path, output_path) -> json:
        timer = time.time()
        print("Generating Subs ...", end="")

        model = whisper.load_model("base")  # Change this to your desired model

        transcribe = model.transcribe(
            audio=str(audio_path),  # Convert WindowsPath to string
            word_timestamps=True,
        )
        segments = Utility.segment_cleaner(transcribe["segments"])

        Utility.save_to_file_json(
            output_path, Path(audio_path).with_suffix(".json"), segments
        )

        print(f"{round(time.time() - timer, 2)} seconds.")
        return segments

    def generate_srt(self, mp3_path):
        timer = time.time()
        print("Generating Subs ...", end="")
        segment_path = os.path.splitext(mp3_path)[0] + ".json"
        model = whisper.load_model("base")
        result = model.transcribe(
            audio=mp3_path, language="en", word_timestamps=True, task="transcribe"
        )

        word_options = {
            "highlight_words": False,
            "max_line_count": 1,
            "max_line_width": 12,
        }

        vtt_writer = get_writer(output_format="srt", output_dir=segment_path)
        vtt_writer(result, mp3_path, word_options)

        print(f"{round(time.time() - timer, 2)} seconds.")

        with open(f"{segment_path}\\audio.srt", "r", encoding="utf-8") as file:
            return file.read()
