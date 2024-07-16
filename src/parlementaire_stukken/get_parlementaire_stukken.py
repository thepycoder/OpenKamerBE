from collections import defaultdict
from functools import reduce
import json
import operator
import os
from bs4 import BeautifulSoup
from tqdm import tqdm

from common.io_utils import html_to_soup


def parse_html_to_nested_dict(soup: BeautifulSoup):
    key_stack = []
    nested_dict = defaultdict(lambda: defaultdict(dict))
    multi_fields = [
        "Auteur",
        "Auteurs",
        "Opvolgend(e) document(en)",
        "Eurovoc descriptoren",
        "Type",
        "Kalender",
        "Rapporteur",
        "Commissie",
        "Titel",
        "Staatsblad erratum",
        "Hoofddocument",
        "Hoodfdocument",
        "Incident",
        "Vrije trefwoorden",
        "Bevoegdheid",
        "Bevoegheid",
    ]

    for tr in soup.find_all("tr"):
        td_key, td_value = tr.find_all("td")

        # Extract the clean text from each <td>
        key_text = " ".join(td_key.get_text(strip=True).split())
        value_text = " ".join(td_value.get_text(strip=True).split())
        if key_text in multi_fields:
            value_text = [defaultdict(lambda: defaultdict(dict))]
        elif not value_text:
            value_text = {}

        # Calculate the level of nesting based on <img> tags
        images = td_key.find_all("img", class_="puce")
        level = len(images)

        # Correct the level when there are ints in the key_stack
        # They point to a list being used as a way to combine duplicate keys
        # like "auteur"
        limit = level + 1
        depth = 0
        indexes = 0
        for i in key_stack:
            if not isinstance(i, int):
                depth += 1
            else:
                indexes += 1
            if depth == limit:
                break
        if key_stack and indexes:
            level += indexes

        # If the current level is the same as the length of the stack
        # replace the latest key with the current key
        # e.g. [Kamer, Hoofdoc, BICAM] if the next one is Document Nr. it should
        # replace BICAM.
        # If the level is one more, just append it, we've made a new level
        # If the level is less, replace the corresponding key entry and all following ones
        if level == len(key_stack):
            # In case the key can occur multiple times, we turn it into a list instead.
            if key_stack and key_stack[-1] in multi_fields:
                key_stack.append(-1)
            key_stack.append(key_text)
        elif level == len(key_stack) + 1:
            key_stack.append(key_text)
        elif level < len(key_stack):
            key_stack = key_stack[:level] + [key_text]

        # Then use the keystack to set the correct key value pair in the dict
        if key_stack[-1] in reduce(operator.getitem, key_stack[:-1], nested_dict):
            reduce(operator.getitem, key_stack[:-1], nested_dict)[key_stack[-1]] += (
                value_text
            )
        else:
            reduce(operator.getitem, key_stack[:-1], nested_dict)[key_stack[-1]] = (
                value_text
            )
    return nested_dict


def main(html_dir: str = "html"):
    for i, filename in tqdm(enumerate(sorted(os.listdir(html_dir)))):
        # Check if the file is an HTML file
        if not filename.endswith(".html"):
            continue
        # Construct full file path
        file_path = os.path.join(html_dir, filename)
        # Turn the html file into a soup
        soup = html_to_soup(file_path=file_path)
        # Get the raw, nested dict from the html
        nested_document_metadata = parse_html_to_nested_dict(soup=soup)
        # Now map this dict onto objects for easier handling
        with open(
            f"src/parlementaire_stukken/json/{filename.replace('.html', '.json')}", "w"
        ) as fp:
            json.dump(nested_document_metadata, fp, indent=4)


if __name__ == "__main__":
    stukken = main(html_dir="src/parlementaire_stukken/html")
    # with open("votes.json", "w") as fp:
    #     # Use default=str to stringify everything that's not json serializable (like datetime)
    #     json.dump([v.to_dict() for v in votes.values()], fp, indent=4)
