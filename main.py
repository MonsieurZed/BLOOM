import time
from script.basic import *
from script.llm import LLMGen, Model, PromptLoader
from _old.sdxl import SDXL
from script.tts import TTSGen
from script.video import VideoGen

# json_file_path = r"D:\GIT\BLOOM\BLOOM\_generative\11 Mai 1997_USA, Los Angeles"
json_file_path = r"D:\GIT\BLOOM\BLOOM\_generative\25 Septembre 1994_Unknown location"
gen_folder = "_generative"

with open(json_file_path + "\\base.json", "r", encoding="utf-8") as file:
    base = json.load(file)

date = base.get("date", "Unknown Date")
place = base.get("place", "Unknown Location")
story_text = base.get("story", "No Story Provided")

output_folder = f"{gen_folder}\{date.replace(' ', '')}_{place.replace(' ', '')}"
Utility.make_folder(output_folder)

make_voice = False
make_sub = False
make_storyboard = False
make_sdxl = True
make_image = True
select_image = True
make_background = False
make_video = False
make_publish = False

title = f"Darwin Award, {date}, {place}"
number_of_scene = 7
image_style = "faded film, desaturated, grainy, vignette, vintage"
image_mood = "Suspense"
image_iteration = 2


Llm = LLMGen(Model.Gemini_2Flash, output_folder, log=True)
Tts = TTSGen(output_folder)
Sdxl = SDXL(output_folder)
video = VideoGen(output_folder)

timer = time.time()
print(f"Generating {output_folder} ...")

if make_voice:
    storyteller = Llm.ask(
        sys=PromptLoader.System.Storyteller,
        prompt=story_text,
    )

    mp3 = Tts.generate_mp3(title + " " + storyteller + "<break time='2s'/> BLOOM!'")
else:
    mp3 = output_folder + "\\audio.mp3"

if make_sub:
    subs = Tts.generate_srt(mp3)
else:
    with open(f"{output_folder}\\audio.srt", "r", encoding="utf-8") as file:
        subs = file.read()

if make_storyboard:
    storyboard = Llm.ask(
        sys=PromptLoader.System.Storyboard,
        prompt=f"Number of scene needed : {number_of_scene}\nStory : {base}",
    )
else:
    with open(f"{output_folder}\\storyboard_result", "r", encoding="utf-8") as file:
        storyboard = Utility.json_from_str(file.read())

if make_sdxl:
    prompt = Llm.ask(
        sys=PromptLoader.System.SDXL,
        prompt=f"Style:'{image_style}'\nMood : {image_mood}\nIteration quantity : {image_iteration}\nStoryboard : {storyboard}",
    )
if make_storyboard or make_sub:
    sync = Llm.ask(
        sys=PromptLoader.System.Sync,
        prompt=f"Storyboard:\n{storyboard}\n\n\nSubtilte :\n{subs}",
    )

if make_image:
    Llm.ask_image(quantity=1, select=select_image)

if make_background:
    video.create_background_video()

if make_video:
    video.add_sub_to_video()

if make_publish:
    publish = Llm.ask(
        sys=PromptLoader.System.Publish,
        prompt=base,
    )

print(f"Finished in {round(time.time() - timer, 2)} seconds.")
