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

    for tr in soup.find_all("tr"):
        td_key, td_value = tr.find_all("td")

        # Extract the clean text from each <td>
        key_text = " ".join(td_key.get_text(strip=True).split())
        value_text = " ".join(td_value.get_text(strip=True).split())
        if not value_text:
            value_text = {}

        # Calculate the level of nesting based on <img> tags
        images = td_key.find_all("img", class_="puce")
        level = len(images)

        # If the current level is the same as the length of the stack
        # replace the latest key with the current key
        # e.g. [Kamer, Hoofdoc, BICAM] if the next one is Document Nr. it should
        # replace BICAM.
        # If the level is one more, just append it, we've made a new level
        # If the level is less, replace the corresponding key entry and all following ones
        if level == len(key_stack):
            key_stack.append(key_text)
        elif level == len(key_stack) + 1:
            key_stack.append(key_text)
        elif level < len(key_stack):
            if key_stack[level] == key_text:
                latest_key = list(
                    reduce(operator.getitem, key_stack[:-2], nested_dict).keys()
                )[-1]
                if "::" in latest_key:
                    key_text = key_text + f"::{int(latest_key.split('::')[1]) + 1}"
                else:
                    key_text = key_text + "::1"
            key_stack = key_stack[:level] + [key_text]

        # Then use the keystack to set the correct key value pair in the dict
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
