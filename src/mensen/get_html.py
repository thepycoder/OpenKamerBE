import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from retry import retry


@retry(exceptions=ValueError, tries=-1, delay=300)
def get_main_page(base_url, headers):
    session = requests.Session()  # Using session to maintain cookies
    session.headers.update(headers)

    try:
        response = session.get(base_url)
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

    return soup


@retry(exceptions=ValueError, tries=-1, delay=300)
def get_member_page(member_url):
    response = requests.get(member_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    if title_tag is None:
        raise ValueError("No title, something went wrong!")

    if "Request Rejected" in title_tag.text:
        raise ValueError("Request was rejected, wait and try again")

    return soup


base_url = "https://www.dekamer.be/kvvcr/showpage.cfm?section=/depute&language=nl&cfm=/site/wwwcfm/depute/cvlist54.cfm"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}
main_soup = get_main_page(base_url=base_url, headers=headers)
# Extract all the links to member details
links = main_soup.select("td > a")
for i, link in tqdm(enumerate(links)):
    href = link.attrs.get("href", "")
    # There are annoying empty links in between
    if "nohtml" in href:
        continue

    filename = f"src/mensen/html/{i}.html"
    # Get the member page url
    member_url = requests.compat.urljoin(base_url, href)
    member_soup = get_member_page(member_url)

    with open(filename, "w") as fp:
        fp.write(str(member_soup))
