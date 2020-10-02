import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents import fa_agent

# q-learning player with function approximation
# qfa

class qfa(fa_agent):
    
    def __init__(self, epsilon=0.01, learning_rate=0.01, discount_factor=0.01):
        super().__init__()
        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = np.zeros(len(self._get_feature_space()))
        print(self.weights)

        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # statistics
        self.rewards = []
        self.lengths = []

        self.cumulative_reward = 0.0

        self.prev_val = None

    def _play(self, game):  
        if not self.prev_val is None:
            # backing up involves computing optimal action for this state
            self.prev_val, action = self._backup(self.prev_val, self.prev_features, self.reward, game)
        else:
            self.prev_val, action = self._q(game)
        
        return action

    def _q(self, state):
        if state == None:
            # terminal state
            return 0, None

        # epsilon-greedy policy
        actions = self.get_legal_cards(state)

        # iterate through all the state/action pairs, and find the maximum one
        max_value = None
        max_action = None
        max_index = 0
        for i, action in enumerate(actions):
            self.prev_features = self.get_features(state, action)
            value = self._value(self.prev_features)
            if max_value is None or max_value < value:
                max_value = value
                max_action = action
                max_index = i

        if random.uniform(0,1) < self.epsilon:
            # return a non-optimal a different action
            if len(actions) > 1:
                new_actions = actions[:max_index] + actions[max_index + 1:]
                return max_value, random.choice(new_actions)

        return max_value, max_action
    
    def _value(self, features):
        return np.dot(self.weights, features)

    def _backup(self, prev_val, prev_features, reward, next_state):
        next_val, action = self._q(next_state)
        td_target = reward + self.discount_factor * next_val - self.prev_val
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        self.weights = self.weights - self.learning_rate*(td_target) * prev_features

        return next_val, action

    # def _reward(self, reward):
    #     self.cumulative_reward += reward
    #     self.reward = reward

    def _log(self, episode_number, reward):
        if len(self.rewards) < episode_number:
            self.rewards.append([])
            self.lengths.append([])
        self.rewards[episode_number] += reward
        self.lengths[episode_number] += 1

    # tabular solution method
    def _policy(self, state, actions):
        action_prob = np.ones(52, dtype=float) * self.epsilon / len(52)
        best_action = np.argmax(self.Q[state])
        action_prob[best_action] += (1.0 - self.epsilon)
        return action_prob

    def result(self):
        return [self.rewards, self.weights]

if __name__ == "__main__":
    q = qfa()