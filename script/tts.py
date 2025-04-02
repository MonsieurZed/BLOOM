import time
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from script.basic import Key, Utility
import whisper
from elevenlabs import VoiceSettings
from whisper.utils import get_writer
from script.bloom import Bloom
import json


class TTSGen:
    _client: ElevenLabs
    _output: str

    def __init__(self, output):
        self._client = ElevenLabs(api_key=Key.get("elevenlabs"))
        self._output = output

    def generate_mp3(self, text):
        timer = time.time()
        output_audio_file = Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
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

    def generate_subs(self, path_mp3):
        timer = time.time()
        print("Generating Subs ...", end="")
        sgmtFilename = Bloom.get_output_file_path(Bloom.OutputFile.Audio_json)

        model = whisper.load_model("base")  # Change this to your desired model

        transcribe = model.transcribe(
            audio=path_mp3,
            word_timestamps=True,
        )
        segments = transcribe["segments"]

        cleaned_segment = json.dumps(Utility.segment_cleaner(segments))
        with open(sgmtFilename, "w", encoding="utf-8") as file:
            file.write(cleaned_segment)

        print(f"{round(time.time() - timer, 2)} seconds.")
        return cleaned_segment

    def generate_srt(self, path_mp3):
        timer = time.time()
        print("Generating Subs ...", end="")

        model = whisper.load_model("base")
        result = model.transcribe(
            audio=path_mp3, language="en", word_timestamps=True, task="transcribe"
        )

        word_options = {
            "highlight_words": False,
            "max_line_count": 1,
            "max_line_width": 12,
        }

        vtt_writer = get_writer(output_format="srt", output_dir=self._output)
        vtt_writer(result, path_mp3, word_options)

        print(f"{round(time.time() - timer, 2)} seconds.")

        with open(f"{self._output}\\audio.srt", "r", encoding="utf-8") as file:
            return file.read()
