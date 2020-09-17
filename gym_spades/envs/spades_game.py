import random

RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
SUITS = ['♠', '♥', '♦', '♣']
SPADES = 0
# spades, hearts, diamonds, clubs
NOCARD = 52

BID = 0
PLAY = 1
GAMEOVER = 2

def rank(card):
    return card % 13

def suit(card):
    return card // 13

def card_str(card):
    return RANKS[rank(card)] + SUITS[suit(card)]

class player:

    def __init__(self):
        self.action = -1

    def set_game(self, game):
        self.game = game
   
    def set_index(self, index):
        self.index = index
    
    def set_hand(self, hand):
        self.hand = hand

    def bid(self):
        return 0

    def play(self, round):
        return self.play_randomly[0]
    
    def _play(self, round):
        return self.play()

    def play_randomly(self):
        cards = self.get_legal_actions()
        card = random.choice(cards)
        #card = self.play(round)
        self.hand.remove(card)
        return card

    def get_legal_actions(self):
        if self.game.num_played == 0:
            return self.hand
        start_suit = suit(self.game.round[0])
        legal_cards = []
        for card in self.hand:
            if suit(card) == start_suit:
                legal_cards.append(card)
        if len(legal_cards) == 0:
            return self.hand
        return legal_cards

    def result(self, trick, starting_player, took_trick):
        return

    def game_end(self, trick_taken, points):
        return

class spades:

    def __init__(self, players):
        self.players = players

        # keep track of each player's bid and number of taken tricks
        self.bids = [0] * 4
        self.tricks = [0] * 4

        # cards played in round
        self.round = []
        self.num_played = 0

        # number of rounds played
        self.round_counter = 0

        self.reset()

    def reset(self, shuffle_players = False):
        # shuffle the deck and send it to everyone
        self.deck = [i for i in range(52)]
        random.shuffle(self.deck)

        if shuffle_players:
            random.shuffle(players)

        for i in range(4):
            self.players[i].set_hand(self.deck[i*13 : (i+1)*13])
            self.players[i].set_index(i)
            self.players[i].set_game(self)

        self.starting_player = 0

        self.mode = BID

    def print(self):
        for i in range(4):
            print('Player ' + str(i) + ':')
            cards = ''
            for card in self.players[i].hand:
                cards += card_str(card) + ' '
            print(cards)

    def next_player(self, p):
        return (p + 1) % 4

    def place_bid(self, player, bid):
        assert player == self.next_player(self.starting_player + self.num_played)
        self.bid[self.num_played] = bid
        self.num_played += 1

    def play_card(self, player, card):
        assert player == self.next_player(self.starting_player + self.num_played)
        self.round.append(card)
        self.num_played += 1
        
    def step(self):
        if self.mode == BID:
            return self.players[self.starting_player + self.num_played], self.bids

    # Not recommended
    def play_round(self):
        if self.round_counter == 13:
            print("ERROR: game over")

        self.round = [0]*4
        p = self.starting_player
        for i in range(4):
            self.round[i] = self.players[p]._play(self.round)
            p = self.next_player(p)
            self.num_played += 1

        # who won?
        p = self.starting_player
        winning = 0
        for i in range(1,4):
            p = self.next_player(p)
            # same suit as winning? (will be spades if played, else lead suit)
            if suit(self.round[p]) == suit(self.round[winning]):
                # played higher card?
                if self.round[p] > self.round[winning]:
                    winning = p
            elif suit(self.round[p]) == SPADES:
                winning = p

        print([card_str(c) for c in self.round], self.starting_player, winning)
        
        self.starting_player = winning

        # round over, send results
        for player in self.players:
            player.result(round, self.starting_player, player == winning)

        self.round_counter += 1

    def game_over(self):
        return self.round_counter == 13


if __name__ == "__main__":
    players = [0]*4
    for i in range(4):
        players[i] = player()

    g = spades(players)
    g.print()