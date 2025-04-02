import time

from moviepy.editor import TextClip
from script.basic import *
from script.bloom import Bloom
from script.llm import LLMGen, PromptLoader
from _old.sdxl import SDXL
from script.tts import TTSGen
from script.video import VideoGen

img = False
Llm = LLMGen(Bloom.Model.Gemini_2Flash, "_output", log=True)

if img:
    text = TextClip.list("font")
    font_list_file_path = r"D:\GIT\BLOOM\BLOOM\font_list.txt"
    with open(font_list_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(text))

    with open(r"D:\GIT\BLOOM\BLOOM\data\stories.json", "r", encoding="utf-8") as file:
        jsonfile = file.read()

    storyboard = {
        "scene": [
            {
                "scene": "1",
                "description": "Un homme poignardé qui tient un panneau : J'ai faim",
            },
            # {
            #     "scene": "1",
            #     "description": "un couple en voiture",
            # },
            # {
            #     "scene": "1",
            #     "description": "Student dressed as Dracula mort au millieu d'une piece",
            # },
        ]
    }

    image_style = "A nostalgic 90s-style photograph taken with a disposable camera"
    image_mood = "Suspense"
    image_iteration = 2

    jsontxt = Llm.ask(
        sys=PromptLoader.System.SDXL,
        prompt=f"Style:'{image_style}'\nMood : {image_mood}\nIteration quantity : {image_iteration}\nStoryboard : {storyboard}",
    )

    txt = Utility.json_from_str(jsontxt)

    Llm.quick_image(txt["prompts"][0]["prompt"])
    # Llm.quick_image(txt["prompts"][1]["prompt"])
    # Llm.quick_image(txt["prompts"][2]["prompt"])

else:

    subs = {
        "asr": [
            {
                "text": "Darwin Award, 09 Avril 2003, Nouvelle-Zélande.",
                "start": 0.0,
                "end": 3.84,
                "words": [
                    {"word": "Darwin", "start": 0.0, "end": 0.44},
                    {"word": "Award,", "start": 0.44, "end": 0.8},
                    {"word": "09", "start": 1.18, "end": 1.58},
                    {"word": "Avril", "start": 1.58, "end": 2.02},
                    {"word": "2003,", "start": 2.02, "end": 2.82},
                    {"word": "Nouvelle-Zélande.", "start": 3.22, "end": 3.84},
                ],
            },
            {
                "text": "Phil, a safety officer at a food processing plant, found himself in a familiar predicament.",
                "start": 4.68,
                "end": 9.48,
                "words": [
                    {"word": "Phil,", "start": 4.68, "end": 4.99},
                    {"word": "a", "start": 5.3, "end": 5.54},
                    {"word": "safety", "start": 5.54, "end": 5.8},
                    {"word": "officer", "start": 5.8, "end": 6.26},
                    {"word": "at", "start": 6.26, "end": 6.42},
                    {"word": "a", "start": 6.42, "end": 6.48},
                    {"word": "food", "start": 6.48, "end": 6.66},
                    {"word": "processing", "start": 6.66, "end": 7.1},
                    {"word": "plant,", "start": 7.1, "end": 7.5},
                    {"word": "found", "start": 7.76, "end": 7.94},
                    {"word": "himself", "start": 7.94, "end": 8.28},
                    {"word": "in", "start": 8.28, "end": 8.47},
                    {"word": "a", "start": 8.47, "end": 8.54},
                    {"word": "familiar", "start": 8.54, "end": 8.92},
                    {"word": "predicament.", "start": 8.92, "end": 9.48},
                ],
            },
            {
                "text": "His car needed repairs, but lifting it with a jack didn't provide enough space.",
                "start": 10.04,
                "end": 14.0,
                "words": [
                    {"word": "His", "start": 10.04, "end": 10.23},
                    {"word": "car", "start": 10.23, "end": 10.44},
                    {"word": "needed", "start": 10.44, "end": 10.7},
                    {"word": "repairs,", "start": 10.7, "end": 11.06},
                    {"word": "but", "start": 11.76, "end": 11.92},
                    {"word": "lifting", "start": 11.92, "end": 12.18},
                    {"word": "it", "start": 12.18, "end": 12.34},
                    {"word": "with", "start": 12.34, "end": 12.5},
                    {"word": "a", "start": 12.5, "end": 12.58},
                    {"word": "jack", "start": 12.58, "end": 12.78},
                    {"word": "didn't", "start": 12.78, "end": 13.16},
                    {"word": "provide", "start": 13.16, "end": 13.42},
                    {"word": "enough", "start": 13.42, "end": 13.66},
                    {"word": "space.", "start": 13.66, "end": 14.0},
                ],
            },
            {
                "text": "Thinking quickly, he removed the car battery, placing it under the jack for extra height.",
                "start": 14.88,
                "end": 19.14,
                "words": [
                    {"word": "Thinking", "start": 14.88, "end": 15.22},
                    {"word": "quickly,", "start": 15.22, "end": 15.66},
                    {"word": "he", "start": 15.94, "end": 16.02},
                    {"word": "removed", "start": 16.02, "end": 16.22},
                    {"word": "the", "start": 16.22, "end": 16.52},
                    {"word": "car", "start": 16.52, "end": 16.66},
                    {"word": "battery,", "start": 16.66, "end": 17.0},
                    {"word": "placing", "start": 17.4, "end": 17.64},
                    {"word": "it", "start": 17.64, "end": 17.8},
                    {"word": "under", "start": 17.8, "end": 17.9},
                    {"word": "the", "start": 17.9, "end": 18.06},
                    {"word": "jack", "start": 18.06, "end": 18.27},
                    {"word": "for", "start": 18.27, "end": 18.52},
                    {"word": "extra", "start": 18.52, "end": 18.84},
                    {"word": "height.", "start": 18.84, "end": 19.14},
                ],
            },
            {
                "text": "As he worked more comfortably, a sickening crack echoed.",
                "start": 19.62,
                "end": 22.46,
                "words": [
                    {"word": "As", "start": 19.62, "end": 19.84},
                    {"word": "he", "start": 19.84, "end": 19.95},
                    {"word": "worked", "start": 19.95, "end": 20.18},
                    {"word": "more", "start": 20.18, "end": 20.38},
                    {"word": "comfortably,", "start": 20.38, "end": 20.84},
                    {"word": "a", "start": 21.18, "end": 21.24},
                    {"word": "sickening", "start": 21.24, "end": 21.68},
                    {"word": "crack", "start": 21.68, "end": 21.9},
                    {"word": "echoed.", "start": 21.9, "end": 22.46},
                ],
            },
            {
                "text": "The battery couldn't bear the weight.",
                "start": 22.74,
                "end": 24.1,
                "words": [
                    {"word": "The", "start": 22.74, "end": 22.84},
                    {"word": "battery", "start": 22.84, "end": 23.16},
                    {"word": "couldn't", "start": 23.16, "end": 23.52},
                    {"word": "bear", "start": 23.52, "end": 23.7},
                    {"word": "the", "start": 23.7, "end": 23.9},
                    {"word": "weight.", "start": 23.9, "end": 24.1},
                ],
            },
            {
                "text": "The jack collapsed, pinning Phil beneath the vehicle.",
                "start": 24.68,
                "end": 27.18,
                "words": [
                    {"word": "The", "start": 24.68, "end": 24.84},
                    {"word": "jack", "start": 24.84, "end": 25.08},
                    {"word": "collapsed,", "start": 25.08, "end": 25.7},
                    {"word": "pinning", "start": 26.0, "end": 26.16},
                    {"word": "Phil", "start": 26.16, "end": 26.42},
                    {"word": "beneath", "start": 26.42, "end": 26.66},
                    {"word": "the", "start": 26.66, "end": 26.84},
                    {"word": "vehicle.", "start": 26.84, "end": 27.18},
                ],
            },
            {
                "text": "The pressure on his chest was unbearable, stealing his breath, trapped and helpless.",
                "start": 27.18,
                "end": 33.62,
                "words": [
                    {"word": "The", "start": 27.18, "end": 27.82},
                    {"word": "pressure", "start": 27.82, "end": 28.18},
                    {"word": "on", "start": 28.18, "end": 28.36},
                    {"word": "his", "start": 28.36, "end": 28.5},
                    {"word": "chest", "start": 28.5, "end": 28.74},
                    {"word": "was", "start": 28.74, "end": 28.98},
                    {"word": "unbearable,", "start": 28.98, "end": 29.58},
                    {"word": "stealing", "start": 30.12, "end": 30.66},
                    {"word": "his", "start": 30.66, "end": 31.24},
                    {"word": "breath,", "start": 31.24, "end": 31.6},
                    {"word": "trapped", "start": 32.32, "end": 32.85},
                    {"word": "and", "start": 32.85, "end": 33.22},
                    {"word": "helpless.", "start": 33.22, "end": 33.62},
                ],
            },
            {
                "text": "He died in a pool of battery acid.",
                "start": 34.28,
                "end": 36.18,
                "words": [
                    {"word": "He", "start": 34.28, "end": 34.48},
                    {"word": "died", "start": 34.48, "end": 34.78},
                    {"word": "in", "start": 34.78, "end": 34.94},
                    {"word": "a", "start": 34.94, "end": 35.03},
                    {"word": "pool", "start": 35.03, "end": 35.28},
                    {"word": "of", "start": 35.28, "end": 35.5},
                    {"word": "battery", "start": 35.5, "end": 35.82},
                    {"word": "acid.", "start": 35.82, "end": 36.18},
                ],
            },
            {
                "text": "Tragically, this wasn't Phil's first brush with such an accident.",
                "start": 36.86,
                "end": 40.08,
                "words": [
                    {"word": "Tragically,", "start": 36.86, "end": 37.32},
                    {"word": "this", "start": 37.72, "end": 37.86},
                    {"word": "wasn't", "start": 37.86, "end": 38.21},
                    {"word": "Phil's", "start": 38.21, "end": 38.53},
                    {"word": "first", "start": 38.53, "end": 38.8},
                    {"word": "brush", "start": 38.8, "end": 39.08},
                    {"word": "with", "start": 39.08, "end": 39.28},
                    {"word": "such", "start": 39.28, "end": 39.53},
                    {"word": "an", "start": 39.53, "end": 39.64},
                    {"word": "accident.", "start": 39.64, "end": 40.08},
                ],
            },
            {
                "text": "A decade earlier, he'd been pinned under a car, escaping with just a broken leg.",
                "start": 40.66,
                "end": 44.84,
                "words": [
                    {"word": "A", "start": 40.66, "end": 40.76},
                    {"word": "decade", "start": 40.76, "end": 41.02},
                    {"word": "earlier,", "start": 41.02, "end": 41.52},
                    {"word": "he'd", "start": 41.88, "end": 42.02},
                    {"word": "been", "start": 42.02, "end": 42.1},
                    {"word": "pinned", "start": 42.1, "end": 42.34},
                    {"word": "under", "start": 42.34, "end": 42.6},
                    {"word": "a", "start": 42.6, "end": 42.76},
                    {"word": "car,", "start": 42.76, "end": 43.0},
                    {"word": "escaping", "start": 43.42, "end": 43.74},
                    {"word": "with", "start": 43.74, "end": 43.96},
                    {"word": "just", "start": 43.96, "end": 44.12},
                    {"word": "a", "start": 44.12, "end": 44.3},
                    {"word": "broken", "start": 44.3, "end": 44.56},
                    {"word": "leg.", "start": 44.56, "end": 44.84},
                ],
            },
            {
                "text": "Some, it seems, never learn, even from their own mistakes.",
                "start": 45.44,
                "end": 49.58,
                "words": [
                    {"word": "Some,", "start": 45.44, "end": 45.72},
                    {"word": "it", "start": 46.04, "end": 46.34},
                    {"word": "seems,", "start": 46.34, "end": 46.68},
                    {"word": "never", "start": 47.2, "end": 47.42},
                    {"word": "learn,", "start": 47.42, "end": 47.74},
                    {"word": "even", "start": 48.3, "end": 48.56},
                    {"word": "from", "start": 48.56, "end": 48.78},
                    {"word": "their", "start": 48.78, "end": 48.96},
                    {"word": "own", "start": 48.96, "end": 49.2},
                    {"word": "mistakes.", "start": 49.2, "end": 49.58},
                ],
            },
            {
                "text": "Bloom.",
                "start": 50.3,
                "end": 50.46,
                "words": [{"word": "Bloom.", "start": 50.3, "end": 50.46}],
            },
        ]
    }

    story = {
        "id": 3,
        "date": "09 Avril 2003",
        "place": "Nouvelle-Zélande",
        "story": "Phil, a safety officer at a food processing plant, found himself in a familiar predicament. His car needed repairs, but lifting it with a jack didn't provide enough space.Thinking quickly, he removed the car battery, placing it under the jack for extra height. As he worked more comfortably, a sickening crack echoed—the battery couldn't bear the weight.The jack collapsed, pinning Phil beneath the vehicle. The pressure on his chest was unbearable, stealing his breath. Trapped and helpless, he died in a pool of battery acid.Tragically, this wasn't Phil's first brush with such an accident. A decade earlier, he'd been pinned under a car, escaping with just a broken leg. Some, it seems, never learn, even from their own mistakes.",
    }

    jsontxt = Llm.quick_ask(
        sys=Bloom.Prompt.System.SoundDesigner,
        prompt=f"{story} {subs}",
        output_path=r"D:\GIT\BLOOM\BLOOM",
    )
    print(jsontxt)
