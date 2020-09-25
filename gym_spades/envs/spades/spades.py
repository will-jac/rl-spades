import random

from gym_spades.envs.spades.player import player

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
    CLUBS = 3
    DIAMONDS = 4
    
    SUITS = [SPADES, HEARTS, CLUBS, DIAMONDS]
    
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

    @staticmethod
    def create_card(rank, suit):
        return rank + (suit * 13)

class spades:
    BID = 0
    PLAY = 1
    GAMEOVER = 2

    NIL = 0

    NO_LEAD = 4

    def __init__(self, players):
        # the agents
        self.players = players

        self.reset()

    # reset the game to pay again
    def reset(self, shuffle_players = False):

        # keep track of the number of tricks taken
        self.tricks = [0] * 4
        # keep track of all the rounds that happened
        self.round_history = []

        # keep track of the discard (same as above, but by suit)
        self.discard_by_suit = [[] for i in range(4)]

        # cards played in round
        self.round = []
        # number of players that have played
        self.num_played = 0

        # number of rounds played
        self.round_counter = 0

        self.spades_broken = False

        # shuffle the deck and send it to everyone
        self.deck = cards.create_deck()

        if shuffle_players:
            random.shuffle(players)

        for i in range(4):
            self.players[i].set_hand(self.deck[i*13 : (i+1)*13])
            self.players[i].set_index(i)

        self.starting_player = 0

        self.mode = BID

        # some other tracking stuff
        self.player_played_off_in_suit = [[0]*4 for i in range(4)]
        self.num_suit_lead_in_round = [0]*4

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
        t1 = self.bids[0] + self.bids[2]
        t2 = self.bids[1] + self.bids[3]
        self.is_over_bid

    # play a round of spades, eg one trick
    def play_round(self):
        assert self.round_counter < 13 and self.mode == spades.PLAY

        self.round = []

        self.suit_lead = spades.NO_LEAD 
        self.spades_played = False

        p = self.starting_player
        
        self.winning = p
        self.winning_suit = cards.SPADES
        self.winning_rank = cards.ACE

        for i in range(4):
            state = self.get_state(self.players[p])
            c = self.players[p].play(state)
            self.round.append(c)

            s = cards.suit(c) 
            r = cards.rank(c)
            self.discard_by_suit[r].append(c)
            self.discard_by_suit[r].sort()
            p = self.next_player(p)

            # determine which card is winning
            # and do other tracking stuff
            if i == 0:
                self.suit_lead = cards.suit(c)  
                self.winning = p
                self.winning_suit = s
                self.winning_rank = r
                self.num_suit_lead_in_round[s] += 1
            else:
                if s != self.suit_lead:
                    self.player_played_off_in_suit[p][self.suit_lead] = 1
                if s == self.winning_suit:
                    if r > self.winning_rank:
                        self.winning = p
                        self.winning_suit = s
                        self.winning_rank = r
                elif s == cards.SPADES:
                    self.spades_played = True
                    self.spades_broken = True
                    self.winning = p
                    self.winning_suit = s
                    self.winning_rank = r

        self.starting_player = self.winning
        
        # store the round info
        self.tricks[winning] += 1
        self.round_history.append(self.round)
        self.round_counter += 1

        # return the (index of the) player that took the round
        return winning

    def game_over(self):
        return self.round_counter == 13

    def _build_state(self, player):
        # a --really-- simplistic state
        return [self.round, player.hand]

    def have_highest_card_in_lead_suit(self, player):
        if len(self.round) == 0:
            # it's our lead
            # do we have the highest card in any suit?
            for s in range(4):
                i = -1
                for r in range(cards.ACE, cards.TWO, -1):
                    if self.discard_by_suit[s][i] == r:
                        continue
                    elif r in player.hand:
                        return True
                    else:
                        break
            return False
        
        # someone else has already lead
        s = cards.suit(round[0])
        i = -1
        for r in range(cards.ACE, cards.TWO, -1):
            if self.discard_by_suit[s][i] == r:
                continue
            elif r in round:
                return False
            elif r in player.hand:
                return True
            else:
                return False

    def can_win(self, player, have_highest):
        if self.suit_lead == spades.NO_LEAD:
            return True

        can_play_spades = True
        can_win_spades = False
        for c in player.hand:
            if cards.suit(c) == self.suit_lead:
                can_play_spades = False
                if cards.rank(c) > cards.rank(self.round[0]):
                    return True
            elif cards.suit(c) == cards.SPADES:
                if self.spades_played:
                    if cards.rank(c) > self.winning_rank:
                        can_win_spades = True
                else:
                    can_win_spades = True

        if can_play_spades:
            return can_win_spades

    def smallest_suit(self, player):
        suits_in_hand = [0]*4
        for c in player.hand:
            suits_in_hand[cards.suit(c)] += 1
        smallest = 14
        suit = cards.CLUBS
        for s in suits_in_hand:
            if s < smallest:
                suit = cards.SUITS[s]
                smallest = s
        return suit
        
if __name__ == "__main__":
    players = [0]*4
    for i in range(4):
        players[i] = player()

    g = spades(players)
    g.print()