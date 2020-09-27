import random
import itertools
from gym_spades.envs.spades import spades

class player:

    bid_random = True

    def get_state(self):
        ...

    def set_index(self, index):
        self.index = index
    
    def set_hand(self, hand):
        from gym_spades.envs.spades import cards

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

    # default action: a random player
    def play(self, game):
        from gym_spades.envs.spades import cards

        c = self._play(game)
        self.hand.remove(c)
        self.hand_by_suit[cards.suit(c)].remove(c)
        return c

    def _play(self, game):
        cards = self.get_legal_cards(game)
        return random.choice(cards)

    def game_end(self, trick_taken, points):
        return

    def get_legal_cards(self, game):
        from gym_spades.envs.spades import cards

        # if it's our lead, we can do anything
        if len(game.round_so_far) == 0:
            if game.spades_broken:
                return list(itertools.chain.from_iterable([
                    self.hand_by_suit[1],self.hand_by_suit[2],self.hand_by_suit[3],
                ]))
            else:
                return self.hand
        # must follow lead if we can
        legal_cards = []
        if len(self.hand_by_suit[game.suit_lead]) > 0:
            legal_cards = self.hand_by_suit[game.suit_lead]
        else:
            # if we can't follow suit, we can do anything
            return self.hand
        
        return legal_cards

    # bid ==> rule-based agent
    # https://arxiv.org/pdf/1912.11323v1.pdf
    # 5.1, Competing Algorithms (RB), and G.1, G.2
    def bid(self, current_bids):
        from gym_spades.envs.spades import cards

        if True:
            print("Player", self.index, ":", [cards.card_str(c) for c in self.hand])

        #self.hand.sort()

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
                    print("ace point", i)
                    points += 1
                elif l > 1 and r == cards.KING:
                    # non-singleton king = 1 trick
                    print("king point", i)
                    points += 1
                elif l > 1 and r == cards.QUEEN and i == cards.SPADES:
                    # non-singleton queen of spades
                    if l > 2:
                        # non-doubleton queen of spades = 1 trick
                        print("queen point a", i)
                        points += 1
                    elif j != l - 1 and cards.rank(self.hand_by_suit[i][j+1]) == cards.ACE:
                        # doubleton queen of spades + ace of spades = 1 trick
                        print("queen point b", i)
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

        print("liabilities by suit:", liability_by_suits, "can overcome:", can_overcome_liabilities)
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
                    print("bidding nil")
                    self.bid_amount = spades.NIL
                    return self.bid_amount
        
        # not bidding nil, so determine what we _are_ bidding

        # add in spades bids
        if spades_count < 2:
            print("spades -= 1")
            points -= 1
        elif spades_count > 3:
            print("spades +=", (spades_count - 3))
            points += (spades_count - 3)
        elif spades_count == 3:
            # 3 spades + void or singleton in side suit
            for i in range(1, 4): # the rest of the suits, spades == 0
                if len(self.hand_by_suit[i]) < 2:
                    print("points += 1")
                    points += 1
        
        # cannot bid 0
        if points <= 0:
            print("was 0, now bidding 1")
            self.bid_amount = 1
            return self.bid_amount

        # add some randomness?
        # only used when training
        if player.bid_random:
            r = random.choice([-1,0,1])
            print("random =", r)
            points += r

        print("bidding ", points)
        self.bid_amount = points
        return self.bid_amount