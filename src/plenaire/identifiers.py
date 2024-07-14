# Some regexes
re_vote_nr = r"\(stemming\/vote(?:\s|&nbsp;)* *\d+(?:\s|&nbsp;)*\)"
re_detail_vote_nr = r"Vote[\s| ]*nominatif[\s| ]*-[\s| ]*Naamstemming:[\s| ]*(\d*)"
re_vote_count = r"(Oui|Ja|Non|Nee|Abstentions|Onthoudingen)[\s| ]*(\d*)[\s| ]*(?:Oui|Ja|Non|Nee|Abstentions|Onthoudingen)"


def is_subject(tag):
    return (tag.name == "p" and "Titre2NL" in tag.get("class", [])) or (
        tag.name == "h2"
        and tag.get("class", []) == []
        and not tag.find("span", attrs={"lang": "FR"})
    )


def is_section(tag):
    return (
        tag.name == "p"
        and ("Titre1NL" in tag.get("class", []) or "Titre1FR" in tag.get("class", []))
    ) or (tag.name == "h1" and tag.get("class", []))


def is_votecounts_table(tag):
    "should return True for beginning of a table"
    return (tag.name == "table") and (len(tag) == 11)


def is_naamstemming(tag):
    return (
        (
            tag.name == "p"
            and (tag.get("class") == ["Titre1NL"] or tag.get("class") == ["Titre1FR"])
        )
        or (tag.name == "h1")
    ) and (
        "naamstemmingen" in tag.text.lower().strip()
        or "votes nominatifs" in tag.text.lower().strip()
    )


def is_naamstemming_details(tag):
    return (
        ((tag.name == "p" and tag.get("class") == ["Titre1NL"]) or (tag.name == "h1"))
        and "detail" in tag.text.lower()
        and "naamstemmingen" in tag.text.lower()
    )
