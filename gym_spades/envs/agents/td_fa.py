import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent

# td (sarsa) learning agent with function approximation

class td_fa(fa_agent):
    
    def __init__(self, epsiolon):
        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = [0 for _ in self.get_state_space()]
        print(self.weights)

    def _play(self, game):
        # iterate through all the state/action pairs, and find the maximum one
        max_value = None
        max_index = None
        for i, action in enumerate(self.get_legal_cards(game)):
            features = self.get_features(game, action)
            value = self._value(features)
            if max_value is None or max_value < value:
                max_value = value
                max_index = i

        return random.choice()

    def _value(self, features):
        return np.dot(self.weights, features)

    def _backup():

        
if __name__ == "__main__":
    q = qfa()