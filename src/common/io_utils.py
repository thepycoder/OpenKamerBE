import json
from typing import List

from common.objects import Member, Vote


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
