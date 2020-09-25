from gym_spades.envs.spades.player import player
from gym_spades.envs.spades.spades import cards, spades

# example player - a human!

class human(player):
    suits = ['S', 'H', 'C', 'D']
    # humans have no choice for bidding - sorry!
    def _play(self, state, round):
        print("The round so far:\t", [cards.card_str(c) for c in round])
        print("Your hand:\t", [cards.card_str(c) for c in self.hand])
        while True:
            print("What card will you play? (S,H,C,D for suit, eg 10H)")
            card = input()
            suit = human.suits.index(card[-1])
            rank = int(card[0:-1])
            card = cards.create_card(rank, suit)
            if card in self.hand:
                return card
            print("Invalid card! Please select a card in your hand:", [cards.card_str(c) for c in self.hand])


