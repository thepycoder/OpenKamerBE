from collections import defaultdict
from functools import reduce
import json
import operator
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm


def parse_html_to_nested_dict(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    key_stack = []
    nested_dict = defaultdict(lambda: defaultdict(dict))
    multi_fields = [
        "Auteur",
        "Opvolgend(e) document(en)",
        "Eurovoc descriptoren",
        "Type",
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
        amount_of_list_indexes = len(
            [i for i in key_stack[: level + 1] if isinstance(i, int)]
        )
        if key_stack and amount_of_list_indexes:
            level += amount_of_list_indexes

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


for i in tqdm(range(0, 9999)):
    # Sample HTML content
    html_content = requests.get(
        f"https://www.dekamer.be/kvvcr/showpage.cfm?section=flwb&language=nl&cfm=/site/wwwcfm/search/fiche.cfm?ID=55K{i:04d}&db=FLWB&legislat=55"
    )
    # Parse the HTML and print the result
    nested_dict = parse_html_to_nested_dict(html_content.text)
    if nested_dict:
        with open(f"stukken/55K{i:04d}.json", "w") as fp:
            json.dump(nested_dict, fp)
