import random
#from gym_spades.envs.spades import cards, player

class spades:
    BID = 0
    PLAY = 1
    GAMEOVER = 2

    NIL = 0

    NO_LEAD = 4

    def __init__(self, players):
        # the agents
        self.players = players
        self.shuffle_players = True
        self.game_starting_player = 0

    # reset the game to pay again
    def reset(self):
        from gym_spades.envs.spades.cards import cards

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

        if self.shuffle_players:
            self.game_starting_player = random.randrange(0,4)
        self.starting_player = self.game_starting_player

        for i in range(4):
            self.players[i].reset(i, self.deck[i*13 : (i+1)*13])

        self.mode = spades.BID

        # some other tracking stuff
        self.player_played_off_in_suit = [[0]*4 for i in range(4)]
        self.num_suit_lead_in_round = [0]*4

        self.tricks_won = [0 for _ in range(4)]

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
        self.players[0].opponent_team_bid = t1
        self.players[1].team_bid = t1
        self.players[1].opponent_team_bid = t0
        self.players[2].team_bid = t0
        self.players[2].opponent_team_bid = t1
        self.players[3].team_bid = t1
        self.players[3].opponent_team_bid = t0

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

        #print(self.round_counter, [len(p.hand) for p in self.players])

        self.round_so_far = []

        self.suit_lead = spades.NO_LEAD
        self.spades_played = False

        p = self.starting_player

        self.winning = p
        self.winning_suit = cards.SPADES
        self.winning_rank = cards.ACE

        for i in range(4):
            #print(i)
            c = self.players[p].play(self)
            self.round_so_far.append(c)

            s = cards.suit(c)
            r = cards.rank(c)
            #print("\t", cards.card_str(c))
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

        self.tricks_won[self.winning] += 1

        # send info to players
        for p in self.players:
            p.set_reward(self.winning)
        #print("winning:", self.winning)
        # self.players[self.winning].set_reward()
        # self.players[(self.winning + 2) % 4].set_reward()
        # self.players[(self.winning + 1) % 4].set_reward()
        # self.players[(self.winning + 3) % 4].set_reward()

        if self.round_counter < 13:
            return True
        else:
            self.mode = spades.GAMEOVER
            return False

    def end_game(self):
        # call the _play function for the backups
        # and compute score
        points = [0 for _ in range(4)]

        for i,p in enumerate(self.players):
            p._play(None)
            if p.bid_amount == 0:
                if self.tricks_won[i] == 0:
                    points[i] = 100
                else:
                    points[i] = -100

        # now, do team points
        a_tricks = self.tricks_won[0] + self.tricks_won[2]
        b_tricks = self.tricks_won[1] + self.tricks_won[3]
        if a_tricks < self.players[0].team_bid:
            points[0] -= 10 * self.players[0].team_bid
        else:
            points[0] += 10 * self.players[0].team_bid
            rem = a_tricks - self.players[0].team_bid
            points[0] += rem

        if b_tricks < self.players[1].team_bid:
            points[1] -= 10 * self.players[1].team_bid
        else:
            points[1] += 10 * self.players[1].team_bid
            rem = b_tricks - self.players[1].team_bid
            points[1] += rem

        a_points = points[0] + points[2]
        b_points = points[1] + points[3]

        self.players[0].points_hist.append(a_points)
        self.players[1].points_hist.append(b_points)
        self.players[2].points_hist.append(a_points)
        self.players[3].points_hist.append(b_points)

        # set the next starting player
        self.game_starting_player = self._next_player(self.game_starting_player)
        # shouldn't shuffle players now, because next round just continues
        self.shuffle_players = False

    def is_game_over(self):
        return self.round_counter == 13 and self.mode == spades.GAMEOVER

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