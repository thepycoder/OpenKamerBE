import os
import json
from collections import defaultdict


def process_json_files(folder_path):
    # Dictionaries to count occurrences
    auteurs_count = defaultdict(int)
    partij_count = defaultdict(int)
    hoofddescriptor_count = defaultdict(int)

    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                # Get the 'Hoofddocument' section
                hoofddocument = data["Kamer en/of Senaat"]["Hoofddocument"]

                # Extract the 'Auteur' and their 'Partij'
                try:
                    auteur = hoofddocument["Auteur"]["Naam"]
                    partij = hoofddocument["Auteur"]["Partij"]
                except KeyError:
                    auteur = "None"
                    partij = "None"

                # Update counts for 'auteur' and 'partij'
                auteurs_count[auteur] += 1
                partij_count[partij] += 1

                # Extract the 'Eurovoc-hoofddescriptor' in 'NL'
                try:
                    hoofddescriptor = data["Descriptoren, trefwoorden"][
                        "Eurovoc-hoofddescriptor"
                    ]["NL"]
                except KeyError:
                    hoofddescriptor = "None"

                # Update count for 'hoofddescriptor'
                hoofddescriptor_count[hoofddescriptor] += 1

    # Sort the dictionaries by count
    sorted_auteurs = sorted(
        auteurs_count.items(), key=lambda item: item[1], reverse=True
    )
    sorted_partijen = sorted(
        partij_count.items(), key=lambda item: item[1], reverse=True
    )
    sorted_hoofddescriptors = sorted(
        hoofddescriptor_count.items(), key=lambda item: item[1], reverse=True
    )

    return sorted_auteurs, sorted_partijen, sorted_hoofddescriptors


# Assuming the folder path where JSON files are stored
folder_path = "stukken"

# Process the files and retrieve counts
auteurs_count, partij_count, hoofddescriptor_count = process_json_files(folder_path)

# Display the results (this code won't execute here, it's for you to run locally)
print("Auteurs Count:", auteurs_count)
print("Partij Count:", partij_count)
print("Hoofddescriptor Count:", hoofddescriptor_count)
