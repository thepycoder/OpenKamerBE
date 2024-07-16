import json
from typing import List

from bs4 import BeautifulSoup

from common.objects import Member, Vote


def html_to_soup(file_path: str):
    # Open and read the HTML file
    with open(file_path, "r", encoding="latin-1") as file:
        # Create a BeautifulSoup object and append it to the list
        soup = BeautifulSoup(file, "html.parser")
    return soup


def get_votes(filepath: str = "votes.json") -> List[Vote]:
    with open(filepath, "r") as fp:
        votes_dicts = json.load(fp)
        votes = [Vote.from_dict(vote_dict) for vote_dict in votes_dicts]
    return votes


def get_members(filepath: str = "members.json") -> List[Member]:
    with open(filepath, "r") as fp:
        members_dicts = json.load(fp)
        members = [Member.from_dict(vote_dict) for vote_dict in members_dicts]
    return members
