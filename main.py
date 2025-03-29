import time
from script.basic import *
from script.llm import LLM, Model, Prompt
from script.sdxl import SDXL
from script.tts import TTS

quantity = 4
name = "25SEPT94"
story = """Paul Stiller et sa femme sont morts à Andover Township, par un bâton de dynamite qui a explosé dans leur voiture : s’ennuyant à bord de leur voiture à deux heures du matin, ils ont voulu allumer un bâton de dynamite et le jeter par la fenêtre pour voir ce que ça faisait, mais apparemment n’ont pas remarqué que les vitres étaient fermées quand ils ont lancé le bâton."""

prompt = """An ominous backroom corridor, enveloped in a harsh yellow glow from flickering fluorescent lights. The walls are stark and uniform, amplifying the sense of isolation and vulnerability in this disorienting space."""
timer = time.time()
Folder_check()


#################
def main():
    output_folder = f"_output/{time.strftime('%m%d-%H%M')}"

    Llm = LLM(Model.Gemini_2Flash, output_folder, log=True)
    Tts = TTS(output_folder)
    Sdxl = SDXL(output_folder)

    story = Llm.ask(
        sys=Prompt.System.Storyteller,
        prompt=story,
    )

    mp3 = Tts.generate_mp3(story)
    subs = Tts.generate_subs(mp3)

    storyboard = Llm.ask(
        sys=Prompt.System.Storyboard,
        prompt=story,
    )

    prompt = Llm.ask(
        sys=Prompt.System.SDXL,
        prompt=f"For each scene make 3 iteration prompt in the style of a dark :\n {storyboard}",
    )

    sync = Llm.ask(
        sys=Prompt.System.Sync,
        prompt=f"srt={subs}\n\nstoryboard={storyboard}",
    )

    Sdxl.generate_from_json(prompt, quantity=1)


def short():
    output_folder = "_output\zzz"
    mp3_path = f"{output_folder}/audio.mp3"
    sub_path = f"{output_folder}/audio.srt"
    Sdxl = SDXL(output_folder)
    Llm = LLM(Model.Gemini_2Flash, output_folder, log=True)
    # Tts = TTS(output_folder)
    # subs = Tts.generate_subs(mp3_path)

    storyboard = Llm.ask(
        sys=Prompt.System.Storyboard,
        #  prompt=f"Number of scene needed :{round(Utility.get_duration(mp3_path)/5)}  \n Story : {story}",
        prompt=f"""
        Number of scene needed : 5
        Story : {story}""",
    )

    prompt = Llm.ask(
        sys=Prompt.System.SDXL,
        prompt=f"""
        Style: Photorealistic
        Mood : Suspense
        Iteration quantity : 3
        Storyboard : {storyboard}""",
    )

    # sync = Llm.ask(
    #     sys=Prompt.System.Sync,
    #     prompt=f"srt={sub_path}\n\nstoryboard={storyboard}",
    # )

    Sdxl.generate_from_json(
        prompt, style=SDXL.Style.Anime, mood=SDXL.Mood.Suspense, quantity=2
    )


def imgen():
    output_folder = "_output\\imgen"
    llm = LLM(Model.Gemini_2Flash, output_folder, log=True)
    Sdxl = SDXL(output_folder)

    prompt = llm.ask(
        sys=Prompt.System.SDXL,
        prompt="1 iterations : Un motard faisant du camping avec une veste en cuir marron, un casque noir et une moto africa twin noir",
    )

    Sdxl.generate_from_json(
        prompt, style=SDXL.Style.Realistic, mood=SDXL.Mood.Suspense, quantity=3
    )


def retry():
    output_folder = "_output\\imgen"
    Sdxl = SDXL(output_folder)

    with open("_output\lastfull\sdxl", "r", encoding="utf-8") as file:
        prompt = file.read()
    Sdxl.generate_from_json(
        prompt, style=SDXL.Style.Anime, mood=SDXL.Mood.Horror, quantity=3
    )


# imgen()
short()
# retry()

print(f"Total time {round(time.time() - timer, 2)}sec")
