# Mapping from person ID to party ID
from collections import defaultdict

from common.io_utils import get_members, get_votes
from common.text_corrections import fix_name

INCLUDE_DUNNO = False

votes = get_votes()
members = get_members()

person_to_party = {
    fix_name(m.name, swap_first_last_name=True): m.party for m in members
}
parties = set(person_to_party.values())

dissenting_party_votes = {party: 0 for party in parties}
party_votes = {party: 0 for party in parties}
lone_wolfs = defaultdict(int)
dissenters = defaultdict(int)

# For each vote, find the majority per party
for vote in votes:
    for party in parties:
        yay = [n for n in vote.yay if n and person_to_party[n] == party]
        nay = [n for n in vote.nay if n and person_to_party[n] == party]
        dunno = [n for n in vote.dunno if n and person_to_party[n] == party]

        votecounts = [len(yay), len(nay), len(dunno)]
        party_votes[party] += sum(votecounts)
        if votecounts.count(0) == 2:
            # No dissenting vote, skipping
            continue
        # This is where it gets interesting, at least one person voted against their party!
        # print(party, votecounts, vote.subject)
        # Let's keep track of which people dissent and in which party they are
        majority_idx = votecounts.index(max(votecounts))

        vote_sets_to_count = [yay, nay]
        if INCLUDE_DUNNO:
            vote_sets_to_count.append(dunno)

        for i, votelist in enumerate(vote_sets_to_count):
            if i == majority_idx:
                continue
            # We're adding the amount of non-majority votes to the dissenting party votes here
            dissenting_party_votes[party] += len(votelist)
            if len(votelist) == 1:
                lone_wolfs[votelist[0]] += 1
            for name in votelist:
                dissenters[name] += 1

print("Dissenting Parties:")
print("=" * 25)
print(dissenting_party_votes)
for party in parties:
    percentage_dissenting = round(
        100 * (dissenting_party_votes[party] / party_votes[party]), 2
    )
    print(f"{party}: {percentage_dissenting}%")
print("\n")

print("Dissenters:")
print("=" * 25)
for name, amount in sorted(dissenters.items(), key=lambda x: x[1], reverse=True):
    print(f"{name} ({person_to_party[name]}): {amount}")
print("\n")

print("Lone Wolfs (they were alone in their dissenting vote):")
print("=" * 25)
for name, amount in sorted(lone_wolfs.items(), key=lambda x: x[1], reverse=True):
    print(f"{name} ({person_to_party[name]}): {amount}")
