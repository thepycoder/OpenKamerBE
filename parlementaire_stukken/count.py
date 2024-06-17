import os
import json
from collections import defaultdict


descriptor_lookup = {
    "STRAFRECHT": "Recht en Wetgeving",
    "STRAFPROCEDURE": "Recht en Wetgeving",
    "STRAFGEVANGENIS": "Recht en Wetgeving",
    "BURGERLIJK RECHT": "Recht en Wetgeving",
    "BURGERLIJKE RECHTSVORDERING": "Recht en Wetgeving",
    "ARBEIDSRECHT": "Recht en Wetgeving",
    "WERKLOOSHEIDSVERZEKERING": "Recht en Wetgeving",
    "OUDERVERLOF": "Recht en Wetgeving",
    "FISCAAL RECHT": "Recht en Wetgeving",
    "DIRECTE BELASTING": "Recht en Wetgeving",
    "BTW": "Recht en Wetgeving",
    "HERZIENING VAN DE GRONDWET": "Recht en Wetgeving",
    "CONSTITUTIONELE RECHTSPRAAK": "Recht en Wetgeving",
    "EUROPESE UNIE": "Recht en Wetgeving",
    "EUROPESE RAAD": "Recht en Wetgeving",
    "EUROPEES PARLEMENT": "Recht en Wetgeving",
    "MIGRATIEBELEID": "Recht en Wetgeving",
    "VREEMDELINGENRECHT": "Recht en Wetgeving",
    "ASIELRECHT": "Recht en Wetgeving",
    "ECONOMISCH BELEID": "Overheidsbeleid en -administratie",
    "BELASTINGBELEID": "Overheidsbeleid en -administratie",
    "MONETAIR BELEID": "Overheidsbeleid en -administratie",
    "SOCIAAL BELEID": "Overheidsbeleid en -administratie",
    "SOCIALE ZEKERHEID": "Overheidsbeleid en -administratie",
    "SOCIALE BIJSTAND": "Overheidsbeleid en -administratie",
    "VOLKSGEZONDHEID": "Overheidsbeleid en -administratie",
    "GEZONDHEIDSBELEID": "Overheidsbeleid en -administratie",
    "ZIEKTEVERZEKERING": "Overheidsbeleid en -administratie",
    "DEFENSIEBELEID": "Overheidsbeleid en -administratie",
    "OPENBARE VEILIGHEID": "Overheidsbeleid en -administratie",
    "NATIONALE VEILIGHEID": "Overheidsbeleid en -administratie",
    "MILIEUBESCHERMING": "Overheidsbeleid en -administratie",
    "MILIEUBELEID": "Overheidsbeleid en -administratie",
    "DUURZAME ONTWIKKELING": "Overheidsbeleid en -administratie",
    "RECHTEN VAN DE MENS": "Maatschappelijke Kwesties",
    "BESTRIJDING VAN DISCRIMINATIE": "Maatschappelijke Kwesties",
    "GELIJKE BEHANDELING VAN MAN EN VROUW": "Maatschappelijke Kwesties",
    "GEESTELIJKE GEZONDHEID": "Maatschappelijke Kwesties",
    "GEHANDICAPTE": "Maatschappelijke Kwesties",
    "GEZONDHEIDSZORG": "Maatschappelijke Kwesties",
    "TAALGEBRUIK": "Maatschappelijke Kwesties",
    "ONDERWIJS": "Maatschappelijke Kwesties",
    "CULTUUR": "Maatschappelijke Kwesties",
    "BESCHERMING VAN DE CONSUMENT": "Maatschappelijke Kwesties",
    "VERKEERSVEILIGHEID": "Maatschappelijke Kwesties",
    "VOEDSELVEILIGHEID": "Maatschappelijke Kwesties",
}


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
                hoofddocument = data["Kamer en/of Senaat"]["Hoofddocument"][-1]

                # Extract the 'Auteur' and their 'Partij'
                partijen = set()
                try:
                    for auteur in hoofddocument["Auteur"]:
                        auteurs_count[auteur["Naam"]] += 1
                        partijen.add(auteur["Partij"])
                except KeyError:
                    auteurs_count["None"] += 1
                    partijen = set(["None"])

                # Update counts for 'partij'
                for partij in partijen:
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
folder_path = "parlementaire_stukken/json"

# Process the files and retrieve counts
auteurs_count, partij_count, hoofddescriptor_count = process_json_files(folder_path)

# Display the results (this code won't execute here, it's for you to run locally)
print("Auteurs Count:", auteurs_count)
print("Partij Count:", partij_count)
print("Hoofddescriptor Count:", hoofddescriptor_count)
