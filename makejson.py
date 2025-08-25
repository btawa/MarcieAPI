from marcie_helper_new import process_square_cards, process_ffdecks_promos


def pull_ffdecks_promos() -> list:
    try:
        return process_ffdecks_promos('https://ffdecks.com/api/card/game-language/1')
    except:
        return []


def pull_square_cards() -> list:
    try:
        return process_square_cards('https://fftcg.square-enix-games.com/en/get-cards')
    except:
        return []


def combine_cards(card_group_1, card_group_2) -> list:
    return card_group_1 + card_group_2
