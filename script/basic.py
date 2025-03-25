import os
import yaml


def checks():
    print("Checking...")
    folder_path = f"_output"
    try:
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")
    except OSError as error:
        print(f"Error creating folder: {error}")
