from marcie_helper import *
import sys
import os

if sys.argv[1] == 'ffdecks':
    ffdecks = loadJson('https://ffdecks.com/api/cards/basic')
    cards = ffdeckstomarcieapi(ffdecks['cards'])
    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)
    promos = []

    with open('ffdecks.json', 'w+') as outfile:
        json.dump(cards, outfile)

    with open('ffdecks_promos.json', 'w+') as outfile:
        for card in cards:
            if re.search(r'PR-0[1-9]', card['Code']):
                promos.append(card)
        json.dump(promos, outfile)


elif sys.argv[1] == 'square':
    square = loadJson('https://fftcg.square-enix-games.com/en/get-cards')
    cards = squaretomarcieapi(square['cards'])

    # Remove Duplicates
    result = []
    for card in cards:
        if card not in result:
            result.append(card)

    cards = result

    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)

    with open('square.json', 'w+') as outfile:
        json.dump(cards, outfile)


elif sys.argv[1] == 'combine':
    with open('ffdecks_promos.json', 'r') as infile:
        promos = json.load(infile)

    with open('square.json', 'r') as infile:
        cards = json.load(infile)

    combined = cards + promos

    with open('combined.json', 'w+') as outfile:
        json.dump(combined, outfile)

    os.remove('ffdecks.json')
    os.remove('square.json')
    os.remove('ffdecks_promos.json')

else:
    pass