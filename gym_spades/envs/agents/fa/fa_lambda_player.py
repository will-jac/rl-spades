from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents.fa import fa_player

import numpy as np
import itertools
import random

class fa_lambda_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.eligibility = np.zeros((self.get_feature_space()))

    def _backup(self, state):
        #print(self.hand)
        value, action, features = self.parent._get_action(state)
        #print(value, action, features)
        td_target = self.reward + self.parent.discount_factor * value - self.prev_value


        #print(self.index, "backup",  self.parent.learning_rate, td_target, self.prev_features)
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        # section 12.2
        self.eligibility = self.parent.discount_factor * self.parent.lambda_v ** self.parent.exponent * self.eligibility + self.prev_features
        self.parent.weights = self.parent.weights + self.parent.learning_rate * td_target * self.eligibility

        return value, action, features
