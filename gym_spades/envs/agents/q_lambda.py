from __future__ import annotations

import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import qfa


# q-learning player with function approximation
#

class q_lambda(qfa):

    def __init__(self, epsilon: int=0.01, learning_rate: int=0.01, discount_factor: int=0.01, lambda: int=0.4):
        super().__init__()
        self.name = 'q-lambda'

        self.weights = np.zeros((self._get_feature_space()))
        self.eligibility = np.zeros((self._get_feature_space()))
        self.lambda = lambda
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def result(self) -> (list[float], list[float]):
        return self.weights, self.eligibility

if __name__ == "__main__":
    q = q_lambda()
