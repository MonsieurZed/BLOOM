import os
from pydub import AudioSegment
from pydub.effects import normalize


def leveling_audio_file(folder_path, max_db=-20):
    """
    Iterates over all audio files in a folder and adjusts their decibel levels
    if they exceed the specified maximum decibel level.

    Args:
        folder_path (str): Path to the folder containing audio files.
        max_db (int): Maximum allowed decibel level. Files exceeding this will be adjusted.
    """
    # Supported audio file extensions
    supported_extensions = (".mp3", ".wav", ".flac", ".ogg", ".aac")

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is an audio file
        if os.path.isfile(file_path) and file_name.lower().endswith(
            supported_extensions
        ):
            try:
                # Load the audio file
                audio = AudioSegment.from_file(file_path)

                # Calculate the current decibel level
                current_db = audio.dBFS

                # Check if the decibel level exceeds the maximum allowed
                if current_db > max_db:
                    print(f"Adjusting {file_name}: Current dBFS = {current_db:.2f}")

                    # Normalize the audio to the maximum allowed decibel level
                    adjustment_factor = max_db - current_db
                    adjusted_audio = audio.apply_gain(adjustment_factor)

                    # Save the adjusted audio back to the same file
                    adjusted_audio.export(file_path, format=file_name.split(".")[-1])
                    print(f"{file_name} adjusted to {max_db} dBFS.")
                else:
                    print(
                        f"{file_name} is within acceptable dBFS range: {current_db:.2f}"
                    )
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    leveling_audio_file(r"D:\GIT\BLOOM\BLOOM\data\sounds")
