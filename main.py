from marcie_helper import *
import json
from flask import Flask, escape, request, Response, render_template
import re
from cube_list import opus10_cube, opus11_cube, opus12_cube, opus13_cube
from CardClient import CardClient

app = Flask(__name__)
card_client = CardClient()


def checkAPI():
    """ This function is used to validate the API_KEY used in this API"""

    args = request.args

    with open('settings.json', 'r') as myfile:
        settings = json.load(myfile)

    if settings['API_KEY'] == args['api_key']:
        return True
    else:
        return False


@app.route('/api/new', methods=['POST'])
def get_new_cards():
    try:
        card_client.pull_new_cards()
        return Response(status=201)
    except:
        return Response(status=400)


@app.route('/api/card/<code>')
def getCard(code):
    """ This function is used to grab a specific card by code"""

    card_list = []

    if checkAPI() is True:
        for card in card_client.cards:
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
        for card in card_client.cards:
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
        print(card_client.lastfetch)
        return Response(json.dumps(card_client.cards), mimetype='application/json')
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
        elif opusnum == '12':
            ourcube = opus12_cube
        elif opusnum == '13':
            ourcube = opus13_cube

        for carda in ourcube:
            for cardb in card_client.cards:
                if re.search('^' + carda, cardb['Code']):
                    cube_cards.append(cardb)

        return Response(json.dumps(cube_cards), mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/matches/image')
def imageMatches():
    if checkAPI() is True:
        with open('/root/opusscraper/matches.json', 'r') as f:
            matches = json.load(f)
        return render_template('matches.html', urls=matches)


@app.route('/api/matches')
def urlMatches():
    if checkAPI() is True:
        with open('/root/opusscraper/matches.json', 'r') as f:
            matches = json.load(f)

        return Response(json.dumps(matches), mimetype='application/json')


if __name__ == '__main__':
    app.run()
