import time, json
from tools.bloom import Bloom
from tools.utility import Utility
from pathlib import Path
from generator import AIGen, VideoGen, TTSGen

# json_file_path = r"D:\GIT\BLOOM\BLOOM\_generative\11 Mai 1997_USA, Los Angeles"
batch = r"_output\batch_0"
mono = r"D:\GIT\BLOOM\BLOOM\_output\batch_0\3_09.Avril.2003_Nouvelle-Zélande"

mode = False  # false > mono | true > batch

base_language = Bloom.Languages.English
other_languages = [Bloom.Languages.French, Bloom.Languages.Spanish]


block_voice = True
make_voice_storytelling = False

make_sub = False
make_subcheck = False
make_storyboard = False
make_sounddesign = False
select_sounddesign = False
make_imagen = True
make_image = True
select_image = False
make_background = True
make_video = True
make_publish = False
make_languages = False

number_of_scene = 7
image_quantity = 1
imagen_prompt = {
    "number_of_scene": number_of_scene,
    "image_iteration": 2,
    "image_style": "A nostalgic 90s-style photograph taken with a disposable camera",
    "additional_rule": "Must be realistic (no drawings) and avoid fictional characters.",
    "image_mood": "suspense",
}

title_tag = "Darwin Award"


def make(output_folder: str):

    base = Bloom.set_video(output_folder, base_language)
    date = base.get("date", "Unknown Date")
    place = base.get("place", "Unknown Location")
    story_text = base.get("story", "No Story Provided")

    llm = AIGen()
    tts = TTSGen(output_folder)
    video = VideoGen(output_folder)

    title = f"{title_tag}:{date},{place}."

    timer = time.time()

    ##### TEXT AND MP3 Generation

    mp3_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
    if not Utility.check_file_exists(mp3_path) or make_voice_storytelling:
        storyteller = llm.ask_json(
            sys=Bloom.Prompt.System.Storyteller,
            prompt={
                "Language": base_language.value,
                "start with": title,
                "story": story_text,
            },
            output_path=Bloom.get_folder_path(),
        )
        if not block_voice:
            mp3_path = tts.generate_mp3(
                storyteller, Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
            )

    else:
        storyteller_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Storyteller)
        with open(storyteller_path, "r", encoding="utf-8") as file:
            storyteller = file.read()

    ##### Storyboard

    storyboard_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Storyboard)
    if not Utility.check_file_exists(storyboard_path) or make_storyboard:
        storyboard = llm.ask_json(
            sys=Bloom.Prompt.System.Storyboard,
            prompt={
                "number of scene": number_of_scene,
                "story": storyteller["storyteller"],
            },
            output_path=Bloom.get_folder_path(),
        )
    else:
        with open(storyboard_path, "r", encoding="utf-8") as file:
            storyboard = json.loads(file.read())

    ##### IMAGEN

    imagen_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.ImageGen)
    if not Utility.check_file_exists(imagen_path) or make_imagen:
        imagen_prompt["story_information"] = base
        imagen_prompt["storyboard"] = storyboard["scene"]

        imagen = llm.ask_json(
            sys=Bloom.Prompt.System.ImageGen,
            prompt=imagen_prompt,
            output_path=Bloom.get_folder_path(),
        )
    else:
        with open(imagen_path, "r", encoding="utf-8") as file:
            imagen = json.loads(file.read())

    ##### SUBTITLE

    sub_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_json)
    if not Utility.check_file_exists(sub_path) or make_sub:
        subs = tts.generate_subs(
            output_path=Bloom.get_folder_path(),
            input_filename=Bloom.OutputFile.Audio_mp3,
            output_filename=Bloom.OutputFile.Audio_json,
        )
    else:
        with open(sub_path, "r", encoding="utf-8") as file:
            subs = json.loads(file.read())

    subcheck_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Subschecker)
    if not Utility.check_file_exists(subcheck_path) or make_subcheck:
        subcheck_prompt = storyteller
        subcheck_prompt["asr"] = subs
        subs = llm.ask_json(
            sys=Bloom.Prompt.System.Subschecker,
            prompt=subcheck_prompt,
            output_path=Bloom.get_folder_path(),
        )
    else:
        with open(subcheck_path, "r", encoding="utf-8") as file:
            subs = json.loads(file.read())

    ##### SYNC

    sync_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.ImageSync)
    if not Utility.check_file_exists(sync_path) or make_storyboard or make_sub:
        sync = llm.ask_json(
            sys=Bloom.Prompt.System.ImageSync,
            prompt={"storyboard": storyboard, "subtitle": subs},
            output_path=Bloom.get_folder_path(),
        )
    else:
        with open(sync_path, "r", encoding="utf-8") as file:
            sync = json.loads(file.read())

    sound_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.SoundDesigner)
    if not Utility.check_file_exists(sound_path) or make_sounddesign:
        sound_json = llm.ask_json(
            sys=Bloom.Prompt.System.SoundDesigner,
            prompt={"storyboard": storyboard, "subtilte": subs},
            sys_custom=Bloom.get_audio_list(),
            output_path=Bloom.get_folder_path(),
        )
    else:
        with open(sound_path, "r", encoding="utf-8") as file:
            sound_json = json.loads(file.read())
    ##### IMG GEN

    if make_image:
        llm.ask_image(
            prompts=imagen,
            output_folder=Bloom.get_common_folder(),
            quantity=image_quantity,
            select=select_image,
        )

    ##### PUBLISH

    publish_path = Bloom.get_prompt_file_path(Bloom.Prompt.System.Publish)
    if not Utility.check_file_exists(publish_path) or make_publish:
        publish = llm.ask_json(
            sys=Bloom.Prompt.System.Publish,
            prompt=base,
            output_path=Bloom.get_folder_path(),
        )
        with open(publish_path, "r", encoding="utf-8") as file:
            publish = json.loads(file.read())
    #### VIDEO

    sound_mp3 = Bloom.get_output_file_path(Bloom.OutputFile.Sound_mp3)
    if not Utility.check_file_exists(sound_mp3) or make_background:
        video.create_sound_design(
            sound_json=sound_json,
            output_audio_path=Bloom.get_output_file_path(Bloom.OutputFile.Sound_mp3),
        )

    background_path = Bloom.get_output_file_path(Bloom.OutputFile.Part_mp4)
    if not Utility.check_file_exists(background_path) or make_background:
        video.create_background_video(
            sync_data=sync,
            image_folder=Bloom.get_common_folder(),
            audio_path=Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3),
            intro_img_path=Bloom.get_data_file_path(Bloom.Data.Intro_img),
            outro_img_path=Bloom.get_data_file_path(Bloom.Data.Outro_img),
            outro_audio_path=Bloom.get_data_file_path(Bloom.Data.Outro_audio),
            music_path=Bloom.get_data_file_path(Bloom.Data.music),
            sound_path=Bloom.get_output_file_path(Bloom.OutputFile.Sound_mp3),
            partial_video_path=Bloom.get_output_file_path(Bloom.OutputFile.Part_mp4),
        )

    final_path = Bloom.get_root_file_path(Bloom.OutputFile.Final_mp4, base_language)
    if not Utility.check_file_exists(final_path) or make_video:
        video.add_sub_to_video(
            part_video_file=Bloom.get_output_file_path(Bloom.OutputFile.Part_mp4),
            audio_file=Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3),
            subtitle_file=Bloom.get_prompt_file_path(Bloom.Prompt.System.Subschecker),
            final_path=Bloom.get_root_file_path(
                Bloom.OutputFile.Final_mp4, Bloom._current_language
            ),
        )

    print(f"Finished in {round(time.time() - timer, 2)} seconds.")

    if make_languages:
        for language in other_languages:
            base = Bloom.set_video(output_folder, language)

            ##### TEXT AND MP3 Generation
            mp3_path = Bloom.get_output_file_path(Bloom.OutputFile.Audio_mp3)
            if not Utility.check_file_exists(mp3_path) or make_voice_storytelling:
                translated_storyteller = llm.ask_json(
                    sys=Bloom.Prompt.System.Translate,
                    prompt={f"Translate to {language.value} : {storyteller}"},
                    output_path=Bloom.get_folder_path(),
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
                subs = llm.ask_json(
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
