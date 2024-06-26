"""These are some general rules and fixes to get the names and parties etc into their 'backend' format, which we'll use everywhere."""

from unidecode import unidecode


def fix_name(name, swap_first_last_name):
    """Define a number of rules that fix the names into a format that will fit downstream analysis"""
    # These special cases are quite simply written wrongly sometimes
    name = name.replace("Flahaux André", "Flahaut André")
    if name == "Wollants Ber":
        name = "Wollants Bert"
    # For some reason some names end with a .
    name = name.replace(".", "")
    # Get rid of accents, sometimes they're typed in the reports, but sometimes forgotten
    name = name.replace("'", "")
    # Unidecode gets rid of any special characters like accents or umlauts and simply replaces it with the basic letter (e.g. Ç becomes C)
    name = unidecode(name)
    # Split the name and reorder first and last names
    if swap_first_last_name and len(name.split()) > 1:
        name = " ".join(name.split()[1:]) + " " + name.split()[0]
    return name


def fix_party(party):
    # Vooruit used to be SP.A and some members still have it as their signature
    party = party.replace("sp.a", "Vooruit")
    # 2 Brussels reps have both PTB and PVDA in the name, make it PTB as Brussels is usually more walloon leaning anyway
    party = party.replace("PTB*PVDA", "PTB")

    return party
