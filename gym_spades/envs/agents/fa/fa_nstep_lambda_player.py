from __future__ import annotations

from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents.fa import fa_player

import numpy as np
import itertools
import random

class fa_nstep_lambda_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.history = [0]*self.parent.n
        self.history_length = 0

    def _play(self, game: spades) -> cards:
        if game is None:
            # do the last n rounds of backup
            for i in range(self.parent.n):
                self._backup(None)
            return 0
        else:
            state = {}
            actions = self.get_legal_cards(game)
            for action in actions:
                state[action] = self.get_features(game, action)

            self.prev_value, action, self.prev_features = self._backup(state)
        return action

    def _backup(self, state: dict[cards, list[int]]) -> (float, cards):
        value, action, features = self.parent._get_action(state)
        if self.reward is None:
            return value, action, features

        #print(self.reward, self.parent.discount_factor, value, self.prev_value)
        td_error = self.reward + self.parent.discount_factor * value - self.prev_value
        # pg 297
        self.history.append((td_error, value, features))

        if len(self.history) == self.parent.n:
            G = value
            for i, td_err, _, _ in enumerate(self.history):
                G += (self.parent._v * self.parent.learning_rate)**(i) * td_err
            # backup from that position
            _, v, f = self.history.pop(0)
            self.parent.weights += self.parent.discount_factor * (G - v) * f

        return value, action, features
