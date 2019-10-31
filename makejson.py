from fftcg_parser import *
from main import *
import sys

if sys.argv[1] == 'ffdecks':
    ffdecks = loadJson('https://ffdecks.com/api/cards/basic')
    cards = ffdeckstomarcieapi(ffdecks['cards'])
    imageurlset = urlset(cards)

elif sys.argv[1] == 'square':
    square = loadJson('https://fftcg.square-enix-games.com/en/get-cards')
    cards = squaretomarcieapi(square['cards'])
    imageurlset = urlset(cards)
else:
    pass

cards = addimageurltojson(cards, imageurlset)

with open('cards.json', 'w+') as outfile:
    json.dump(cards, outfile)
