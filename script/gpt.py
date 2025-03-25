from openai import OpenAI
import yaml
import os

with open("conf/key.yml", "r") as file:
    key = yaml.safe_load(file)
with open("conf/gpt.yml", "r", encoding="utf-8") as file:
    gpt = yaml.safe_load(file)


def generate_scripts(name, story):

    folder_path = f"_output/{name}"
    try:
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")
    except OSError as error:
        print(f"Error creating folder: {error}")

    client = OpenAI(api_key=key["openai"]["api_key"])

    conversation_history = [
        {"role": "system", "content": gpt["prompt"]["base"]},
        {
            "role": "user",
            "content": f"Voici l'histoire à transformer en script : {story}",
        },
    ]

    print("Generating script...")

    completion = client.chat.completions.create(
        model=gpt["model"], store=True, messages=conversation_history
    )

    with open(f"_output/{name}/1_base.txt", "w", encoding="utf-8") as f:
        f.write(completion.choices[0].message.content)

    print("Script generated.")

    ####################################################

    assistant_message = completion.choices[0].message
    conversation_history.append(
        {"role": "assistant", "content": assistant_message.content}
    )
    conversation_history.append(
        {
            "role": "user",
            "content": gpt["prompt"]["json"],
        }
    )

    completion = client.chat.completions.create(
        model=gpt["model"], store=True, messages=conversation_history
    )

    with open(f"_output/{name}/2_prompt.json", "w", encoding="utf-8") as f:
        f.write(completion.choices[0].message.content)

    print("Prompt generated.")

    ########################################################

    assistant_message = completion.choices[0].message
    conversation_history.append(
        {"role": "assistant", "content": assistant_message.content}
    )
    conversation_history.append(
        {
            "role": "user",
            "content": gpt["prompt"]["tts"],
        }
    )

    completion = client.chat.completions.create(
        model=gpt["model"], store=True, messages=conversation_history
    )

    with open(f"_output/{name}/3_TTS.txt", "w", encoding="utf-8") as f:
        f.write(completion.choices[0].message.content)

    print("TTS generated.")
