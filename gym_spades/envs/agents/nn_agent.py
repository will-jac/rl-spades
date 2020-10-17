from __future__ import annotations

from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents import agent, agent_player

import tensorflow as tf
import numpy as np
import itertools
import random

## ahh seems hard

class nn_agent(fa_agent):
    def _play(self, state: dict[cards, list[int]]) -> cards:
        ...

    def _get_nn_output_size(self) -> int:
        return nn_player.get_nn_output_size()

    def create_player(self):
        return nn_player(self)

class nn_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.round_type = None

        self.prev_value = None
        self.prev_features = None

        # statistics
        self.rewards = []

        self.cumulative_reward = 0.0

    def reset(self, index: int, hand: list[cards]):
        super().reset(index, hand)
        self.prev_value = None
        self.prev_features = None

    def _play(self, game: spades) -> cards:
        # print("playing:",self.index)
        #cards.print_hand(self.hand)
        if game is None:
            state = None
        else:
            state = {}
            actions = self.get_legal_cards(game)
            for action in actions:
                state[action] = self.get_features(game, action)

        if self.prev_value is None:
            self.prev_value, action, self.prev_features = self.parent._get_action(state)
        else:
            self.prev_value, action, self.prev_features = self._backup(state)

        return action

    def _backup(self, state: dict[cards, list[int]]) -> (float, cards):
        value, action, features = self.parent._get_action(state)
        td_target = self.reward + self.parent.discount_factor * value - self.prev_value

        print(self.index, "backup",  self.parent.learning_rate, td_target, self.prev_features)
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        self.parent.weights = self.parent.weights + self.parent.learning_rate * td_target * self.prev_features

        return value, action, features

    def result(self) -> (list[float], list[float]):
        return (self.rewards, self.parent.weights)
