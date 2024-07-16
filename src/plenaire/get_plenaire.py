from copy import copy
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from bs4 import BeautifulSoup
import bs4
from tqdm import tqdm

from common.io_utils import html_to_soup
from common.objects import Vote
from common.text_corrections import fix_name
from plenaire.identifiers import (
    is_naamstemming,
    is_naamstemming_details,
    is_section,
    is_subject,
    is_votecounts_table,
    re_vote_nr,
    re_detail_vote_nr,
    re_vote_count,
)
from plenaire.parsers import parse_date, parse_votes_table


def naamstemming_to_votes(
    naamstemming: bs4.element.Tag,
    session_id: str,
    filename: str,
) -> Dict[Tuple[str, int], Vote]:
    # In this dict we'll keep track of the different votes within this document. A single "naamstemming" can be considered a round of votes, for multiple documents
    # So we'll log each of these votes separately
    votes: Dict[Tuple[str, int], Vote] = dict()

    current_vote: Vote = Vote(session_id=session_id, srcfile=filename)
    last_tag_was_subject = False
    # .next_siblings looks at the tag ahead of naamstemming in the corresponding soup.
    # We're essentially going line by line through the document here
    for j, tag in enumerate(naamstemming.next_siblings):
        tag_text = " ".join(tag.strings).lower()

        # Next siblings also produces a nonsense string (like \n) after every real tag
        # So skip all even next tags, which will be nonsense (but annoyingly, a different nonsense every document)
        if j % 2 == 0:
            continue

        # A bold (titre2) sentence in dutch signifies a subject of a vote. It can be a new subject
        # or a new line in the current subject. Depends on whether the previous sentence was also a subject
        # or not
        if is_subject(tag):
            # Every subtitle in between "Naamstemmingen" and the next H1 title is considered part of a vote
            # If the previous tag was a subject, this new line is part of the previous one
            if last_tag_was_subject:
                current_vote.subject += tag_text + "\n"
            else:
                # If not: consider this to be a new vote, close off the old one and reset
                current_vote = close_vote_and_start_new(
                    Vote, votes, session_id, filename, current_vote, tag_text
                )
            last_tag_was_subject = True
        elif is_section(tag):
            # If we hit the next Title, the voting section is done
            # This should never happen right after a subtitle, otherwise we won't have the vote nr anyway
            # However, we're e.g searching for "naamstemmingen" so it might happen the french version is next immediately below
            # it's also a title, so skip that
            if is_naamstemming(tag):
                last_tag_was_subject = False
                continue
            # If this is truly a next title, close off the current vote and break the loop (aka stop going line by line, we have everything we need)
            current_vote = close_vote_and_start_new(
                Vote, votes, session_id, filename, current_vote, tag_text
            )
            break

        else:
            # In this case it's normal text
            # First, check if it contains the vote nr (aka we're in between vote headers)
            vote_match = re.search(re_vote_nr, tag_text, re.IGNORECASE)
            if vote_match:
                # Extract the matched text
                matched_text = vote_match.group()
                # Extract the number, assuming it's the last part of the matched string
                number = int(re.search(r"\d+", matched_text).group())
                # Set the current vote to that number. This overwrites the number inhereted from the previous voting session in this section.
                current_vote.nr_within_session = number

                # Parse the table counting the votes
                # if not is_votecounts_table(
                #     tag
                # ):  # matching stemming/vote should only find tables:
                #     # logging.warning(
                #     #     f"Tag containing stemming/vote is not a votecountstable: {tag}"
                #     # )
                #     pass
                # Overwrite the votecountstable inhereted from the previous voting session in this section.
                summarized_vote = parse_votes_table(tag, session_id, number)
                if summarized_vote:
                    current_vote.summarized_vote = summarized_vote

            last_tag_was_subject = False

    # If this is truly a next title, close off the current vote and break the loop
    close_vote_and_start_new(Vote, votes, session_id, filename, current_vote, tag_text)

    return votes


def extend_votes_with_names(
    soup: BeautifulSoup, session_id: str, votes: Dict[Tuple[str, int], Vote]
):
    # To get the names from the appendix in the document, it's easier to work purely on text as the HTML is finnicky and non-unique there
    full_text = soup.text
    # Look for a line in the HTML where "details" and "naamstemmingen" occur, below which is listed who voted Y/N/eh
    vote_details = soup.find_all(is_naamstemming_details)
    if vote_details:
        if len(vote_details) > 1:
            raise ValueError(
                f"Found more than 1 occurence of Details of Naamstemmingen in document nr {session_id}"
            )
            # vote_details = vote_details[-1]
        else:
            vote_details = vote_details[0]

        naamstemming_index = full_text.find(vote_details.text)
        detailed_text = full_text[naamstemming_index:]

        split_on_vote = re.split(
            re_detail_vote_nr,
            detailed_text,
        )

        for i in range(1, len(split_on_vote), 2):
            nr_within_session = int(split_on_vote[i])
            vote_body = split_on_vote[i + 1].strip()

            split_body = re.split(
                re_vote_count,
                vote_body,
            )

            for j in range(1, len(split_body), 3):
                vote = split_body[j].lower()
                # amount_of_votes = split_body[j + 1]
                names = split_body[j + 2].replace("\n", " ")
                names = [n.strip() for n in names.split(",") if n.strip()]
                names = [" ".join(n.split()) for n in names]
                names = [fix_name(name, swap_first_last_name=False) for name in names]

                # print(f"{amount_of_votes} votes {vote}: {names}")

                if vote in ("ja", "oui"):
                    if (session_id, nr_within_session) in votes:
                        votes[(session_id, nr_within_session)].yay = names
                elif vote in ("nee", "non"):
                    if (session_id, nr_within_session) in votes:
                        votes[(session_id, nr_within_session)].nay = names
                elif vote in ("abstentions", "onthoudingen"):
                    if (session_id, nr_within_session) in votes:
                        votes[(session_id, nr_within_session)].dunno = names
                else:
                    raise ValueError(
                        f"Vote is not a valid value: {vote} for session: {session_id}"
                    )
    return votes


def extend_votes_with_date(votes: Dict[Tuple[str, int], Vote], document_date: datetime):
    for key, vote in votes.items():
        vote.date = document_date
    return votes


def close_vote_and_start_new(Vote, votes, session_id, srcfile, current_vote, tag_text):
    if (
        current_vote.subject
        and current_vote.nr_within_session != -1
        and (session_id, current_vote.nr_within_session) not in votes
    ):
        votes[(session_id, current_vote.nr_within_session)] = copy(current_vote)
    current_vote = Vote(session_id=session_id, srcfile=srcfile, subject=tag_text + "\n")
    return current_vote


def main(html_dir: str = "html", offset: int = 0, amount: int = 309):
    all_votes: Dict[Tuple[str, int], Vote] = {}
    for i, filename in tqdm(
        enumerate(sorted(os.listdir(html_dir))[offset : offset + amount])
    ):
        # Check if the file is an HTML file
        if not filename.endswith(".html"):
            continue
        # Construct full file path
        file_path = os.path.join(html_dir, filename)
        # First get all the html files into beautifulsoups
        soup = html_to_soup(file_path)
        # Get the document date from the header of the document so we can add it to the votes
        document_date = parse_date(soup)
        # Find the naamstemmingen (named votes)
        naamstemmingen = soup.find_all(is_naamstemming)
        # Turn each of the naamstemmingen into a Vote object
        for naamstemming in naamstemmingen:
            session_id = f"{i+1+offset:04d}"
            votes = naamstemming_to_votes(
                naamstemming=naamstemming,
                session_id=session_id,
                filename=filename,
            )
            votes = extend_votes_with_names(
                soup=soup, session_id=session_id, votes=votes
            )
            votes = extend_votes_with_date(votes=votes, document_date=document_date)
            all_votes.update(votes)

    return all_votes


if __name__ == "__main__":
    votes = main(html_dir="src/plenaire/html")
    with open("votes.json", "w") as fp:
        # Use default=str to stringify everything that's not json serializable (like datetime)
        json.dump([v.to_dict() for v in votes.values()], fp, indent=4)
