import json
import time
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
    VideoClip,
    CompositeAudioClip,
)
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
import whisper_timestamped as whisper
from collections.abc import Callable
from PIL import Image
from PIL.Image import Resampling
import math
import numpy
from script.basic import Utility


class VideoGen:
    _output: str
    _select: str

    def __init__(self, output, select=False):
        self._output = output
        self._select = select

    def _zoom_in_effect(
        self,
        clip: VideoClip,
        ratio: float = 0.04,
    ) -> VideoClip:
        """
        Apply a zoom effect to a clip.
        """

        def _apply(
            get_frame: Callable[[float], numpy.ndarray],
            t: float,
        ) -> numpy.ndarray:
            # Get the frame
            img = Image.fromarray(get_frame(t))
            base_size = img.size

            # Calculate the new size
            new_size = (
                math.ceil(img.size[0] * (1 + (ratio * t))),
                math.ceil(img.size[1] * (1 + (ratio * t))),
            )

            # Make the size even
            new_size = (
                new_size[0] + (new_size[0] % 2),
                new_size[1] + (new_size[1] % 2),
            )

            # Resize the image
            img = img.resize(new_size, Resampling.LANCZOS)

            # Crop the image
            x = math.ceil((new_size[0] - base_size[0]) / 2)
            y = math.ceil((new_size[1] - base_size[1]) / 2)
            img = img.crop((x, y, new_size[0] - x, new_size[1] - y)).resize(
                base_size, Resampling.LANCZOS
            )

            # Convert to numpy array and return
            result = numpy.array(img)
            img.close()
            return result

        return clip.fl(_apply)

    def _get_text_clips(self, text, fontsize):
        text_clips = []
        for segment in text:
            for word in segment["words"]:
                text_clips.append(
                    TextClip(
                        word["text"],
                        fontsize=fontsize,
                        method="caption",
                        stroke_width=4,
                        stroke_color="black",
                        font="Open Sans ExtraBold",
                        color="white",
                    )
                    .set_start(word["start"])
                    .set_end(word["end"])
                    .set_position("center")
                )
        return text_clips

    def _get_transcribed_text(self, filename):
        audio = whisper.load_audio(filename)
        model = whisper.load_model("small", device="cpu")
        results = whisper.transcribe(model, audio, language="en")
        return results["segments"]

    def create_background_video(self):
        timer = time.time()
        print("Generating background video ... ", end="")

        image_folder = f"{self._output}"
        sync_file = f"{self._output}\\sync_result"
        audio_file = f"{self._output}\\audio.mp3"
        music_file = r"D:\GIT\BLOOM\BLOOM\data\suspense.mp3"
        background_file = f"{self._output}\\backround.mp4"

        resolution = (808, 1440)
        fps = 30

        with open(sync_file, "r") as f:
            sync_data = json.load(f)["sync"]

        clips = []
        for n, sync in enumerate(sync_data):
            scene = sync["scene"]
            start_time = sync["start_time"]
            end_time = sync["end_time"]

            # Calculate duration
            start_seconds = sum(
                int(x) * 60**i for i, x in enumerate(reversed(start_time.split(":")))
            )
            end_seconds = sum(
                int(x) * 60**i for i, x in enumerate(reversed(end_time.split(":")))
            )
            duration = end_seconds - start_seconds

            # Load the image for the scene
            if scene == "0":
                image_path = r"D:\GIT\BLOOM\BLOOM\data\intro.png"
                clip = ImageClip(image_path, duration=duration)
                clips.append(clip)
                continue
            else:
                image_path = Utility.get_scene(image_folder, scene)

            if not image_path:
                print(f"Image for scene {scene} not found: {image_path}")
                continue

            # Create an ImageClip
            clip = ImageClip(image_path, duration=duration)
            clips.append(clip)
            clips[n] = self._zoom_in_effect(clips[n], 0.04)

        image_path = r"D:\GIT\BLOOM\BLOOM\data\outro.png"
        clip = ImageClip(image_path, duration=3)
        clips.append(clip)

        # Concatenate all clips
        if clips:
            final_video = concatenate_videoclips(clips, method="compose")
            audio_clip_1 = AudioFileClip(audio_file)
            audio_clip_2 = AudioFileClip(music_file).volumex(0.1)

            # Add fade-in and fade-out effects to the music
            audio_clip_2 = audio_fadein(audio_clip_2, duration=3)  # 3-second fade-in
            audio_clip_2 = audio_fadeout(audio_clip_2, duration=3)  # 3-second fade-out

            # Combine the audio files
            combined_audio = CompositeAudioClip([audio_clip_1, audio_clip_2])

            # Set the combined audio to the final video
            final_video.audio = combined_audio

            final_video.write_videofile(background_file, fps=fps, codec="libx264")

            print(f"Video created successfully: {background_file}")
        else:
            print("No clips were created. Please check your sync file and images.")

        print(f"{round(time.time() - timer, 2)} seconds.")

    # Loading the video as a VideoFileClip

    def add_sub_to_video(self):
        timer = time.time()
        print("Generating background video ... ", end="")

        background_file = f"{self._output}\\backround.mp4"
        audio_file = f"{self._output}\\audio.mp3"
        audio = AudioFileClip(audio_file)
        original_clip = VideoFileClip(background_file)

        transcribed_text = self._get_transcribed_text(audio_file)

        text_clip_list = self._get_text_clips(text=transcribed_text, fontsize=90)

        final_clip = CompositeVideoClip([original_clip] + text_clip_list).set_duration(
            audio.duration + 5
        )

        final_clip.write_videofile(f"{self._output}/final.mp4", codec="libx264")
        print(f"{round(time.time() - timer, 2)} seconds.")
