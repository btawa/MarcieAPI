from fftcg_parser import *
import json
from flask import Flask, escape, request
from stringify import *

cards = loadJson('https://fftcg.square-enix-games.com/en/get-cards')

app = Flask(__name__)

mykeys = ('Element','Name_EN','Cost','Code','Multicard','Type_EN','Category_1','Text_EN','Job_EN','Power', 'Ex_Burst' , 'Set', 'Rarity')

for card in cards:
    for key in list(card):
        if key in mykeys:
            card[key] = prettyTrice(card[key])
        else:
            del card[key]

with open('cards.json', 'w') as outfile:
    json.dump(cards, outfile)

myjson = json.dumps(cards)
mydict = json.loads(myjson)

@app.route('/card/<name>')
def hello(name):
    for card in mydict:
        if card['Code'] == name:
            return card

@app.route('/')
def hello2():
    return myjson



if __name__ == '__main__':
    app.run()
