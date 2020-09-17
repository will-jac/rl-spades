import random

import gym_spades.envs.spades.Player

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
    # spades, hearts, diamonds, clubs
    SPADES = 0
    HEARTS = 1
    DIAMONDS = 3
    CLUBS = 4

    SUITS = [SPADES, HEARTS, DIAMONDS, CLUBS]
    
    SUIT_STRING = ['♠', '♥', '♦', '♣']

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
        return RANKS[rank(card)] + SUIT_STRING[suit(card)]


class spades:
    BID = 0
    PLAY = 1
    GAMEOVER = 2

    NIL = 0

    def __init__(self, players):
        # the agents
        self.players = players

        self.reset()

    # reset the game to pay again
    def reset(self, shuffle_players = False):

        # keep track of the number of tricks taken
        self.tricks = [0] * 4

        # cards played in round
        self.round = []
        # number of players that have played
        self.num_played = 0

        # number of rounds played
        self.round_counter = 0

        # shuffle the deck and send it to everyone
        self.deck = cards.create_deck()

        if shuffle_players:
            random.shuffle(players)

        for i in range(4):
            self.players[i].set_hand(self.deck[i*13 : (i+1)*13])

        self.starting_player = 0

        self.mode = BID

    def print(self):
        for i in range(4):
            print('Player ' + str(i) + ':')
            cards = ''
            for card in self.players[i].hand:
                cards += deck.card_str(card) + ' '
            print(cards)

    def _next_player(self, p):
        return (p + 1) % 4

    def bid_round(self):
        assert self.mode == spades.BID
        
        self.bids = []

        for i in range(4):
            self.bids.append(self.players[i].bid(self.bids))

    # play a round of spades, eg one trick
    def play_round(self):
        assert self.round_counter < 13 and self.mode == spades.PLAY

        self.round = []

        p = self.starting_player
        for i in range(4):
            state = self._build_state(p)
            self.round.append(self.players[p].play(state))
            p = self.next_player(p)

        winning = _take_trick()

        #print([card_str(c) for c in self.round], self.starting_player, winning)

        self.starting_player = winning
        self.round_counter += 1

        # return the (index of the) player that took the round
        return winning

    def _take_trick(self):
        # who won the trick?
        p = self.starting_player
        winning = 0
        for i in range(1,4):
            p = self.next_player(p)
            # same suit as winning? (will be spades if played, else lead suit)
            if cards.suit(self.round[p]) == cards.suit(self.round[winning]):
                # played higher card?
                if self.round[p] > self.round[winning]:
                    winning = p
            elif cards.suit(self.round[p]) == cards.SPADES:
                winning = p
        return winning

    def game_over(self):
        return self.round_counter == 13

    def _build_state(self, player):
        # a --really-- simplistic state
        return [self.round, self.players[player].hand]


if __name__ == "__main__":
    players = [0]*4
    for i in range(4):
        players[i] = player()

    g = spades(players)
    g.print()