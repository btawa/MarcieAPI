from fftcg_parser import *
from main import *

#with open('completesetffdecks.json', 'r') as infile:
#    cards = json.load(infile)

ffdecks = loadJson('http://ffdecks.com/api/cards/basic')
square = loadJson('https://fftcg.square-enix-games.com/en/get-cards')


ffdecks = parseffdeckstomarcie(ffdecks)
square = makecards(square)

print(json.dumps(ffdecks))


#with open('imageurls.txt', 'w') as outfile:
#    for url in imageurlset:
#        outfile.write(url + "\n")