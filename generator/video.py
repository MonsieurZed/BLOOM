from pathlib import Path
import numpy, math, json, time, textwrap
from PIL import Image
from PIL.Image import Resampling
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from moviepy.audio.AudioClip import concatenate_audioclips
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
import whisper_timestamped as whisper
from tools.utility import Utility, Key


class VideoGen:
    _output: str
    _select: str
    _fps: int
    _resolution: tuple[int, int]
    _codec: int

    def __init__(self, select=False, fps=24, resolution=(768, 1408), codec="libx264"):
        print("Loading Video Gen ...")
        self._select = select
        self._fps = fps
        self._resolution = resolution
        self._codec = codec

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

    def _get_text_clips(self, asr, fontsize):
        text_clips = []
        for segment in asr:
            for word in segment["words"]:

                wrapped_text = textwrap.fill(word["word"], width=16)

                text_clips.append(
                    TextClip(
                        wrapped_text,
                        fontsize=fontsize,
                        method="caption",
                        stroke_width=4,
                        stroke_color="black",
                        font="Arial-Black",
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

    def create_sound_design(
        self,
        sound_json: str,
        output_audio_path: str,
        sound_folder: Path,
        fade_duration: float = 4.0,
    ):
        """
        Creates a sound design by merging audio clips from a JSON file into one audio clip
        at the correct timestamps, ensuring each clip is a maximum of 4 seconds and applying
        fade-in and fade-out effects.

        Args:gg
            json_file_path (str): Path to the JSON file containing sound clip paths and timestamps.
            output_audio_path (str): Path to save the merged audio file.
            fade_duration (float): Duration of the fade-in and fade-out effects (in seconds).
        """
        # List to store all audio clips
        audio_clips = []

        # Iterate over the sounds in the JSON file
        for sound in sound_json:
            sound_path = sound["path"]
            timestamp = float(sound["time"])

            try:
                # Load the sound clip
                sound_clip = AudioFileClip(str(sound_folder / sound_path))

                # Trim the clip to a maximum of 4 seconds
                sound_clip = sound_clip.subclip(0, min(6, sound_clip.duration))

                # Apply fade-in and fade-out effects
                sound_clip = sound_clip.audio_fadein(0.5).audio_fadeout(2).volumex(0.1)

                # Set the start time for the sound clip
                sound_clip = sound_clip.set_start(timestamp)

                # Add the sound clip to the list
                audio_clips.append(sound_clip)
            except Exception as e:
                print(f"Error processing sound {sound_path}: {e}")

        # Combine all audio clips
        combined_audio = CompositeAudioClip(audio_clips)

        # Write the combined audio to a file
        combined_audio.write_audiofile(output_audio_path, fps=44100)

        print(f"Merged audio saved to: {output_audio_path}")

        return str(output_audio_path)

    def create_background_video(
        self,
        sync_data: json = None,
        intro_img_path=None,
        outro_img_path=None,
        outro_audio_path=None,
        image_folder=None,
        tts_path=None,
        music_path=None,
        sound_path=None,
        partial_video_path=None,
    ):

        timer = time.time()
        print(f"Generating {partial_video_path} ... ", end="")

        clips = []

        for sync in sync_data:
            scene = sync["scene"]
            start_time = sync["start_time"]
            end_time = sync["end_time"]

            # Calculate duration
            # start_seconds = sum(
            #     int(x) * 60**i for i, x in enumerate(reversed(start_time.split(":")))
            # )
            # end_seconds = sum(
            #     int(x) * 60**i for i, x in enumerate(reversed(end_time.split(":")))
            # )
            # duration = end_seconds - start_seconds
            duration = end_time - start_time
            # Load the image for the scene

            image_path = (
                intro_img_path if scene == 0 else Utility.get_scene(image_folder, scene)
            )

            if not image_path:
                print(f"Image for scene {scene} not found: {image_path}")
                continue

            clip = ImageClip(str(image_path), duration=duration)
            # Create an ImageClip and apply zoom effect
            if scene != 0:
                clip = self._zoom_in_effect(clip, 0.04)

            clips.append(clip)

        # Add outro clip
        outro_clip = ImageClip(str(outro_img_path), duration=3)
        clips.append(outro_clip)

        # Concatenate all clips
        if clips:

            part_video = concatenate_videoclips(clips, method="compose")
            story_clip = AudioFileClip(str(tts_path))
            outro_audio_path = AudioFileClip(str(outro_audio_path))
            music_clip = AudioFileClip(str(music_path))
            sound_clip = AudioFileClip(str(sound_path))
            # Add fade-in and fade-out effects to the music

            music_clip = music_clip.subclip(0, story_clip.duration)
            music_clip = audio_fadein(music_clip, duration=1)  # 3-second fade-in
            music_clip = audio_fadeout(music_clip, duration=3)  # 3-second fade-out
            music_clip = music_clip.volumex(0.15)
            # Combine the audio files

            bloom_start_time = max(0, story_clip.duration - 2)

            outro_audio_path = outro_audio_path.set_start(bloom_start_time)
            outro_audio_path = audio_fadein(outro_audio_path, duration=1)
            outro_audio_path = audio_fadeout(outro_audio_path, duration=1)

            final_audio = CompositeAudioClip(
                [story_clip, sound_clip, music_clip, outro_audio_path]
            )

            # Set the combined audio to the final video
            part_video.audio = final_audio

            # Write the final video to a file
            part_video.write_videofile(
                str(partial_video_path), fps=self._fps, codec=self._codec
            )

            print(f"Video created successfully: {partial_video_path}")
            return str(partial_video_path)
        else:
            print("No clips were created. Please check your sync file and images.")

        print(f"{round(time.time() - timer, 2)} seconds.")

    def add_sub_to_video(
        self,
        part_video_file,
        audio_file,
        subtitle_file,
        final_path,
    ):
        timer = time.time()
        print("Adding subtitles to video ... ", end="")

        audio = AudioFileClip(str(audio_file))
        original_clip = VideoFileClip(str(part_video_file))

        # Generate text clips
        text_clip_list = self._get_text_clips(asr=subtitle_file, fontsize=90)

        # Combine the original video with the text clips
        final_clip = CompositeVideoClip([original_clip] + text_clip_list).set_duration(
            audio.duration + 3
        )

        # Write the final video to a file
        final_clip.write_videofile(
            str(final_path),
            fps=self._fps,
            codec=self._codec,
        )
        print(f"{round(time.time() - timer, 2)} seconds.")
        return str(final_path)
