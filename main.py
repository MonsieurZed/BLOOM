import time
from script.basic import *
from script.llm import LLM, Model
from script.sdxl import SDXL
from script.tts import TTS

quantity = 4
name = "25SEPT94"
story = """
On Halloween night, 1994, a student dressed as Dracula with a twist. He placed a pine plank under his T-shirt to create a spooky effect of being stabbed. But things took a fatal turn when he hammered the knife... <break time=\"1.0s\" /> The blade cut through the plank and into his heart. He stumbled into the party, said *<u>\"I really did it\"</u>*, and collapsed before his horrified friends."""

prompt = """An ominous backroom corridor, enveloped in a harsh yellow glow from flickering fluorescent lights. The walls are stark and uniform, amplifying the sense of isolation and vulnerability in this disorienting space."""

Folder_check()


#################
def main():
    output_folder = f"_output/{time.strftime('%m%d-%H%M')}"

    Llm = LLM(Model.Gemini_2Flash, output_folder, log=True)
    Tts = TTS(output_folder)
    Sdxl = SDXL(output_folder)

    story = Llm.ask(
        sys="storyteller",
        user=story,
    )

    mp3 = Tts.generate_mp3_from_json(story)
    print(mp3)
    subs = Tts.generate_subs(mp3)

    storyboard = Llm.ask(
        sys="storyboard",
        user=story,
    )

    prompt = Llm.ask(
        sys="sdxl",
        user=f"For each scene make 3 iteration prompt in the style of a dark :\n {storyboard}",
    )

    sync = Llm.ask(
        sys="sync",
        user=f"srt={subs}\n\nstoryboard={storyboard}",
    )

    Sdxl.generate_from_json(prompt, quantity=1)


def short():
    output_folder = "_output\lastfull"
    mp3_path = f"{output_folder}/audio.mp3"
    sub_path = f"{output_folder}/audio.srt"
    Sdxl = SDXL(output_folder)
    Llm = LLM(Model.Gemini_2Flash, output_folder, log=True)
    # Tts = TTS(output_folder)
    # subs = Tts.generate_subs(mp3_path)

    storyboard = Llm.ask(
        sys="storyboard",
        user=f"Number of scene needed :{round(Utility.get_duration(mp3_path)/5)}  \n Story : {story}",
    )

    prompt = Llm.ask(
        sys="sdxl",
        user=f"For each scene make 2 iteration prompt in the style of a dark polar :\n {storyboard}",
    )

    sync = Llm.ask(
        sys="sync",
        user=f"srt={sub_path}\n\nstoryboard={storyboard}",
    )

    Sdxl.generate_from_json(prompt, style=SDXL.Style.Realistic, quantity=2)


def imgen():
    output_folder = "_output\\imgen"
    Sdxl = SDXL(output_folder)
    llm = LLM(Model.Gemini_2Flash, output_folder, log=True)

    prompt = llm.ask(
        sys="sdxl",
        user="3 iterations : Un motard avec une veste en cuir marron, un casque noir et une moto africa twin noir",
    )

    Sdxl.generate_from_json(prompt, quantity=3)


# imgen()
short()
