import requests
from tqdm import tqdm


for i in tqdm(range(310)):
    response = requests.get(f"https://www.dekamer.be/doc/PCRI/html/55/ip{i:03d}x.html")
    if response.status_code == 200:
        with open(f"plenaire/html/ip{i:03d}.html", "wb") as fp:
            fp.write(response.content)
    else:
        print(f"{i} was not a 200")
