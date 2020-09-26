import random

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent

# q-learning player with function approximation
# qfa

class qfa(fa_agent):
        
    def _play(self, state, round):
        return random.choice(self.get_legal_cards())
    

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