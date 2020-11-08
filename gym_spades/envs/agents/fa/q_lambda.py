import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents.fa import qfa

# q-learning player with function approximation
# section 12.2

class q_lambda(qfa):

    def __init__(self, epsilon: int=0.01, learning_rate: int=0.01, discount_factor: int=0.01, lambda_v: int=0.4):
        super().__init__()
        self.name = 'q-lambda'

        self.weights = np.zeros((self._get_feature_space()))
        self.eligibility = np.zeros((self._get_feature_space()))
        self.lambda_v = lambda_v
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def result(self):
        return self.weights, self.eligibility

    def create_player(self):
        from gym_spades.envs.agents.fa import fa_lambda_player
        p = fa_lambda_player(self)
        p.name = self.name
        return p

if __name__ == "__main__":
    q = q_lambda()
