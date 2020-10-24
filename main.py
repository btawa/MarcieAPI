from marcie_helper import *
import json
from flask import Flask, escape, request, Response
import re
from cube_list import opus10_cube, opus11_cube

app = Flask(__name__)


def checkAPI():
    """ This function is used to validate the API_KEY used in this API"""

    args = request.args

    with open('settings.json', 'r') as myfile:
        settings = json.load(myfile)

    if settings['API_KEY'] == args['api_key']:
        return True
    else:
        return False


@app.route('/api/card/<code>')
def getCard(code):
    """ This function is used to grab a specific card by code"""

    card_list = []

    if checkAPI() is True:
        for card in mycards:
            if re.search('^' + code, card['Code']):
                card_list.append(card)

        if len(card_list) == 1:
            return card_list[0]
        else:
            return Response(json.dumps(card_list), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/set/<opus>')
def getSet(opus):
    """ This function is used to grab a whole set by opus number from the API"""

    try:
        opus = int(opus)
    except:
        return Response('500 Input is not a integer', 500)

    if checkAPI() is True:
        card_list = []
        for card in mycards:
            if card['Set'] is None:
                pass
            else:
                if int(opus) == int(roman.fromRoman(card['Set'].split()[1])):
                    card_list.append(card)

        return Response(json.dumps(card_list), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/')
def getAllCards():
    """ This function will return all cards in the API"""

    if checkAPI() is True:
        return Response(json.dumps(mycards), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/cube/<opusnum>')
def getCube(opusnum):
    """ This function will return a list of cards which are part of an all-star cube.  The cube information comes
    from cube_list.py which contains the list of each card code in the cube"""

    cube_cards = []

    if checkAPI() is True:
        if opusnum == '10':
            ourcube = opus10_cube
        elif opusnum == '11':
            ourcube = opus11_cube

        for carda in ourcube:
            for cardb in mycards:
                if re.search('^' + carda, cardb['Code']):
                    cube_cards.append(cardb)

        return Response(json.dumps(cube_cards), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


with open('cards.json', 'r') as infile:
    mycards = json.load(infile)


if __name__ == '__main__':
    app.run()
