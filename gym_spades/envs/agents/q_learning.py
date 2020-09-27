import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent

# q-learning player with function approximation
# qfa

class qfa(fa_agent):
    
    def __init__(self):
        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = [0 for _ in self.get_state_space()]
        print(self.weights)

    def _play(game):
        return random.choice(self.get_legal_cards(game))

    def _value(self, state):
        return np.dot(self.weights, state)

    #def _backup()
        
if __name__ == "__main__":
    q = qfa()