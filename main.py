import time
from script.basic import *
from script.llm import LLMGen
from script.bloom import Bloom
from script.video import VideoGen
from script.tts import TTSGen
from pathlib import Path

# json_file_path = r"D:\GIT\BLOOM\BLOOM\_generative\11 Mai 1997_USA, Los Angeles"
batch = r"_output\batch_0"
mono = r"D:\GIT\BLOOM\BLOOM\_output\batch_0\3_09.Avril.2003_Nouvelle-Zélande"

mode = False  # false > mono | true > batch

base_language = Bloom.Languages.English
other_languages = [Bloom.Languages.French, Bloom.Languages.Spanish]

make_voice = False
make_sub = False
make_subcheck = False
make_storyboard = False
make_sounddesign = False
make_sdxl = False
make_image = True
select_image = False
make_background = False
make_video = False
make_publish = False
make_languages = False

number_of_scene = 7
# image_style = "In the 90s aesthetic style vintage faded colors desatured"
image_style = "A nostalgic 90s-style photograph taken with a disposable camera"
image_mood = "suspense"
image_iteration = 2

title_tag = "Darwin Award,"


def make(output_folder: str):

    base = Bloom.set_video(output_folder, base_language)
    date = base.get("date", "Unknown Date")
    place = base.get("place", "Unknown Location")
    story_text = base.get("story", "No Story Provided")

    llm = LLMGen(Bloom.Model.Gemini_2Flash, output_folder, log=True)
    tts = TTSGen(output_folder)
    video = VideoGen(output_folder)

    title = f"{title_tag} {date}, {place}"

    timer = time.time()

    ##### Storyboard

    storyboard_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Storyboard)
    if not Utility.check_file_exists(storyboard_path) or make_storyboard:
        storyboard = llm.ask(
            sys=Bloom.Prompt.System.Storyboard,
            prompt=f"Number of scene needed : {number_of_scene}\nStory : {base}",
        )
    else:
        with open(storyboard_path, "r", encoding="utf-8") as file:
            storyboard = Utility.json_from_str(file.read())

    ##### SDXL

    sdxl_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.SDXL)
    if not Utility.check_file_exists(sdxl_path) or make_sdxl:
        prompt = llm.ask(
            sys=Bloom.Prompt.System.SDXL,
            prompt=f"Style:'{image_style}'\nMood : {image_mood} \nIteration quantity : {image_iteration}\nStoryboard : {storyboard}",
        )

    ##### TEXT AND MP3 Generation

    mp3_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
    if not Utility.check_file_exists(mp3_path) or make_voice:
        storyteller = llm.ask(
            sys=Bloom.Prompt.System.Storyteller,
            prompt=f"Story_starter:\n{title}\nStory:\n{story_text}",
        )
        mp3_path = tts.generate_mp3(storyteller)
    else:
        storyteller_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Storyteller)
        with open(storyteller_path, "r", encoding="utf-8") as file:
            storyteller = file.read()

    ##### SUBTITLE

    sub_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_json)
    if not Utility.check_file_exists(sub_path) or make_sub:
        subs = tts.generate_subs(mp3_path)
    else:
        with open(sub_path, "r", encoding="utf-8") as file:
            subs = file.read()

    subcheck_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Subschecker)
    if not Utility.check_file_exists(subcheck_path) or make_subcheck:
        subs = llm.ask(
            sys=Bloom.Prompt.System.Subschecker,
            prompt=f"story:{storyteller}\n\n\n{subs}",
        )
    else:
        with open(subcheck_path, "r", encoding="utf-8") as file:
            subs = file.read()

    ##### SYNC

    sync_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.ImageSync)
    if not Utility.check_file_exists(sync_path) or make_storyboard or make_sub:
        sync = llm.ask(
            sys=Bloom.Prompt.System.ImageSync,
            prompt=f"Storyboard:\n{storyboard}\n\n\nSubtilte :\n{subs}",
        )

    sound_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.SoundDesigner)
    if not Utility.check_file_exists(sound_path) or make_sounddesign:
        sound = llm.ask(
            sys=Bloom.Prompt.System.SoundDesigner,
            prompt=f"Storyboard:\n{storyteller}\n\n\nSubtilte :\n{subs}",
        )

    ##### IMG GEN

    if make_image:
        llm.ask_image(quantity=1, select=select_image)

    ##### PUBLISH

    publish_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Publish)
    if not Utility.check_file_exists(publish_path) or make_publish:
        publish = llm.ask(
            sys=Bloom.Prompt.System.Publish,
            prompt=base,
        )

    #### VIDEO

    background_path = Bloom.get_output_file_path(Bloom.OutputFile.Part_mp4)
    if not Utility.check_file_exists(background_path) or make_background:
        video.create_background_video()

    final_path = Bloom.get_root_file_path(Bloom.OutputFile.Final_mp4, base_language)
    if not Utility.check_file_exists(final_path) or make_video:
        video.add_sub_to_video()

    print(f"Finished in {round(time.time() - timer, 2)} seconds.")

    if make_languages:
        for language in other_languages:
            base = Bloom.set_video(output_folder, language)

            ##### TEXT AND MP3 Generation
            mp3_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
            if not Utility.check_file_exists(mp3_path) or make_voice:
                translated_storyteller = llm.ask(
                    sys=Bloom.Prompt.System.Translate,
                    prompt={f"Translate to {language.value} : {storyteller}"},
                )
                mp3_path = tts.generate_mp3(translated_storyteller)

            ##### SUBTITLE
            sub_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_json)
            if not Utility.check_file_exists(sub_path) or make_sub:
                subs = tts.generate_subs(mp3_path)
            else:
                with open(sub_path, "r", encoding="utf-8") as file:
                    subs = file.read()

            subcheck_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Subschecker)
            if not Utility.check_file_exists(subcheck_path) or make_subcheck:
                subs = llm.ask(
                    sys=Bloom.Prompt.System.Subschecker,
                    prompt=f"story:{storyteller}\n\n\n{subs}",
                )
            else:
                with open(subcheck_path, "r", encoding="utf-8") as file:
                    subs = file.read()

            sync_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.ImageSync)
            if not Utility.check_file_exists(sync_path) or make_storyboard or make_sub:
                Bloom.copy_file_from(
                    filename=Bloom.Prompt.System.ImageSync.value
                    + Bloom.Prompt.Suffix.Result.value
                )

            background_path = Bloom.get_output_file_path(Bloom.OutputFile.Part_mp4)
            if not Utility.check_file_exists(background_path) or make_background:
                video.create_background_video()

            final_path = Bloom.get_root_file_path(Bloom.OutputFile.Final_mp4, language)
            if not Utility.check_file_exists(final_path) or make_video:
                video.add_sub_to_video()


if mode:
    batch_path = Path(batch)
    for folder in batch_path.iterdir():
        if folder.is_dir():
            make(str(folder))
else:
    make(mono)
