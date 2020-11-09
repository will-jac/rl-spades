from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents.fa import fa_player

import numpy as np
import itertools
import random

class fa_nstep_lambda_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.history = []

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
        if self.reward is None:
            return value, action, features

        #print(self.reward, self.parent.discount_factor, value, self.prev_value)
        td_error = self.reward + self.parent.discount_factor * value - self.prev_value
        # pg 297
        self.history.append((td_error, value, features))

        if len(self.history) == self.parent.n:
            #print("backing up")
            _, first_v, f, = self.history[0]
            G = first_v
            for i, (td_err, _, _) in enumerate(self.history):
                G += (self.parent.lambda_v * self.parent.learning_rate)**(i) * td_err
            # backup from that position
            #print(self.history)
            _, v, f = self.history[11]
            #print((G-v), f)
            self.parent.weights += self.parent.discount_factor * (G - v) * f
            # reset history
            self.history = []
        #else:
        #    print(len(self.history))

        return value, action, features
