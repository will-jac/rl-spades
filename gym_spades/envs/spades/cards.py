import random

class cards:
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12
    RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    # spades, hearts, clubs, diamonds 
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3
    
    SUITS = [SPADES, HEARTS, CLUBS, DIAMONDS]
    
    SUIT_STRING = ['♠', '♥', '♣', '♦']

    NOCARD = 52

    @staticmethod
    def create_deck():
        deck = [i for i in range(52)]
        random.shuffle(deck)
        return deck

    @staticmethod
    def rank(card):
        return card % 13

    @staticmethod
    def suit(card):
        return card // 13

    @staticmethod
    def card_str(card):
        return cards.RANKS[cards.rank(card)] + cards.SUIT_STRING[cards.suit(card)]

    @staticmethod
    def create_card(rank, suit):
        return rank + (suit * 13)
