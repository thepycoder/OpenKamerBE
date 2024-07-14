import logging
import re
import locale
from datetime import datetime


def consistent_votekeys(s1, s2):
    key = "/".join([s1, s2])
    if ("Ja" in key) or ("Oui" in key):
        key = "yay"
    elif ("Nee" in key) or ("Non" in key):
        key = "nay"
    elif ("Onthoud" in key) or ("Abstentions" in key):
        key = "dunno"
    elif ("Total" in key) or ("Totaal" in key):
        key = "total"
    else:
        logging.warning(f"unexpected row contains {s1} and {s2}")
    return key


def parse_votes_table(tag, session_id: str, nr_within_session: int, debug: bool = True):
    # feed this the tag that made is_count return True
    # Initialize an empty list to store the parsed data
    parsed_data = {}

    # Iterate through each row of the table
    taalgroepen = False
    for i, row in enumerate(tag.find_all("tr")):
        if i == 0:
            continue  # skip the first row which states the vote id within the subject

        row_data = []
        for cell in row.find_all("td"):
            # Extract the text from the cell and strip any leading/trailing whitespace
            cell_text = cell.get_text(strip=True)
            row_data.append(cell_text)

        if taalgroepen:
            # We're doing a language-split vote (for some bureaucratic reason), but we don't really care about that
            # If need be we can split any vote on language based on the language of the person who voted, which we can capture ourselves
            # So let's ignore N and F columns and focus on Total column for each Y/N/D
            assert len(row_data) == 5
            row_data = [row_data[0], row_data[2], row_data[4]]

        if i == 1:
            # Check whether we are counting taalgroepen separately:
            taalgroepen = ("F" in "_".join(row_data)) and ("N" in "_".join(row_data))
            if taalgroepen:
                continue

        # if (
        #     debug
        # ):  # todo make check an assertion once all cases covered by is_votecounts_table
        #     check = (len(row_data) == 3) and (
        #         row_data[0]
        #         in set(
        #             [
        #                 "Ja",
        #                 "Nee",
        #                 "Totaal",
        #                 "Onthoudingen",
        #                 "Oui",
        #                 "Non",
        #                 "Abstentions",
        #                 "Total",
        #             ]
        #         )
        #     )
        #     if not check:
        #         logging.warning(
        #             f"{session_id} {nr_within_session} - Possibly invalid table passed is_votecounts_table (row_data: {row_data})"
        #         )

        # Parse data as ints if possible, else parse anyway but throw a warning.
        # try:
        key = consistent_votekeys(row_data[0], row_data[-1])
        # if taalgroepen:
        #     parsed_data[key] = {
        #         lan: int(lvote) for lan, lvote in zip(lankeys, row_data[1:-1])
        #     }
        # else:
        # try:
        parsed_data[key] = int(
            row_data[1]
        )  # key: yay/nay/dunno; row_data[1]: n of votes
        # except ValueError:
        #     print(session_id, nr_within_session)
        # except:
        #     key = consistent_votekeys(row_data[0], row_data[-1])
        #     if taalgroepen:
        #         parsed_data[key] = {
        #             lan: lvote for lan, lvote in zip(lankeys, row_data[1:-1])
        #         }
        #     else:
        #         parsed_data[key] = row_data[1]
        #     logging.warning(
        #         "Non-int votecount, possibly invalid format passing is_votecounts_table"
        #     )
    return parsed_data


def parse_date(soup):
    # Set the locale to Dutch (Belgium)
    locale.setlocale(locale.LC_TIME, "nl_BE.UTF-8")
    # Get the date from the document using regex
    date_string = (
        re.search(
            r"([1-9]|[1-2][0-9]|3[0-1])[\s\\n]*(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)[\s\\n]*(\d{4})",
            "\n".join(list(soup.strings)),
            re.IGNORECASE,
        )
        .group()
        .replace("\n", "")
    )
    # Turn the string into a datetime object
    dt = datetime.strptime(date_string, "%d %B %Y")
    return dt
