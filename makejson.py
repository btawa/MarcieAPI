from fftcg_parser import *
import sys

if sys.argv[1] == 'ffdecks':
    ffdecks = loadJson('https://ffdecks.com/api/cards/basic')
    cards = ffdeckstomarcieapi(ffdecks['cards'])
    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)
    promos = []

    with open('ffdecks.json', 'w+') as outfile:
        json.dump(cards, outfile)

    with open('ffdecks_imageurls.txt', 'w+') as outfile:
        for url in imageurlset:
            outfile.write(url + '\n')

    with open('ffdecks_promos.json', 'w+') as outfile:
        for card in cards:
            if re.search(r'PR-0[1-9]', card['Code']):
                promos.append(card)
        json.dump(promos, outfile)


elif sys.argv[1] == 'square':
    square = loadJson('https://fftcg.square-enix-games.com/en/get-cards')
    cards = squaretomarcieapi(square['cards'])
    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)

    with open('square.json', 'w+') as outfile:
        json.dump(cards, outfile)

    with open('ffdecks_imageurls.txt', 'w+') as outfile:
        for url in imageurlset:
            outfile.write(url + '\n')

elif sys.argv[1] == 'combine':
    with open('ffdecks_promos.json', 'r') as infile:
        promos = json.load(infile)

    with open('square.json', 'r') as infile:
        cards = json.load(infile)

    combined = cards + promos

    with open('combined.json', 'w+') as outfile:
        json.dump(combined, outfile)

else:
    pass