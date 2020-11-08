import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents.fa import q_lambda, fa_nstep_lambda_player


# q-learning player with function approximation
# section 12.2

class q_nstep_lambda(q_lambda):

    def __init__(self, epsilon: int=0.01, learning_rate: int=0.01, discount_factor: int=0.01, lambda_v: int=0.4, n: int=13):
        super().__init__()
        self.name = 'q_nstep_lambda'

        self.weights = np.zeros((self._get_feature_space()))
        self.eligibility = np.zeros((self._get_feature_space()))
        self.lambda_v = lambda_v
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.n = n

    def result(self):
        return self.weights, self.eligibility

    def create_player(self):
        p = fa_nstep_lambda_player(self)
        p.name = self.name
        return p

if __name__ == "__main__":
    q = q_nstep_lambda()
