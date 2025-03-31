import json


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

    for raw_story in raw_stories:
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

        # Split the first line into date and location
        date, *lieu_parts = first_line.split(",", 1)
        lieu = lieu_parts[0].strip() if lieu_parts else ""

        # Add the parsed story to the list
        stories.append({"date": date.strip(), "place": lieu, "story": story_content})

    # Save the stories as a JSON file
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(stories, json_file, ensure_ascii=False, indent=4)

    print(f"Stories successfully converted to JSON and saved to {output_path}")


# Example usage
input_file = r"d:\GIT\BLOOM\BLOOM\data\stories-horror.txt"
output_file = r"d:\GIT\BLOOM\BLOOM\data\stories-horror.json"
parse_stories(input_file, output_file)
