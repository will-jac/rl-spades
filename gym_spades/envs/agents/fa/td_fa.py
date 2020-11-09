import random as rand
import numpy as np

from gym_spades.envs.spades import cards, spades
from gym_spades.envs.agents.fa import fa_agent, fa_player

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

    def create_player(self):
        print('creating td-fa player')
        p = td_player(self)
        p.name = self.name
        return p

class td_player(fa_player):

    def __init__(self, parent):
        super().__init__(parent)
        #self.player = fa_player(self)
        self.first_play = True

    def reset(self, index, hand):
        super().reset(index, hand)
        self.first_play = True

    def _play(self, game):
        #if first trick in hand
        if self.first_play:

            #choose action from current policy
            #TODO: make this an epsilon greedy policy not a greedy one
            poss_actions = self.get_legal_cards(game)
            max_val = np.dot(self.parent.weights, self.get_features(game, poss_actions[0]))
            all_max_actions = []
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
#            print("This is trick number ", self.parent.num_tricks_played+1, " there are ", len(poss_actions), "legal cards")
#            print("HAND: ", [cards.card_str(c) for c in self.hand])
#
#            print("--------------------------------------------------")
#            print("The initial max value is ", max_val)

            for i in range(0, len(poss_actions)):
                temp = np.dot(self.parent.weights, self.get_features(game, poss_actions[i]))
#                print("card ", i, " has value ", temp)
                if temp == max_val:
#                    print("card ", i, " was added to all max actions")
                    all_max_actions.append(poss_actions[i])
                elif temp > max_val:
#                    print("card ", i, " was greater than previous max, reset all max actions")
                    all_max_actions = [poss_actions[i]]
                    max_val = temp
#                print([cards.card_str(c) for c in all_max_actions])

#            print("this is what we have to choose from ", [cards.card_str(c) for c in all_max_actions])
            a = random.choice(all_max_actions)
            
            #epsilon greedy policy
            r_val = rand.uniform(0,1) #stores a random value between 0 and 1
            
            if r_val <= epsilon:
                a = random.choice(poss_actions)


            #save previous features
            self.parent.prev_features = self.get_features(game, a)
            self.parent.num_tricks_played = self.parent.num_tricks_played+1

            #take action a
            return a

        else:
            #find reward for previous action
            r = self.reward #s[len(self.rewards)-1] #TODO FIX THIS

            #is this the terminal state?
            if self.parent.num_tricks_played == 13:
#                print("play was called once more after terminal state was reached")

                #Update weights
                temp = r - np.dot(self.parent.weights, self.parent.prev_features)
                temp = self.parent.learning_rate*temp
                self.parent.weights = self.parent.weights + (temp*self.parent.prev_features)

                #reset
                self.parent.num_tricks_played = 0
                self.parent.prev_features = None
                return None

            else:
                #find reward for previous action
                r = self.rewards[len(self.rewards)-1] #TODO FIX HIS

                #choose action from current policy
                poss_actions = self.get_legal_cards(game)
                max_val = np.dot(self.parent.weights, self.get_features(game, poss_actions[0]))
                all_max_actions = []
                temp = 0

#                print("--------------------------------------------------")
#                print("This is trick number ", self.parent.num_tricks_played+1, " there are ", len(poss_actions), "legal cards")
#                print("HAND: ", [cards.card_str(c) for c in self.hand])
#                print("--------------------------------------------------")
#                print("The initial max value is ", max_val)

                for i in range(0, len(poss_actions)):
                    temp = np.dot(self.parent.weights, self.get_features(game, poss_actions[i]))
#                    print("card ", i, " has value ", temp)
                    if temp == max_val:
#                        print("card ", i, " was added to all max actions")
                        all_max_actions.append(poss_actions[i])
                    elif temp > max_val:
#                        print("card ", i, " was greater than previous max, reset all max actions")
                        all_max_actions = [poss_actions[i]]
                        max_val = temp
#                    print([cards.card_str(c) for c in all_max_actions])


#                print("this is what we have to choose from ",[cards.card_str(c) for c in all_max_actions])
                a = random.choice(all_max_actions)
                
                #epsilon greedy policy
                r_val = rand.uniform(0,1) #stores a random value between 0 and 1
                
                if r_val <= epsilon:
                    a = random.choice(poss_actions)


                #Update weights
                temp = np.dot(self.parent.weights, self.get_features(game, a))
                temp = r + (self.parent.discount_factor*temp)
                temp = temp - np.dot(self.parent.weights, self.parent.prev_features)
                temp = self.parent.learning_rate*temp
                self.parent.weights = self.parent.weights + (temp*self.parent.prev_features)

                #save previous features
                self.parent.prev_features = self.get_features(game, a)
                self.parent.num_tricks_played = self.parent.num_tricks_played+1

                #take action a
                return a


    def _value(self, features):
        return np.dot(self.parent.weights, features)
