from __future__ import annotations

from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents import agent, agent_player, fa_agent, fa_player

import numpy as np
import itertools
import random

class fa_lambda_player(fa_player):

    def _backup(self, state: dict[cards, list[int]]) -> (float, cards):
        value, action, features = self.parent._get_action(state)
        td_target = self.reward + self.parent.discount_factor * value - self.prev_value
        self.parent.eligibility = self.parent.discount_factor * self.parent.lambda * self.parent.eligibility + self.prev_features

        #print(self.index, "backup",  self.parent.learning_rate, td_target, self.prev_features)
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        self.parent.weights = self.parent.weights + self.parent.learning_rate * td_target * self.parent.eligibility

        return value, action, features
