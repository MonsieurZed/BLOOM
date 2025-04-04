import time, json
from tools.bloom import Bloom, Dictionnary
from tools.utility import Utility
from pathlib import Path
from generator import AIGen, VideoGen, TTSGen

# json_file_path = r"D:\GIT\BtOOM\BtOOM\_generative\11 Mai 1997_USA, Los Angeles"
batch = r"_output\batch_0"
mono = r"D:\GIT\BLOOM\BLOOM\_output\batch_0\1_08.Avril.2010_Roumanie\base.json"
data_path = r"D:\GIT\BLOOM\BLOOM\data"
mode = False  # false > mono | true > batch

base_language = Dictionnary.Languages.English
other_languages = [Dictionnary.Languages.French, Dictionnary.Languages.Spanish]


block_voice = True
make_voice_storytelling = False

make_sub = False
make_subcheck = False
make_storyboard = False
make_sounddesign = False
select_sounddesign = False
make_imagen = False
make_image = True
select_image = False
make_part = False
make_video = False
make_publish = False
make_languages = False

number_of_scene = 10
image_quantity = 1
imagen_prompt = {
    "number_of_scene": number_of_scene,
    "image_iteration": 2,
    # "image_style": "A nostalgic 90s-style photograph taken with a disposable camera",
    "image_style": "Drawing like the ReLIFE Anime",
    # "additional_rule": "Must be realistic (no drawings) and avoid fictional characters.",
    "additional_rule": "No fictional characters. Only Human",
    "image_mood": "suspense",
}

title_tag = "Darwin Award"


def make(output_folder: str):
    btoom = Bloom(
        base_path=mono, data_path=data_path, language=base_language, style=None
    )

    llm = AIGen()
    tts = TTSGen()
    video = VideoGen()

    prompt = {
        "Language": base_language.value,
        "start with": f"{title_tag}:{btoom.date},{btoom.place}.",
        "story": btoom.story,
    }

    timer = time.time()

    ##### TEXT AND MP3 Generation

    storyteller = btoom.get(Dictionnary.Prompt.Storyteller)
    tts_path = btoom.get(Dictionnary.OutputFile.Audio_mp3)
    if not storyteller or make_voice_storytelling:
        storyteller = llm.ask_json(
            sys=Dictionnary.Prompt.Storyteller,
            prompt=prompt,
            output_path=btoom.get_log_folder(),
        )["storyteller"]
        btoom.add(key=Dictionnary.Prompt.Storyteller, value=storyteller)

        tts_path = tts.generate_mp3(
            storyteller,
            btoom.get_language_folder(Dictionnary.OutputFile.Audio_mp3),
        )
        btoom.add(key=Dictionnary.OutputFile.Audio_mp3, value=str(tts_path))

    ##### Storyboard

    storyboard = btoom.get(Dictionnary.Prompt.Storyboard)
    if not storyboard or make_storyboard:
        storyboard = llm.ask_json(
            sys=Dictionnary.Prompt.Storyboard,
            prompt={
                "number of scene": number_of_scene,
                "story": storyteller,
            },
            output_path=btoom.get_log_folder(),
        )["storyboard"]
        btoom.add(key=Dictionnary.Prompt.Storyboard, value=storyboard)

    ##### IMAGEN

    imagen = btoom.get(Dictionnary.Prompt.ImageGen)
    if not imagen or make_imagen:

        imagen_prompt["story"] = storyteller
        imagen_prompt["storyboard"] = storyboard

        imagen = llm.ask_json(
            sys=Dictionnary.Prompt.ImageGen,
            prompt=imagen_prompt,
            output_path=btoom.get_log_folder(),
        )["imagen"]
        btoom.add(key=Dictionnary.Prompt.ImageGen, value=imagen)

    ##### SUBTITLE

    subtitle = btoom.get(Dictionnary.OutputFile.Audio_json)
    if not subtitle or make_sub:
        subtitle = tts.generate_subs(
            audio_path=btoom.get(Dictionnary.OutputFile.Audio_mp3),
            output_path=btoom.get_log_folder(),
        )
        btoom.add(key=Dictionnary.OutputFile.Audio_json, value=subtitle)

    subcheck = btoom.get(Dictionnary.Prompt.Subschecker)
    if not subcheck or make_subcheck:
        subcheck_prompt = {}
        subcheck_prompt["story"] = storyteller
        subcheck_prompt["asr"] = subtitle

        subcheck = llm.ask_json(
            sys=Dictionnary.Prompt.Subschecker,
            prompt=subcheck_prompt,
            output_path=btoom.get_log_folder(),
        )["asr"]
        btoom.add(key=Dictionnary.Prompt.Subschecker, value=subcheck)

    ##### SYNC

    imagesync = btoom.get(Dictionnary.Prompt.ImageSync)
    if not imagesync or make_storyboard or make_sub:
        imagesync = llm.ask_json(
            sys=Dictionnary.Prompt.ImageSync,
            prompt={"storyboard": storyboard, "subtitle": subtitle},
            output_path=btoom.get_log_folder(),
        )["imagesync"]
        btoom.add(key=Dictionnary.Prompt.ImageSync, value=imagesync)

    sounddesign = btoom.get(Dictionnary.Prompt.SoundDesigner)
    if not sounddesign or make_sounddesign:
        sounddesign = llm.ask_json(
            sys=Dictionnary.Prompt.SoundDesigner,
            prompt={"storyboard": storyboard, "subtilte": subtitle},
            sys_custom=Utility.get_audio_list(
                music_folder=btoom.get_data_folder(Dictionnary.Data.Sound_Folder)
            ),
            output_path=btoom.get_log_folder(),
        )["sounddesign"]
        btoom.add(key=Dictionnary.Prompt.SoundDesigner, value=sounddesign)

    ##### IMG GEN

    if make_image:
        llm.ask_image(
            prompts=imagen,
            output_folder=btoom.get_img_folder(),
            quantity=image_quantity,
            select=select_image,
        )

    ##### PUBLISH

    publish = btoom.get(Dictionnary.Prompt.Publish)
    if not publish or make_publish:
        publish = llm.ask_json(
            sys=Dictionnary.Prompt.Publish,
            prompt=storyteller,
            output_path=btoom.get_log_folder(),
        )
        btoom.add(key=Dictionnary.Prompt.Publish, value=publish)
    #### VIDEO

    sound_mp3 = btoom.get(Dictionnary.OutputFile.Sound_mp3)
    if not Utility.check_file_exists(sound_mp3) or make_part:
        sound_mp3 = video.create_sound_design(
            sound_json=sounddesign,
            output_audio_path=btoom.get_language_folder(
                Dictionnary.OutputFile.Sound_mp3
            ),
            sound_folder=btoom.get_data_folder(Dictionnary.Data.Sound_Folder),
        )
        btoom.add(key=Dictionnary.OutputFile.Sound_mp3, value=sound_mp3)

    part_mp4 = btoom.get(Dictionnary.OutputFile.Part_mp4)
    if not Utility.check_file_exists(part_mp4) or make_part:
        part_mp4 = video.create_background_video(
            sync_data=imagesync,
            tts_path=tts_path,
            sound_path=sound_mp3,
            image_folder=btoom.get_img_folder(),
            intro_img_path=btoom.get_data_folder(Dictionnary.Data.Intro_img),
            outro_img_path=btoom.get_data_folder(Dictionnary.Data.Outro_img),
            outro_audio_path=btoom.get_data_folder(Dictionnary.Data.Outro_audio),
            music_path=btoom.get_data_folder(Dictionnary.Data.music),
            partial_video_path=btoom.get_language_folder(
                Dictionnary.OutputFile.Part_mp4
            ),
        )
        btoom.add(key=Dictionnary.OutputFile.Part_mp4, value=part_mp4)

    final_path = (
        btoom.get_root()
        / f"{base_language.value}_{Dictionnary.OutputFile.Final_mp4.value}"
    )
    if not Utility.check_file_exists(final_path) or make_video:
        final_path = video.add_sub_to_video(
            part_video_file=btoom.get(Dictionnary.OutputFile.Part_mp4),
            audio_file=btoom.get(Dictionnary.OutputFile.Audio_mp3),
            subtitle_file=btoom.get(Dictionnary.Prompt.Subschecker),
            final_path=final_path,
        )
        btoom.add(key=Dictionnary.OutputFile.Final_mp4, value=final_path)

    print(f"Finished in {round(time.time() - timer, 2)} seconds.")

    if make_languages:
        for language in other_languages:
            base = btoom.set_video(output_folder, language)

            ##### TEXT AND MP3 Generation
            tts_path = btoom.get(Dictionnary.OutputFile.Audio_mp3)
            if not Utility.check_file_exists(tts_path) or make_voice_storytelling:
                translated_storyteller = llm.ask_json(
                    sys=Dictionnary.Prompt.Translate,
                    prompt={f"Translate to {language.value} : {storyteller}"},
                    output_path=btoom.get_log_folder(),
                )
                tts_path = tts.generate_mp3(translated_storyteller)

            ##### SUBTITLE
            subtitle = btoom.get(Dictionnary.OutputFile.Audio_json)
            if not Utility.check_file_exists(subtitle) or make_sub:
                subtitle = tts.generate_subs(tts_path)
            else:
                with open(subtitle, "r", encoding="utf-8") as file:
                    subtitle = file.read()

            subcheck = btoom.get(Dictionnary.Prompt.Subschecker)
            if not Utility.check_file_exists(subcheck) or make_subcheck:
                subtitle = llm.ask_json(
                    sys=Dictionnary.Prompt.Subschecker,
                    prompt=f"story:{storyteller}\n\n\n{subtitle}",
                )
            else:
                with open(subcheck, "r", encoding="utf-8") as file:
                    subtitle = file.read()

            sync_path = btoom.get(Dictionnary.Prompt.ImageSync)
            if not Utility.check_file_exists(sync_path) or make_storyboard or make_sub:
                btoom.copy_file_from(
                    filename=Dictionnary.Prompt.ImageSync.value
                    + btoom.Prompt.Suffix.Result.value
                )

            part_mp4 = btoom.get(Dictionnary.OutputFile.Part_mp4)
            if not Utility.check_file_exists(part_mp4) or make_part:
                video.create_background_video()

            final_path = btoom.get_root_file_path(
                Dictionnary.OutputFile.Final_mp4, language
            )
            if not Utility.check_file_exists(final_path) or make_video:
                video.add_sub_to_video()


if mode:
    batch_path = Path(batch)
    for folder in batch_path.iterdir():
        if folder.is_dir():
            make(str(folder))
else:
    make(mono)
