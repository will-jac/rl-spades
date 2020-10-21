from __future__ import annotations

import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent


# q-learning player with function approximation
# qfa

class deep_q(nn_agent):
    def __init__(self, epsilon: int=0.01, learning_rate: int=0.01, discount_factor: int=0.01):
        super().__init__()
        self.name = 'qfa'
        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = np.zeros((self._get_feature_space()))

        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    # Q function
    # returns value, action, features
    def _get_action(self, state: dict[cards, list[int]]) -> (float, cards, list[int]):
        # terminal condition
        if state == None:
            return 0, None, None

        num_actions = len(state)

        # if only one action, do it
        if num_actions == 1:
            a, f = state.popitem()
            v = self._value(f)
            return v, a, f

        # epsilon-greedy policy

        # probability of selecting any non-optimal value = epsilon
        # => each non-optimal action has prob epsilon / (num_actions - 1)
        action_probs = np.ones(num_actions, dtype=float) * self.epsilon / (num_actions - 1)

        # iterate through all the state/action pairs, and find the maximum one
        values = np.zeros(num_actions, dtype=float)

        for i, (a, f) in enumerate(state.items()):
            values[i] = self._value(f)

        max_index = np.random.choice(np.flatnonzero(values == values.max()))
        max_value = values[max_index]
        # prob of maximum action = 1 - epsilon
        action_probs[max_index] = (1.0 - self.epsilon)

        #print(action_probs)

        action = np.random.choice(list(state.keys()), p=action_probs)
        features = state[action]

        return max_value, action, features

    def _value(self, features: list[int]) -> float:
        return np.dot(self.weights, features)

    def _log(self, episode_number, reward):
        if len(self.rewards) < episode_number:
            self.rewards.append([])
            self.lengths.append([])
        self.rewards[episode_number] += reward
        self.lengths[episode_number] += 1

    def result(self) -> list[float]:
        return self.weights

if __name__ == "__main__":
    q = qfa()
