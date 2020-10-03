from hearthstone.deckstrings import Deck
from hearthstone.enums import FormatType

class HearthStoneDeck():
    def __init__(self, hero, cards, format=FormatType.FT_STANDARD):
        self.deck = Deck()
        self.heroes = hero
        self.format = format
        self.cards = cards

    def getHeroesId(self, str):
        heroes = {'Druid': 274, 'Hunter': 31, 'Mage': 637, 'Paladin': 671, 'Priest': 813, 'Rogue': 930,
                  'Shaman': 1066, 'Warlock': 893, 'Warrior': 7, 'Demonhunter':56550}
        return heroes.get(str.capitalize())

    def genDeckString(self):
        self.deck.heroes = [self.getHeroesId(self.heroes)]
        self.deck.format = self.format
        self.deck.cards = self.cards
        deckstring = self.deck.as_deckstring
        print(deckstring)
        return deckstring


