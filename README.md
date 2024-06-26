# Parlementaire Dataset
Deze repository heeft tot doel een reeks hulpmiddelen te bieden voor het verzamelen, parseren en koppelen van gegevens geproduceerd door het Belgische Federale Parlement (dekamer.be). 
Een gedetailleerde toelichting van de types documenten is hier terug te vinden: https://www.dekamer.be/kvvcr/showpage.cfm?section=/searchlist&language=nl&html=/site/wwwroot/searchlist/typedocN.html#item0-overview

# Very WIP
Deze hele repo is very WIP en is een collectie losse scriptjes die onderzoekend en exploratief zijn bedoeld om te bewijzen dat de data te parsen is. Een volgende stap zet alles dat hierdoor geleerd wordt samen tot een mooier geheel

# Technisch
Alles werkt met Python. Package management wordt gedaan door [PDM](https://pdm-project.org/en/latest/). Lees de documentatie van PDM over hoe je packages moet toevoegen/verwijderen etc. https://pdm-project.org/latest/usage/dependency/

```
git clone git@github.com:thepycoder/OpenKamerBE.git
cd OpenKamerBE
pdm install
```

# Data Loaders
## Parlementairen: De mensen van het parlement
Er is een scraper die informatie over alle parlementariers scraped via deze link: https://www.dekamer.be/kvvcr/showpage.cfm?section=/depute&language=nl&cfm=/site/wwwcfm/depute/cvlist54.cfm (alleen deze regeerperiode, andere periodes zijn todo)

Er zijn altijd 150 parlementariers, maar op de webpagina staan er 188 omdat er soms mensen stoppen, gewisseld worden etc.

De code hiervoor staat onder `mensen` en is een [scrapy](https://scrapy.org/) project.

```
cd mensen
scrapy crawl people_spider -o output.json
```

## Parlementaire Stukken
Parlementaire stukken zijn alle documenten die het parlement produceert: https://www.dekamer.be/kvvcr/showpage.cfm?section=/flwb&language=nl&cfm=Listdocument.cfm?legislat=55
Dit gaat over wetsontwerpen, wetsvoorstellen, verslagen, voorstellen van resolutie etc.

Elk van deze documenten heeft een `fiche`.
Bvb: 
document: https://www.dekamer.be/kvvcr/showpage.cfm?section=/flwb&language=nl&cfm=/site/wwwcfm/flwb/flwbn.cfm?lang=N&legislat=55&dossierID=3698
fiche: https://www.dekamer.be/kvvcr/showpage.cfm?section=flwb&language=nl&cfm=/site/wwwcfm/search/fiche.cfm?ID=55K3698&db=FLWB&legislat=55

`read_fiche.py` is gemaakt om deze fiches te parsen naar JSON voor elk document binnen de regeerperiode.


## Plenaire Vergadering
In de plenaire vergadering wordt op deze stukken gestemd indien het zover is. Dit is mogelijks de belangrijkste moment: het bepaalt welke wetgeving in actie treedt.
De verslagen van deze vergadering staan appart: https://www.dekamer.be/kvvcr/showpage.cfm?section=/cricra&language=nl&cfm=dcricra.cfm?type=plen&cricra=CRI&count=all&legislat=55

`plenaire/explore.ipynb` laat zien hoe deze data kan geparsed worden. Specifiek om de stemmingen ook in JSON formaat te krijgen, zodat ze kunnen gelinkt worden aan de parlementaire stukken en mensen json's.
Aangezien het vrij grote bestanden zijn kan je ze eerst als html downloaden lokaal met `get_html.py` voordat je de notebook gebruikt om erdoor te waden.

## Common
In het mapje `common` staat code die bedoeld is gebruikt te worden door alle losse scripts. Het bepaalt hoe we data gaan opslaan in de backend.
Specifiek zijn hier al een aantal regels, wanneer deze niet voldaan worden voor een nieuw script, moet dat aangepast worden en idealiter in deze folder terecht komen.

### Regels
Namen:
- Volgorde: Achternaam Voornaam
- Accenten en speciale tekens worden gestript met [unidecode](https://pypi.org/project/Unidecode/)

Partijen:
- Wanneer er een naamsverandering is (e.g. SP.A naar Vooruit) worden alle parlementairen tot de nieuwe naam gerekend, ook al is hun pagina niet ge-updated
- Partijen specifiek genaamd in Brussel (e.g. PTB*PVDA enkel voor Brussel, anders PTB of PVDA appart) wordt gerekend tot de waalse partij


## Funny
Er is een mapje `funny` waar je screenshots van grappige passages in kan droppen
