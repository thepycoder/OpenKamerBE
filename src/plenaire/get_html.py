import requests
import os
from typing import Union

from bs4 import BeautifulSoup
from tqdm import tqdm

def get_html(legislature:Union[str,int], v=False):
    # legislature is allowed to be an int or a numerical string:
    assert (isinstance(legislature, str) and legislature.isnumeric()) or isinstance(legislature, int)

    # prepare dir to store htmls for this legislature:
    path_htmls_dir = f"plenaire/html/{legislature}"
    if not os.path.exists(path_htmls_dir):
        os.makedirs(path_htmls_dir)

    # list available htmls: 
    available_htmls = list_available_htmls(legislature)
    n_htmls = len(available_htmls)
    if v:
        print(f"{n_htmls} available htmls found for legislature {legislature}.")

    # iterate over the available htmls and store them in the defined location:
    base_url = "https://www.dekamer.be"
    for file in tqdm(available_htmls):  # tqdm(range(310)):  # n=310 for legislature 55
        response = requests.get(base_url + file)
        # response = requests.get(f"https://www.dekamer.be/doc/PCRI/html/{legislature}/ip{i:03d}x.html")
        if response.status_code == 200:
            filename = file[file.rfind('/')+1:]
            if v:
                print(filename)

            # with open(f"plenaire/html/ip{i:03d}.html", "wb") as fp:
            with open(os.path.join(path_htmls_dir, filename), "wb") as fp:
                fp.write(response.content)
        else:
            if v:
                print(f"{file} was {response.status_code}, not a 200")


def list_available_htmls(legislature:Union[str,int]):
    # Retrieve the page of the corresponding legislature: 
    url = f"https://www.dekamer.be/kvvcr/showpage.cfm?section=/cricra&language=nl&cfm=dcricra.cfm?type=plen&cricra=CRI&count=all&legislat={legislature}" 
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all hyperlinks and list those containing "doc/PRCI/html":
        links = soup.find_all('a', href=True)
        filtered_links = [link['href'] for link in links if 'doc/PCRI/html' in link['href']]
        return filtered_links
    
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


def main():
    legislature = 56
    files = list_available_htmls(legislature)
    print(files)
    get_html(legislature)

if __name__ == '__main__':
    print('main')
    main()