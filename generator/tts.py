import os, json, time, whisper
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from whisper.utils import get_writer
from elevenlabs.client import ElevenLabs
from tools.bloom import Bloom
from tools.utility import Utility, Key


class TTSGen:
    _client: ElevenLabs
    _output: str

    def __init__(self, output):
        self._client = ElevenLabs(api_key=Key.get("elevenlabs"))

    def generate_mp3(self, text, output_audio_file):
        timer = time.time()
        print("Generating MP3 ...", end="")

        load_dotenv()

        audio = self._client.text_to_speech.convert(
            text=text,
            voice_id="TxGEqnHWrfWFTfGW9XjX",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.25,
                use_speaker_boost=True,
                speed=1.10,
            ),
        )

        with open(output_audio_file, "wb") as f:
            for (
                chunk
            ) in audio:  # Iterate over the generator and write chunks to the file
                f.write(chunk)

        print(f"{round(time.time() - timer, 2)} seconds.")
        return output_audio_file

    def generate_subs(self, output_path, input_filename, output_filename) -> json:
        timer = time.time()
        print("Generating Subs ...", end="")

        model = whisper.load_model("base")  # Change this to your desired model

        transcribe = model.transcribe(
            audio=output_path + "\\" + input_filename.value,
            word_timestamps=True,
        )
        segments = Utility.segment_cleaner(transcribe["segments"])

        Utility.save_to_file_json(output_path, output_filename.value, segments)

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
