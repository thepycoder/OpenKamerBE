import json

from plenaire.get_plenaire import Vote


with open("votes.json", "r") as fp:
    votes_dicts = json.load(fp)
    votes = [Vote.from_dict(vote_dict) for vote_dict in votes_dicts]

votes_with_mistakes = {}
votes_with_error = {}

for v in votes:
    n_yay = len(v.yay)
    n_nay = len(v.nay)
    n_dunno = len(v.dunno)

    if "yay" not in v.summarized_vote:
        print(v.session_id, v.nr_within_session, v)

    if not isinstance(v.summarized_vote["yay"], dict):
        wrong_yay = int(v.summarized_vote["yay"]) != n_yay
        wrong_nay = int(v.summarized_vote["nay"]) != n_nay
        wrong_dunno = int(v.summarized_vote["dunno"]) != n_dunno

        if any([wrong_yay, wrong_nay, wrong_nay]):
            votes_with_mistakes[(v.session_id, v.nr_within_session)] = v
            print(f"Mistakes found for session {v.session_id} ({v.nr_within_session}):")
            if wrong_yay:
                print(
                    f"    Ja/Oui: Namenlijst {n_yay}; Tabel: {v.summarized_vote['yay']}"
                )
            if wrong_nay:
                print(
                    f"    Nee/Non: Namenlijst: {n_nay}; Tabel: {v.summarized_vote['nay']}"
                )
            if wrong_dunno:
                print(
                    f"    Onthoudingen/Abstentions: Namenlijst: {n_dunno}; Tabel: {v.summarized_vote['dunno']}"
                )

print()
if len(votes_with_mistakes) == 0:
    print("All counts check out.")
else:
    print(
        f"Parsed names do not correspond to parsed summarized votes in table for {len(votes_with_mistakes)} votes ({len(votes_with_mistakes)/len(votes)*100:0.2f}% of all votes)."
    )
    print(
        f"Wrongly parsed tables which could not be checked: {len(votes_with_error)} out of {len(votes)}"
    )
