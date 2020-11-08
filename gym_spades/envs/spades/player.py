import random
import itertools
from gym_spades.envs.spades import cards

class player:

    def __init__(self):
        self.name = 'player'
        self.rewards = []
        self.game_count = 0
        self.total_rewards = 0
        self.team_bid = 0
        self.opponent_team_bid = 0
        self.bid_random = False
        self.points_hist = []

    def result(self):
        return [self.rewards]

    def reset(self, index, hand):
        self.index = index
        self.partner_index = (index + 2) % 4

        # sorted hand
        self.hand = hand
        self.hand.sort()
        # sorted hand by suit
        self.hand_by_suit = [[] for _ in range(4)]
        for c in self.hand:
            self.hand_by_suit[cards.suit(c)].append(c)
        for s in self.hand_by_suit:
            s.sort()

        # initialize some variables
        self.team_tricks = 0
        self.team_bid = -1
        self.bid_amount = -1

        self.game_count += 1

        self.total_rewards += sum(self.rewards)
        self.avg_rewards = self.total_rewards / self.game_count

        self.rewards = []

        self.reward = None

        self.can_make_bid = True
        self.lost_bid = False

    # default action: a random player
    def play(self, game) -> cards:
        c = self._play(game)
        #print("\t", self.index, "  ",cards.card_str(c), "  ", [cards.card_str(c) for c in self.hand])
        try:
            self.hand.remove(c)
        except ValueError:
            print(self.name, 'encountered an ERROR', self.index, self.bid_amount)
            print('error removing ' + str(c) + ' from hand ' + str(self.hand))
            print('round so far:', game.starting_player, game.round_so_far, 'spades broken:', game.spades_broken)
            print([cards.card_str(c) for c in self.hand])

        try:
            self.hand_by_suit[cards.suit(c)].remove(c)
        except ValueError:
            print(self.hand_by_suit)

        return c

    def _play(self, game):
        if game is None:
            return 0

        cards = self.get_legal_cards(game)
        return random.choice(cards)

    def get_legal_cards(self, game):
        # if it's our lead, we can do anything
        if len(game.round_so_far) == 0:
            if not game.spades_broken:
                legal_cards = self.hand_by_suit[1] + self.hand_by_suit[2] + self.hand_by_suit[3]
                if len(legal_cards) == 0:
                    return self.hand
                else:
                    return legal_cards
            else:
                return self.hand
        # must follow lead if we can
        legal_cards = []
        if len(self.hand_by_suit[game.suit_lead]) > 0:
            legal_cards = self.hand_by_suit[game.suit_lead]
        else:
            # if we can't follow suit, we can do anything
            return self.hand

        if len(legal_cards) == 0:
            # if we have no legal cards, we can do anything
            return self.hand

        return legal_cards

    def set_reward(self, winning_player):
        return

    # bid ==> rule-based agent
    # https://arxiv.org/pdf/1912.11323v1.pdf
    # 5.1, Competing Algorithms (RB), and G.1, G.2
    def bid(self, current_bids):
        liability_by_suits = [0]*4
        points = 0
        # determine points in hand
        for i in range(4):
            l = len(self.hand_by_suit[i])
            for j, c in enumerate(self.hand_by_suit[i]):
                # nil classifier (G.2)
                r = cards.rank(c)
                if j == 0:
                    if r > cards.FIVE:
                        liability_by_suits[i] += 1
                elif j == 1:
                    if r > cards.EIGHT:
                        liability_by_suits[i] += 1
                elif j == 2:
                    if r > cards.TEN:
                        liability_by_suits[i] += 1
                # points classifier (G.1)
                if r == cards.ACE:
                    # ace = 1 trick
                    #print("ace point", i)
                    points += 1
                elif l > 1 and r == cards.KING:
                    # non-singleton king = 1 trick
                    #print("king point", i)
                    points += 1
                elif l > 1 and r == cards.QUEEN and i == cards.SPADES:
                    # non-singleton queen of spades
                    if l > 2:
                        # non-doubleton queen of spades = 1 trick
                        #print("queen point a", i)
                        points += 1
                    elif j != l - 1 and cards.rank(self.hand_by_suit[i][j+1]) == cards.ACE:
                        # doubleton queen of spades + ace of spades = 1 trick
                        #print("queen point b", i)
                        points += 1

        spades_count = len(self.hand_by_suit[cards.SPADES])

        # This part is a small deviation from the paper: we will bid nil if the liabilities can be overcome
        can_overcome_liabilities = 0
        for i in range(4):
            # if we have an empty suit, we can overcome a liability
            if len(self.hand_by_suit[i]) == 0:
                can_overcome_liabilities += 1
            # if we only have one card in a suit (and it's not a liability), we can probably overcome a liability
            elif len(self.hand_by_suit[i]) == 1 and liability_by_suits[i] == 0:
                can_overcome_liabilities += 0.5

        #print("liabilities by suit:", liability_by_suits, "can overcome:", can_overcome_liabilities)
        # should we bid nil?
        if liability_by_suits[cards.SPADES] == 0 and len(self.hand_by_suit[cards.SPADES]) < 4:
            # cannot overcome liabilities in spades (trump) via sluffing off
            # check for A K of spades
            if (spades_count > 1 and self.hand_by_suit[cards.SPADES][-1] < cards.KING \
                    and self.hand_by_suit[cards.SPADES][-2] < cards.KING):
                for i in range(1, 4): # the rest of the suits, spades == 0
                    if liability_by_suits[i] > 0 and can_overcome_liabilities > 0:
                        # how deep in the suit are we?
                        if len(self.hand_by_suit[i]) > 1.5*liability_by_suits[i]:
                            # _maybe_ deep enough
                            diff = (liability_by_suits[i] - can_overcome_liabilities) // 1
                            if diff <= 0:
                                # we can overcome the liability via sluffing off!
                                liability_by_suits[i] = 0
                                can_overcome_liabilities -= -1 * diff
                                # eg: l = 1, c = 1, => diff = 0, c' = 0
                                # ef: l = 1, c = 2, => diff = -1, c' = 1
                liability = sum(liability_by_suits)
                if liability == 0:
                    # bid nil
                    #print("bidding nil")
                    self.bid_amount = 0
                    return self.bid_amount

        # not bidding nil, so determine what we _are_ bidding

        # add in spades bids
        if spades_count < 2:
            #print("spades -= 1")
            points -= 1
        elif spades_count > 3:
            #print("spades +=", (spades_count - 3))
            points += (spades_count - 3)
        elif spades_count == 3:
            # 3 spades + void or singleton in side suit
            for i in range(1, 4): # the rest of the suits, spades == 0
                if len(self.hand_by_suit[i]) < 2:
                    #print("points += 1")
                    points += 1

        # add some randomness?
        # only used when training
        if self.bid_random:
            r = random.choice([-1,0,1])
            #print("random =", r)
            points += r

        if points > 13:
            points = 13
        elif points <= 0:
            points = 1

        #print("bidding ", points)
        self.bid_amount = points
        return self.bid_amount
