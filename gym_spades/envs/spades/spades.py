import random

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
        from gym_spades.envs.spades.cards import cards
        from gym_spades.envs.spades.player import player

        # keep track of the number of tricks taken
        self.tricks = [0] * 4
        # keep track of all the rounds that happened
        self.round_history = []

        # keep track of the discard (same as above, but by suit)
        self.discard_by_suit = [[] for i in range(4)]

        # cards played in round
        self.round_so_far = []
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
            self.players[i].set_index(i)
            self.players[i].set_hand(self.deck[i*13 : (i+1)*13])

        self.starting_player = 0

        self.mode = spades.BID

        # some other tracking stuff
        self.player_played_off_in_suit = [[0]*4 for i in range(4)]
        self.num_suit_lead_in_round = [0]*4

    def print(self):
        from gym_spades.envs.spades.cards import cards
        
        for i in range(4):
            print('Player ' + str(i) + ':')
            cards = ''
            for card in self.players[i].hand:
                cards += deck.card_str(card) + ' '
            print(cards)

    def _next_player(self, p):
        return (p + 1) % 4

    def bid_round(self):
        from gym_spades.envs.spades.player import player

        assert self.mode == spades.BID
        
        self.bids = []

        for i in range(4):
            self.bids.append(self.players[i].bid(self.bids))
        t0 = self.bids[0] + self.bids[2]
        t1 = self.bids[1] + self.bids[3]

        self.players[0].team_bid = t0
        self.players[1].team_bid = t1
        self.players[2].team_bid = t0
        self.players[3].team_bid = t1

        if (t0 + t1) > 13:
            self.is_over_bid = True
        else:
            self.is_over_bid = False
        
        self.mode = spades.PLAY

    # play a round of spades, eg one trick
    def play_round(self):
        from gym_spades.envs.spades.cards import cards
        from gym_spades.envs.spades.player import player

        assert self.round_counter < 13 and self.mode == spades.PLAY

        self.round_so_far = []

        self.suit_lead = spades.NO_LEAD 
        self.spades_played = False

        p = self.starting_player
        
        self.winning = p
        self.winning_suit = cards.SPADES
        self.winning_rank = cards.ACE

        for i in range(4):
            c = self.players[p].play(self)
            self.round_so_far.append(c)

            s = cards.suit(c) 
            r = cards.rank(c)
            print("played:", cards.card_str(c))
            self.discard_by_suit[s].append(c)
            self.discard_by_suit[s].sort()

            # determine which card is winning
            # and do other tracking stuff
            if i == 0:
                self.suit_lead = cards.suit(c)  
                self.winning = p
                self.winning_suit = s
                self.winning_rank = r
                self.num_suit_lead_in_round[s] += 1
                if s == cards.SPADES:
                    self.spades_broken = True
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

            p = self._next_player(p)

        self.starting_player = self.winning
        
        # store the round info
        self.tricks[self.winning] += 1
        self.round_history.append(self.round_so_far)
        self.round_counter += 1

        # send info to players
        self.players[self.winning].team_tricks += 1
        self.players[(self.winning + 2) % 4].team_tricks += 1
        # return the (index of the) player that took the round
        return self.winning

    def game_over(self):
        return self.round_counter == 13

    def _build_state(self, player):
        # a --really-- simplistic state
        return [self.round_so_far, player.hand]

    def have_highest_card_in_lead_suit(self, player):
        from gym_spades.envs.spades.cards import cards
        from gym_spades.envs.spades.player import player

        if len(self.round_so_far) == 0:
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
        from gym_spades.envs.spades.cards import cards
        from gym_spades.envs.spades.player import player

        if self.suit_lead == spades.NO_LEAD:
            return True

        can_play_spades = True
        can_win_spades = False
        for c in player.hand:
            if cards.suit(c) == self.suit_lead:
                can_play_spades = False
                if cards.rank(c) > cards.rank(self.round_so_far[0]):
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
        from gym_spades.envs.spades.cards import cards
        from gym_spades.envs.spades.player import player

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
    from gym_spades.envs.spades import spades
    from gym_spades.envs.spades import player
    from gym_spades.envs.agents import human
    from gym_spades.envs.agents import fa_agent

    players = [fa_agent(), fa_agent(), fa_agent(), fa_agent()]
    game = spades(players)
    game.bid_round()
    print(game.bids)
    game.play_round()