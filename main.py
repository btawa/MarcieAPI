from fftcg_parser import *
import json

cards = loadJson('https://fftcg.square-enix-games.com/en/get-cards')

mykeys = ('Element','Name_EN','Cost','Code','Multicard','Type_EN','Category_1','Text_EN','Job_EN','Power', 'Ex_Burst' , 'Set', 'Rarity')

for card in cards:
    for key in list(card):
        if key in mykeys:
            card[key] = prettyTrice(card[key])
        else:
            del card[key]

with open('cards.json', 'w') as outfile:
    json.dump(cards, outfile)

print(cards[0])



