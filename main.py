from fftcg_parser import *
import json
from flask import Flask, escape, request, Response

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


@app.route('/api/card/<name>')
def hello(name):
    card_list = []
    for card in mydict:
        if name in card['Code']:
            card_list.append(card)

    if len(card_list) == 1:
        return card_list[0]
    else:
        return Response(json.dumps(card_list), mimetype='application/json')


@app.route('/api/set/<opus>')
def set_grab(opus):
    card_list = []
    for card in mydict:
        if int(opus) == int(roman.fromRoman(card['Set'].split()[1])):
             card_list.append(card)

    return Response(json.dumps(card_list), mimetype='application/json')


@app.route('/api/')
def hello2():
    return myjson


if __name__ == '__main__':
    app.run()
