from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents.fa import fa_player

import numpy as np
import itertools
import random

class fa_nstep_lambda_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.G = None
        self.i = 0

    def _play(self, game):
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

    def _backup(self, state):
        value, action, features = self.parent._get_action(state)
        if self.G is None or self.reward is None:
            # first round
            self.G = value
            self.i = 0
            #self.history.append(0, value, features)
            return value, action, features

        #print(self.reward, self.parent.discount_factor, value, self.prev_value)
        td_error = self.reward + self.parent.discount_factor * value - self.prev_value
        # pg 297

        if self.i + 1 == self.parent.n:
            print("backing up")
            # backup from that position
            #print(self.history)
            self.parent.weights += self.parent.discount_factor * (self.G - self.prev_value) * self.prev_features
            # reset history
            self.G = None
            self.i = 0
        else:
            self.G += (self.parent.lambda_v * self.parent.learning_rate)**(self.i) * td_error
            self.i += 1

        return value, action, features
