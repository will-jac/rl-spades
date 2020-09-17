import random
from gym_spades.envs.spades.spades import cards, spades

class player:

    def __init__(self):
        assert False
    
    def set_hand(self, hand):
        self.hand = hand

    def play(self, state):
        return self.play_randomly[0]

    def play_randomly(self):
        cards = self.get_legal_actions()
        card = random.choice(cards)
        #card = self.play(round)
        self.hand.remove(card)
        return card

    def get_legal_actions(self):
        if self.game.num_played == 0:
            return self.hand
        start_suit = cards.suit(self.game.round[0])
        legal_cards = []
        for card in self.hand:
            if cards.suit(card) == start_suit:
                legal_cards.append(card)
        if len(legal_cards) == 0:
            return self.hand
        return legal_cards

    def game_end(self, trick_taken, points):
        return

    # bid ==> rule-based agent
    # https://arxiv.org/pdf/1912.11323v1.pdf
    # 5.1, Competing Algorithms (RB), and G.1, G.2
    def bid(self, current_bids):
        self.hand.sort()
        # go through the hand by suit
        hand_by_suits = [[] for i in range(4)]

        for card in self.hand:
            suit = cards.suits[card]
            hand_by_suits[suit].append(card)

        liability_by_suits = [0]*4
        points = 0
        # determine points in hand
        for i in range(4):
            l = len(hand_by_suits[i]) - 1
            for j in range(hand_by_suits[i]):
                # nil classifier (G.2)
                r = cards.rank(hand_by_suits[i][j])
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
                    points += 1
                elif l > 1 and r == cards.KING:
                    # non-singleton king = 1 trick
                    points += 1
                elif l > 1 and r == cards.QUEEN and i == cards.SPADES:
                    # non-singleton queen of spades
                    if l > 2:
                        # non-doubleton queen of spades = 1 trick
                        points += 1
                    elif j != l - 1 and r == cards.ACE:
                        # doubleton queen of spades + ace of spades = 1 trick
                        points += 1

        # Only one person can bid nil, in our implementation
        can_bid_nil = True
        for bid in current_bids:
            if bid == spades.NIL:
                can_bid_nil = False
                break

        if can_bid_nil:
            # This part is a small deviation from the paper: we will bid nil if the liabilities can be overcome
            can_overcome_liabilities = 0
            for i in range(4):
                # if we have an empty suit, we can overcome a liability
                if len(hand_by_suits[i]) == 0:
                    can_overcome_liabilities += 1
                # if we only have one card in a suit (and it's not a liability), we can probably overcome a liability
                elif len(hand_by_suits[i]) == 1 and liability_by_suits[i] == 0:
                    can_overcome_liabilities += 0.5

            # should we bid nil?
            if liability_by_suits[cards.SPADES] == 0 and len(hand_by_suits[cards.SPADES]) < 4:
                # cannot overcome liabilities in spades (trump) via sluffing off
                for i in range(1, 4): # the rest of the suits, spades == 0
                    if liability_by_suits[i] > 0 and can_overcome_liabilities > 0:
                        # how deep in the suit are we?
                        if len(hand_by_suits[i]) > 1.5*liability_by_suits[i]:
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
                    return spades.NIL
        
        # not bidding nil, so determine what we _are_ bidding

        # add in spades bids
        spades_count = len(hand_by_suits[cards.SPADES])
        if spades_count < 2:
            points -= 1
        elif spades_count > 3:
            points += 1
        elif spades_count == 3:
            # 3 spades + void or singleton in side suit
            for i in range(1, 4): # the rest of the suits, spades == 0
                if len(hand_by_suits[i]) < 2:
                    points += 1
        
        return points