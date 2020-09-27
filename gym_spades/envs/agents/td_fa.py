import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent

# td (sarsa) learning agent with function approximation

class td_fa(fa_agent):
    
    def __init__(self):
        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = [0 for _ in self.get_state_space()]
        print(self.weights)

    def _play(self, game):
        return random.choice(self.get_legal_cards(game))

    def _value(self, features):
        return np.dot(self.weights, features)

    def _backup()
        
if __name__ == "__main__":
    q = qfa()