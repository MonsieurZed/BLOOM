import json
import random
from basic import Utility


def parse_stories(file_path, output_path):
    """
    Parse the stories from the text file and convert them into JSON format.
    :param file_path: Path to the input text file.
    :param output_path: Path to save the output JSON file.
    """
    stories = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split the content into individual stories using "---" as a separator
    raw_stories = content.split("---")
    random.shuffle(raw_stories)
    for id, raw_story in enumerate(raw_stories):
        raw_story = raw_story.strip()
        if not raw_story:
            continue

        # Extract the first line (date and location) and the rest as the story
        lines = raw_story.split("\n", 1)
        if len(lines) < 2:
            continue

        # Extract date and location from the first line
        first_line = lines[0].strip()
        story_content = lines[1].strip()

        # Ignore the story if the content is empty
        if not story_content:
            continue

        # Split the first line into date and location
        date, *lieu_parts = first_line.split(",", 1)
        date = date.strip() if date.strip() else "unknown date"  # Handle empty date
        lieu = (
            lieu_parts[0].strip() if lieu_parts else "Unknown location"
        )  # Handle empty location

        # Add the parsed story to the list
        stories.append({"id": id, "date": date, "place": lieu, "story": story_content})

    # Save the stories as a JSON file
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(stories, json_file, ensure_ascii=False, indent=4)

    print(f"Stories successfully converted to JSON and saved to {output_path}")


def generate_batches_with_folders(file_path, folder_path, batch_size=7):
    """
    Generate batches of stories and save them into structured folders.
    :param file_path: Path to the JSON file containing stories.
    :param folder_path: Path to the folder where batches will be created.
    :param batch_size: Number of stories per batch.
    """
    total = 0
    with open(file_path, "r", encoding="utf-8") as json_file:
        stories = json.load(json_file)

    Utility.make_folder(folder_path)

    # Iterate over the stories in batches
    for i in range(0, len(stories), batch_size):
        batch = stories[i : i + batch_size]
        batch_folder = f"{folder_path}/batch_{i // batch_size}"
        Utility.make_folder(batch_folder)

        for j, story in enumerate(batch):
            # Format the folder name for each story
            story_folder_name = f"{j}_{story['date'].replace(' ', '.')}_{story['place'].replace(' ', '.')}"
            story_folder_path = f"{batch_folder}/{story_folder_name}"
            Utility.make_folder(story_folder_path)

            # Save the story in a base.json file
            story_file_path = f"{story_folder_path}/base.json"
            with open(story_file_path, "w", encoding="utf-8") as story_file:
                json.dump(story, story_file, ensure_ascii=False, indent=4)
            total += 1

        print(f"Batch {i // batch_size + 1} created at {batch_folder}")

    print(f"Total story generated : {total}")


# Example usage
input_file = r"d:\GIT\BLOOM\BLOOM\data\stories.txt"
output_file = r"d:\GIT\BLOOM\BLOOM\data\stories.json"
working_folder = r"d:\GIT\BLOOM\BLOOM\_output"
parse_stories(input_file, output_file)
generate_batches_with_folders(output_file, working_folder)
