import random
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents.fa import fa_agent

# td (sarsa) learning agent with function approximation

class td_fa(fa_agent):

    def __init__(self, epsilon=0.01, learning_rate=0.01, discount_factor=0.7):
        super().__init__()

        # initalize a state vector
        # TODO: add a way to initalize this from a file
        self.weights = np.zeros(self._get_feature_space())
        self.name = "td_fa"
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.rewards = []
        self.prev_features = None
        self.num_tricks_played = 0



    def _play(self, game):

        #if first trick in hand
        if self.num_tricks_played == 0:

            #choose action from current policy
            #TODO: make this an epsilon greedy policy not a greedy one
            poss_actions = self.get_legal_cards(game)
            max_val = np.dot(self.weights, self.get_features(game, poss_actions[0]))
            all_max_actions = []
            print(all_max_actions)
            temp = 0

#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#            print("--------------------------------------------------")
#
#
#
#            print("--------------------------------------------------")
#            print("This is trick number ", self.num_tricks_played+1, " there are ", len(poss_actions), "legal cards")
#            print("HAND: ", [cards.card_str(c) for c in self.hand])
#
#            print("--------------------------------------------------")
#            print("The initial max value is ", max_val)

            for i in range(0, len(poss_actions)):
                temp = np.dot(self.weights, self.get_features(game, poss_actions[i]))
#                print("card ", i, " has value ", temp)
                if temp == max_val:
#                    print("card ", i, " was added to all max actions")
                    all_max_actions.append(poss_actions[i])
                elif temp > max_val:
#                    print("card ", i, " was greater than previous max, reset all max actions")
                    all_max_actions = [poss_actions[i]]
                    max_val = temp
#                print(all_max_actions)

#            print("this is what we have to choose from ", all_max_actions)
            a = random.choice(all_max_actions)


            #save previous features
            self.prev_features = self.get_features(game, a)
            self.num_tricks_played = self.num_tricks_played+1

            #take action a
            return a

        else:
            #find reward for previous action
            r = self.rewards[len(self.rewards)-1]

            #is this the terminal state?
            if self.num_tricks_played == 13:
#                print("play was called once more after terminal state was reached")

                #Update weights
                temp = r - np.dot(self.weights, self.prev_features)
                temp = self.learning_rate*temp
                self.weights = self.weights + (temp*self.prev_features)

                #reset
                self.num_tricks_played = 0
                self.prev_features = None
                return None

            else:
                #find reward for previous action
                r = self.rewards[len(self.rewards)-1]

                #choose action from current policy
                #TODO: make this an epsilon greedy policy not a greedy one
                poss_actions = self.get_legal_cards(game)
                max_val = np.dot(self.weights, self.get_features(game, poss_actions[0]))
                all_max_actions = []
                temp = 0

#                print("--------------------------------------------------")
#                print("This is trick number ", self.num_tricks_played+1, " there are ", len(poss_actions), "legal cards")
#                print("HAND: ", [cards.card_str(c) for c in self.hand])
#                print("--------------------------------------------------")
#                print("The initial max value is ", max_val)

                for i in range(0, len(poss_actions)):
                    temp = np.dot(self.weights, self.get_features(game, poss_actions[i]))
#                    print("card ", i, " has value ", temp)
                    if temp == max_val:
#                        print("card ", i, " was added to all max actions")
                        all_max_actions.append(poss_actions[i])
                    elif temp > max_val:
#                        print("card ", i, " was greater than previous max, reset all max actions")
                        all_max_actions = [poss_actions[i]]
                        max_val = temp
#                    print(all_max_actions)


#                print("this is what we have to choose from ", all_max_actions)
                a = random.choice(all_max_actions)


                #Update weights
                temp = np.dot(self.weights, self.get_features(game, a))
                temp = r + (self.discount_factor*temp)
                temp = temp - np.dot(self.weights, self.prev_features)
                temp = self.learning_rate*temp
                self.weights = self.weights + (temp*self.prev_features)

                #save previous features
                self.prev_features = self.get_features(game, a)
                self.num_tricks_played = self.num_tricks_played+1

                #take action a
                return a


    def _value(self, features):
        return np.dot(self.weights, features)



if __name__ == "__main__":
    td = td_fa()