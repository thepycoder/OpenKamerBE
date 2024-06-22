import json
import os
import time
import requests
from bs4 import BeautifulSoup
import re

from tqdm import tqdm
from common.text_corrections import fix_name, fix_party


HTML_FOLDER = "src/mensen/html"


# Define the main function to scrape data
def scrape_members():
    members_data = []
    for filename in tqdm(os.listdir(HTML_FOLDER)):
        if ".html" not in filename:
            continue
        with open(os.path.join(HTML_FOLDER, filename)) as fp:
            html = fp.read()
        member_soup = BeautifulSoup(html, "html.parser")

        # Extract data
        short_description = (
            member_soup.select_one("td > p").text.strip()
            if member_soup.select_one("td > p")
            else "N/A"
        )

        # Fractie regex
        fraction_regex = r"Volksvertegenwoordiger[\s| ]*\((.*?)\)"
        fraction_match = re.search(fraction_regex, short_description)
        fraction = fraction_match.groups()[0] if fraction_match else "N/A"

        # Birthyear regex
        birthyear_regex = r"op (\d{1,2} \w+ \d{4})"
        birthyear_match = re.search(birthyear_regex, short_description)
        birthyear = birthyear_match.group(1) if birthyear_match else "N/A"

        # Collect data
        members_data.append(
            {
                "name": fix_name(member_soup.select_one("center > h2").text),
                "image_url": member_soup.select_one("td > img")["src"]
                if member_soup.select_one("td > img")
                else None,
                "party": fix_party(fraction),
                "birthyear": birthyear,
            }
        )

    return members_data


# Execute the scraping function
members = scrape_members()
with open("members.json", "w") as fp:
    json.dump(members, fp)
for member in members:
    print(member)
