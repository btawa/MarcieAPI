import json
import logging
import re
import urllib.request
import requests

import roman

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')


# def getimageURL(code):
#     """This function takes in a code as a string and returns an image link which points to square"""
#
#     if re.search(r'[0-9]+\-[0-9]{3}[a-zA-Z]/[0-9]+\-[0-9]{3}[a-zA-Z]', code):
#         URL = 'https://fftcg.cdn.sewest.net/images/cards/full/' + code[-6:] + '_eg.jpg'
#     else:
#         URL = 'https://fftcg.cdn.sewest.net/images/cards/full/' + code + '_eg.jpg'
#
#     return URL


def urlset(cards_list):
    """This function takes in list of cards and creates a list of URL's and returns it as a list"""

    url_list = []
    for card in cards_list:
        if re.search(r'\/', card['Code']):
            for x in card['Code'].split('/'):
                if re.search(r'H|R|P|C|L', x):
                    url_list.append(
                        'https://storage.googleapis.com/marcieapi-images/' + x + '_eg.jpg')
                else:
                    url_list.append(
                        'https://storage.googleapis.com/marcieapi-images/' + x + card['Rarity'] + '_eg.jpg')
        elif card['Rarity'] in ["P","B"]:
            url_list.append(
                'https://storage.googleapis.com/marcieapi-images/' + card['Code'] + '_eg.jpg')
        else:
            url_list.append(
                'https://storage.googleapis.com/marcieapi-images/' + card['Code'] + card['Rarity'] + '_eg.jpg')
    return list(dict.fromkeys(url_list))


# Loading JSON from file and load it into a variable
# data - untouched JSON from file
# card_list - list of cards

def loadJson(path):

    try:
        data = requests.get(path)
        cards_list = json.loads(data.text)
        return cards_list
    except:
        return


def prettyTrice(string):
    # Weird bracket removal:
    string = string.replace(u"\u300a", '(')
    string = string.replace(u"\u300b", ')')
    string = string.replace('&middot;', u"\u00B7")

    # Replace Element Logos
    string = string.replace(u"\u571F", 'Earth')
    string = string.replace(u"\u6c34", 'Water')
    string = string.replace(u"\u706b", 'Fire')
    string = string.replace(u"\u98a8", 'Wind')
    string = string.replace(u"\u6c37", 'Ice')
    string = string.replace(u"\u5149", 'Light')
    string = string.replace(u"\u95c7", 'Dark')
    string = string.replace(u"\u96f7", 'Lightning')

    # Special Ability [[s]]text[[/]] - Shadow Flare on 7-034
    string = re.sub(r"\[\[s\]\](.*?)\[\[/\]\]", r"\1", string)

    # Italics [[i]]text[[/]]
    string = re.sub(r"\[\[i\]\](.*?)\[\[/\]\]", r"\1", string)

    # Replace EX Burst
    string = re.sub(r"\[\[ex\]\]EX BURST\s*\[\[/\]\]\s*", "[EX BURST] ", string)
    string = re.sub(r"\[\[ex\]\]EX BURS\s*\[\[/\]\]T\s*", "[EX BURST] ", string)
    string = re.sub(r"^EX BURST", "[EX BURST]", string)

    # Special Switch
    string = string.replace(u"\u300a"u"\u0053"u"\u300b", '[Special]')

    # Bubble used for Multicard and Ex_Burst
    string = string.replace(u'\u25CB', 'True')
    string = string.replace(u'\u3007', 'True')

    # Horizontal Bar
    string = string.replace(u'\u2015', '')

    # Replace Fullwidth Numbers with normal numbers
    string = string.replace(u"\uFF11", '1')
    string = string.replace(u"\uFF12", '2')
    string = string.replace(u"\uFF13", '3')
    string = string.replace(u"\uFF14", '4')
    string = string.replace(u"\uFF15", '5')
    string = string.replace(u"\uFF16", '6')
    string = string.replace(u"\uFF17", '7')
    string = string.replace(u"\uFF18", '8')
    string = string.replace(u"\uFF19", '9')
    string = string.replace(u"\uFF10", '0')
    string = string.replace(u"\u2015", "-")  # Damage 5 from Opus X cards
    string = string.replace(u"\u00fa", "u")  # Cuchulainn u with tilda

    string = string.replace(u"\u4E00"u"\u822C", 'Generic')  # Fixes #1

    # Tap Symbol
    string = string.replace(u"\u30C0"u"\u30EB", 'Dull')

    # Yuri 7-128 has double quotes around some of his abilities which are printed on card as one quote
    string = string.replace("\"\"", '\"')

    # New lines [[br]]
    string = re.sub(r"\[\[br\]\]", "\n", string)

    return string


# This function is used to convert information from ffdecks JSON
# to marcieapi JSON.  FFDecks uses different characters to denote
# different things.

def ffdeckstostring(string):
    if string is not None:
        string = string.replace('{s}', '[Special]')
        string = string.replace('{a}', '(Water)')
        string = string.replace('{w}', '(Wind)')
        string = string.replace('{e}', '(Earth)')
        string = string.replace('{f}', '(Fire)')
        string = string.replace('{i}', '(Ice)')
        string = string.replace('{l}', '(Lightning)')
        string = string.replace('{d}', '(Dull)')

        string = string.replace('{x}', '[EX BURST]')
        string = string.replace('{0}', '(0)')
        string = string.replace('{1}', '(1)')
        string = string.replace('{2}', '(2)')
        string = string.replace('{3}', '(3)')
        string = string.replace('{4}', '(4)')
        string = string.replace('{5}', '(5)')
        string = string.replace('{6}', '(6)')
        string = string.replace('{7}', '(7)')
        string = string.replace('{8}', '(8)')
        string = string.replace('{9}', '(9)')

        string = string.replace('*', '')
        string = string.replace('%', '')
        string = string.replace('~', '')
        string = string.replace(u"\u2015", "-")  # Damage 5 from Opus X cards
        string = string.replace(u"\u00fa", "u")  # Cuchulainn u with tilda

    return string


# This function converts ffdecks inputs to marcieapi output

def ffdeckstomarcieapi(listofdicts):
    converted = []

    for x in range(0, len(listofdicts)):
        converted.append({})

    for card in range(0, len(listofdicts)):
        converted[card]['Category_1'] = ffdeckstostring(listofdicts[card]['category'])
        converted[card]['Code'] = ffdeckstostring(listofdicts[card]['serial_number'])
        converted[card]['Cost'] = listofdicts[card]['cost']
        converted[card]['Ex_Burst'] = listofdicts[card]['is_ex_burst']
        converted[card]['Job_EN'] = ffdeckstostring(listofdicts[card]['job'])
        converted[card]['Multicard'] = listofdicts[card]['is_multi_playable']
        converted[card]['Name_EN'] = ffdeckstostring(listofdicts[card]['name'])
        converted[card]['Power'] = listofdicts[card]['power']
        converted[card]['Rarity'] = ffdeckstostring(listofdicts[card]['rarity'])[0]

        # Ffdecks sets element to null if it's a dual element card and then gives list of
        # elements under elements.
        if listofdicts[card]['element'] is None:
            element_text = ''
            for element in range(len(listofdicts[card]['elements'])):
                if element != len(listofdicts[card]['elements']) - 1:
                    element_text += listofdicts[card]['elements'][element] + "/"
                else:
                    element_text += listofdicts[card]['elements'][element]
            converted[card]['Element'] = element_text
        else:
            converted[card]['Element'] = ffdeckstostring(listofdicts[card]['element'])

        if re.search(r'^PR-', converted[card]['Code']):
            converted[card]['Set'] = None
        else:
            setnumber = int(re.search(r'^\d+', converted[card]['Code']).group(0))
            converted[card]['Set'] = 'Opus ' + roman.toRoman(setnumber)
        converted[card]['Type_EN'] = ffdeckstostring(listofdicts[card]['type'])
        converted[card]['Text_EN'] = []

        for line in range(0, len(listofdicts[card]['abilities'])):
            converted[card]['Text_EN'].append(ffdeckstostring(str(listofdicts[card]['abilities'][line])))
    return converted


def addimageurltojson(cards_list, image_list):
    for card in cards_list:
        for url in image_list:
            if re.search(r'\/', card['Code']):
                if card['Code'].split('/')[0] in url:
                    card['image_url'] = url
                    card['image_url_jp'] = None

            elif card['Code'] == re.search(r'(PR-\d{3}|\d+-\d{3}|B-\d{3}|C-\d{3})', url).group(1):
                card['image_url'] = url
                card['image_url_jp'] = None

    return cards_list


def addjapaneseurls(cards):
    #root_url = "http://www.square-enix-shop.com/jp/ff-tcg/card/cimg/large/opus"
    root_url = "https://storage.googleapis.com/marcieapi-images/jp/"
    regex = re.compile('([0-9]+)(-[0-9]+)([A-Z])')

    for card in cards:
        if re.search(regex, card['image_url']):
            set = re.search(regex, card['image_url']).group(1)
            cardnum = re.search(regex, card['image_url']).group(2)
            rarity = re.search(regex, card['image_url']).group(3)
            card['image_url_jp'] = root_url + set + cardnum + rarity + ".png"

    return cards


# This function makes a cards JSON from square and writes it to cards.json in the local directory
# LEGACY

def squaretomarcieapi(cards):
    mykeys = (
    'Rarity', 'Element', 'Name_EN', 'Cost', 'Multicard', 'Type_EN', 'Category_1', 'Text_EN', 'Job_EN', 'Power',
    'Ex_Burst', 'Set', 'Code')

    for card in cards:
        for key in list(card):
            if key in mykeys:
                if key == "Multicard" or key == "Ex_Burst":
                    card[key] = prettyTrice(card[key])
                    if card[key] == "True":
                        card[key] = True
                    else:
                        card[key] = False
                elif key == 'Power':
                    if card[key] == "":
                        card[key] = None
                    elif card[key] == " ":
                        card[key] = None
                    elif re.search(r'\u2015', card[key]):
                        card[key] = None
                    elif re.search(r'\－', card[key]):
                        card[key] = None
                    else:
                        card[key] = int(card[key])
                elif key == "Rarity":
                    if card[key]:
                        card[key] = card[key][0]
                    else:
                        card[key] = "T"
                elif key == "Code":
                    if re.search(r'^PR-\d{3}', card[key]):
                        card[key] = card[key]
                    elif re.search(r'\/', card[key]):
                        r = re.compile(r"^(.*?)([A-Z])(\/)(.*)") # Reprint logic only grab first (6-006C)/1-011C
                        card[key] = re.search(r, card[key]).group(1) # and strip letter output (6-006)
                    elif re.search(r'S', card[key]):
                        card['Rarity'] = 'S'
                        card[key] = card[key][:-1]
                    elif re.search(r'B', card[key]):
                        card['Rarity'] = 'B'
                        card[key] = card[key]
                    elif re.search(r'C-\d{3}', card[key]):
                        card['Rarity'] = "T"
                        card[key] = card[key]
                    else:
                        card[key] = card[key][:-1]
                elif key == "Cost":
                    if card[key]:
                        card[key] = int(card[key])
                    else:
                        card[key] = 0
                else:
                    card[key] = prettyTrice(card[key])
            else:
                del card[key]

        if card['Text_EN']:
            card['Text_EN'] = card['Text_EN'].split('\n')
            for line in range(len(card['Text_EN'])):
                card['Text_EN'][line] = re.sub(r'^\s+', '', card['Text_EN'][line])
                card['Text_EN'][line] = re.sub(r'\s+$', '', card['Text_EN'][line])
        else:
            card["Text_EN"] = None



    myjson = json.dumps(cards)
    mydict = json.loads(myjson)

    return mydict


# This function makes a cards JSON from square and writes it to cards.json in the local directory
# NEW WIP

def squaretomarcieapi2(cards):
    mykeys = (
    'Rarity', 'Element', 'Name_EN', 'Cost', 'Multicard', 'Type_EN', 'Category_1', 'Text_EN', 'Job_EN', 'Power',
    'Ex_Burst', 'Set', 'Code')

    key_map = [(key.lower(), key) for key in mykeys]
    output_cards = []

    for card in cards:
        output_card = {}
        for key in key_map:
            input_key = key[0]  #
            output_key = key[1]

            if input_key == "multicard" or input_key == "ex_burst":
                output_card[output_key] = prettyTrice(card[input_key])
                if output_card[output_key] == "True":
                    output_card[output_key] = True
                else:
                    output_card[output_key] = False

            elif input_key == "power":
                if card[input_key] == "":
                    output_card[output_key] = None
                elif card[input_key] == " ":
                    output_card[output_key] = None
                elif re.search(r'\u2015', card[input_key]):
                    output_card[output_key] = None
                elif re.search(r'\－', card[input_key]):
                    output_card[output_key] = None
                else:
                    output_card[output_key] = int(card[input_key])

            elif input_key == "rarity":
                if card[input_key]:
                    output_card[output_key] = card[input_key][0]
                else:
                    output_card[output_key] = "T"

            elif input_key == "code":
                if re.search(r'^PR-\d{3}', card[input_key]):
                    output_card[output_key] = card[input_key]
                elif re.search(r'\/', card[input_key]):
                    r = re.compile(r"^(.*?)([A-Z])(\/)(.*)") # Reprint logic only grab first (6-006C)/1-011C
                    output_card[output_key] = re.search(r, card[input_key]).group(1) # and strip letter output (6-006)
                elif re.search(r'S', card[input_key]):
                    output_card['rarity'] = 'S'
                    output_card[output_key] = card[input_key][:-1]
                elif re.search(r'B', card[input_key]):
                    output_card['rarity'] = 'B'
                    output_card[output_key] = card[input_key]
                elif re.search(r'C-\d{3}', card[input_key]):
                    output_card['rarity'] = "T"
                    output_card[output_key] = card[input_key]
                else:
                    output_card[output_key] = card[input_key][:-1]

            elif input_key == "cost":
                if card[input_key]:
                    output_card[output_key] = int(card[input_key])
                else:
                    output_card[output_key] = 0

            elif input_key == "element":
                if card[input_key]:
                    element = prettyTrice("/".join(card[input_key]))
                else:
                    element = None

                output_card[output_key] = element

            elif input_key == "text_en":
                if card[input_key]:
                    output_card[output_key] = prettyTrice(card[input_key]).split('\n')
                    for line in range(len(output_card[output_key])):
                        output_card[output_key][line] = re.sub(r'^\s+', '', output_card[output_key][line])
                        output_card[output_key][line] = re.sub(r'\s+$', '', output_card[output_key][line])
                else:
                    output_card[output_key] = None

            elif input_key == "category_1":
                if card[input_key]:
                    output_card[output_key] = prettyTrice(card[input_key])
                else:
                    output_card[output_key] = None

            else:
                output_card[output_key] = prettyTrice(card[input_key])

        output_cards.append(output_card)

    return output_cards
