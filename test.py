from fftcg_parser import *
from main import *

#with open('completesetffdecks.json', 'r') as infile:
#    cards = json.load(infile)

ffdecks = loadJson('https://ffdecks.com/api/cards/basic')
square = loadJson('https://fftcg.square-enix-games.com/en/get-cards')


ffdecks_cards = ffdeckstomarcieapi(ffdecks)
#square_cards = squaretomarcieapi(square)

imageurlset1 = urlset(ffdecks_cards)
#imageurlset2 = urlset(square_cards)

a = addimageurltojson(ffdecks_cards, imageurlset1)

print(json.dumps(a))



# with open('imageurls1.txt', 'w') as outfile:
#     for url in imageurlset1:
#         outfile.write(url + "\n")
# 
# with open('imageurls2.txt', 'w') as outfile:
#     for url in imageurlset2:
#         outfile.write(url + "\n")