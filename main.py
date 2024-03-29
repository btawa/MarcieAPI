import json
import os
import re
import threading

from decouple import Config, RepositoryEnv
from flask import Flask, request, Response, render_template
import roman

from CardClient import CardClient
from cube_list import opus10_cube, opus11_cube, opus12_cube, opus13_cube
from marcie_helper import *

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = '.env'
env_config = Config(RepositoryEnv(os.path.join(SCRIPT_PATH, ENV_FILE)))

card_client = CardClient()
card_client.init()
app = Flask(__name__)


def checkAPI():
    """ This function is used to validate the API_KEY used in this API"""

    args = request.args

    if env_config.get('API_KEY') == args['api_key']:
        return True
    else:
        return False


@app.route('/api/lastfetch', methods=['GET'])
def get_last_fetch():
    if checkAPI() is True:
        if card_client.lock is False:
            lastfetch = {'lastfetch': card_client.lastfetch}
        else:
            lastfetch = {'lastfetch': card_client.lastfetch, 'status': 'Fetch in progress'}

        return Response(response=json.dumps(lastfetch), status=200, mimetype='application/json')
    else:
        return Response('401 Unauthorized API Key', 401)


@app.route('/api/new', methods=['POST'])
def get_new_cards():
    if checkAPI() is True:
        threads = list()

        try:
            if card_client.lock is False:
                card_client.lock = True

                x = threading.Thread(target=card_client.pull_new_cards, args=())
                threads.append(x)
                x.start()

                status = {'status': "Starting get_new_cards, this may take a while"}

                return Response(response=json.dumps(status), status=201, mimetype='application/json')
            else:
                status = {'status': "CardClient is locked, is something already running?"}
                return Response(response=json.dumps(status), status=401, mimetype='application/json')

        except:
            return Response(status=400)
    else:
        return Response('401 Unauthorized API Key', 401)


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


# Square no longer labels things in the format `Opus X`, so set is broken
# This will probably be deprecated and can just use `/card/15-` commenting out for now.

# @app.route('/api/set/<opus>')
# def getSet(opus):
#     """ This function is used to grab a whole set by opus number from the API"""
#
#     try:
#         opus = int(opus)
#     except:
#         return Response('500 Input is not a integer', 500)
#
#     if checkAPI() is True:
#         card_list = []
#         for card in card_client.cards:
#             if card['Set'] is None:
#                 pass
#             else:
#                 if int(opus) == int(roman.fromRoman(card['Set'].split()[1])):
#                     card_list.append(card)
#
#         return Response(json.dumps(card_list), mimetype='application/json')
#     else:
#         return Response('401 Unauthorized API Key', 401)


@app.route('/api/')
def getAllCards():
    """ This function will return all cards in the API"""

    if checkAPI() is True:
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

@app.route('/api/links/<opusnum>')
def get_square_images(opusnum):
    square_root_url = "https://fftcg.cdn.sewest.net/images/cards/full/"
    square_end_url = "_eg.jpg"
    square_urls = []

    if checkAPI() is True:
        try:
            for card in card_client.cards:
                if re.search(r'^' + opusnum + '-', card['Code']):
                    image_url = f"{square_root_url}{card['Code']}{card['Rarity']}{square_end_url}"
                    square_urls.append(image_url)

        except:
            return Response('Bad Request', 400)

        finally:
            return Response(json.dumps(square_urls), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000')
