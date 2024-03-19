from marcie_helper import *


def pull_ffdecks_promos() -> list:
    ffdecks = loadFfdecks('https://ffdecks.com/api/cards/basic')
    cards = ffdeckstomarcieapi(ffdecks['cards'])
    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)
    cards = addjapaneseurls(cards)
    promos = []

    for card in cards:
        if re.search(r'^PR-[0-9]+', card['Code']):
            promos.append(card)

    return promos


def pull_ffdecks_cards() -> list:
    ffdecks = loadFfdecks('https://ffdecks.com/api/cards/basic')
    cards = ffdeckstomarcieapi(ffdecks['cards'])
    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)
    cards = addjapaneseurls(cards)
    promos = []
    non_promos = []


    for card in cards:
        if re.search(r'PR-0[1-9]', card['Code']):
            promos.append(card)
        else:
            non_promos.append(card)

    return non_promos


def pull_square_cards() -> list:
    square = loadSquare('https://fftcg.square-enix-games.com/en/get-cards')
    cards = squaretomarcieapi2(square['cards']) # 2 is after Opus 21 Changes

    # Remove Duplicates
    added_codes = []
    result = []
    for card in cards:
        if card['Code'] not in added_codes:
            added_codes.append(card['Code'])
            result.append(card)


    cards = result

    imageurlset = urlset(cards)
    cards = addimageurltojson(cards, imageurlset)
    cards = addjapaneseurls(cards)

    return cards


def combine_cards(card_group_1, card_group_2) -> list:
    return card_group_1 + card_group_2
