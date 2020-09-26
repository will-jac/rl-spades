import random

from gym_spades.envs.spades.player import player
from gym_spades.envs.spades import cards, spades

# example player - a human!

class rule_based_0(player):
    suits = ['S', 'H', 'C', 'D']
    # humans have no choice for bidding - sorry!
    def _play(self, state, round):
        return random.choice(self.get_legal_cards())
    # F.1: Number of sure future takes
    # Worst case: All unseen spades are held by a single opponent
    # and all the spades tricks are lead by the agent. Only spades
    # cards are sure winners.
    # Sure takes: Boss (eg A) or # more than unseen (eg [K,Q]=1 trick).
    # def num_sure_future_takes(self, game):
    #     for c in self.hand_by_suit[cards.SPADES]:
              
    #         game.discard_by_suit[cards.SPADES]

    def getState(self, game):
        # https://arxiv.org/pdf/1912.11323v1.pdf page 10, top right
        
        # round type of:
        # under         no nils, sum of bids in {8-10}
        # over          no nils, sum of bids in {11-13}
        # 14            no nils, sum of bids == 14
        # strong under  no nils, sum of bids <= 8
        # strong over   no nils, sum of bids >= 15
        # we nil        single nil bid in partnership
        # opponents nil single nil bid in opponents
        # nil vs nil    each has one nil                        # illegal
        # double nil    both players in a partnership bid nil   # illegal

        # end game conditions
        # partnership can win game this round
        # opponents can win game this round
        
 

        return