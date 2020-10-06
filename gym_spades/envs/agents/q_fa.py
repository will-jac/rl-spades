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
        self.weights = np.zeros((self._get_feature_space()))

        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # statistics
        self.rewards = []
        self.lengths = []

        self.cumulative_reward = 0.0

        self.prev_val = None

    def _play(self, game):  
        if self.prev_val is None:
            self.prev_val, action = self._q(game)
        else:
            # backing up involves computing optimal action for this state
            self.prev_val, action = self._backup(self.prev_features, game)
        
        return action

    def _q(self, state):
        # terminal condition
        if state is None:
            return 0, None

        # epsilon-greedy policy
        actions = self.get_legal_cards(state)
        
        num_actions = len(actions)
        if num_actions == 1:
            self.prev_features = self.get_features(state, actions[0])
            v = self._value(self.prev_features)
            return v, actions[0]
        # probability of selecting any non-optimal value = epsilon 
        # => each non-optimal action has prob epsilon / (num_actions - 1)
        action_probs = np.ones(num_actions, dtype=float) * self.epsilon / (num_actions - 1)

        # iterate through all the state/action pairs, and find the maximum one
        values = np.zeros(num_actions, dtype=float)
        features = np.zeros(shape=(num_actions,self._get_feature_space()))

        for i, a in enumerate(actions):
            features[i] = self.get_features(state, a)
            values[i] = self._value(features[i])

        max_index = np.random.choice(np.flatnonzero(values == values.max()))
        max_value = values[max_index]
        # prob of maximum action = 1 - epsilon 
        action_probs[max_index] = (1.0 - self.epsilon)

        #print(action_probs)
        
        action_index = np.random.choice(np.arange(num_actions), p=action_probs)
        self.prev_features = features[action_index]

        return max_value, actions[action_index]
    
    def _value(self, features):
        return np.dot(self.weights, features)

    def _backup(self, prev_features, next_state):
        next_val, action = self._q(next_state)
        td_target = self.reward + self.discount_factor * next_val - self.prev_val
        #print(self.index, "backup",  self.reward, next_val, self.prev_val, td_target, self.weights)
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        self.weights = self.weights + self.learning_rate*(td_target) * prev_features

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
