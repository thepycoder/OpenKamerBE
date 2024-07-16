import os
import time
from bs4 import BeautifulSoup
import requests
from retry import retry
from tqdm import tqdm


@retry(exceptions=ValueError, tries=-1, delay=300)
def get_page(url, headers):
    session = requests.Session()  # Using session to maintain cookies
    session.headers.update(headers)

    try:
        response = session.get(url)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.HTTPError as err:
        raise ValueError("HTTP error occurred:", err)
    except requests.exceptions.RequestException as err:
        raise ValueError("Error occurred:", err)

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("title")
    if title_tag is None:
        raise ValueError("No title, something went wrong!")

    if "Request Rejected" in title_tag.text:
        raise ValueError("Request was rejected, wait and try again")

    # Get the ID Story and then the text from it, check if it is anything, then remove the file is it's not
    story_container = soup.find(id="Story")

    if not story_container:
        raise ValueError(
            f"Could not find Story container needed to check if there is content on this page: {url}"
        )

    if (
        len(list(story_container.strings)) == 1
        and "does not exit" in story_container.string
    ):
        # In this case, the document does not exist (but there is a spelling mistake in the error message lol)
        return None

    return soup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

for i in tqdm(range(0, 9999)):
    filepath = f"src/parlementaire_stukken/json/55K{i:04d}.html"
    if os.path.exists(filepath):
        continue
    # Sample HTML content
    soup = get_page(
        f"https://www.dekamer.be/kvvcr/showpage.cfm?section=flwb&language=nl&cfm=/site/wwwcfm/search/fiche.cfm?ID=55K{i:04d}&db=FLWB&legislat=55",
        headers=headers,
    )
    time.sleep(1)
    if soup is None:
        continue
    # Parse the HTML and print the result
    with open(filepath, "w") as fp:
        fp.write(str(soup))
