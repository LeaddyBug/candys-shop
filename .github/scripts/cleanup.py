import json
import os
from urllib.parse import unquote

MAPPING_FILE = "mapping.json"
PREVIEWS_DIR = "previews"

# Load mapping.json
with open(MAPPING_FILE, "r") as f:
    data = json.load(f)

unique_dict = []
for item in data:
    contains = False
    for unique_item in unique_dict:
        if unique_item["Game"] == item["Game"]:
            if unique_item["Song"] == item["Song"]:
                contains = True
                unique_item["Audio"] = item.get("Audio", "")
    if not contains:
        temp = {
            "Game": item["Game"],
            "Song": item["Song"],
        }
        if "Audio" in item:
            temp["Audio"] = item["Audio"]
        unique_dict.append(temp)

# Push to mapping that it the link has been pruned
for item in data:
    for unique_item in unique_dict:
        if unique_item["Game"] != item["Game"]:
            continue
        if unique_item["Song"] != item["Song"]:
            continue
        audio = item.get("Audio", "")
        if unique_item["Audio"] == audio:
            continue
        if isinstance(audio, str) and "github.com" in audio:
            item["pruned"] = True

with open(MAPPING_FILE, "w") as f:
    json.dump(data, f, indent=2)

# Step 5: Cleanup unused preview files
used_audio_files = []
for x in unique_dict:
    audio = x["Audio"]
    if isinstance(audio, str) and "github.com" in audio:
        file = unquote(audio.split("raw/main/")[1])
        # print("Unique File", file)
        used_audio_files.append(file)

# Remove unused files in previews/
cleaned_files =  0
for root, _, files in os.walk(PREVIEWS_DIR):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, ".")
        # print("Test Path", rel_path)
        if rel_path not in used_audio_files:
            print(f"Removing unused preview file: {rel_path}")
            cleaned_files += 1
            os.remove(full_path)
print(f"Cleaned {cleaned_files} files")
