import time

from makejson import pull_ffdecks_promos, pull_square_cards, combine_cards


class CardClient():
    def __init__(self):
        self.cards = []
        self.lastfetch = time.time()
        self.lock = False

    def pull_new_cards(self):
        self.cards = combine_cards(pull_square_cards(),pull_ffdecks_promos())
        self.lastfetch = time.time()
        self.lock = False

    def init(self):
        self.pull_new_cards()

