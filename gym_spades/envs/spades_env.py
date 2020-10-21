from gym_spades.envs.spades import spades, cards, player

import pickle
from datetime import datetime

class SpadesEnv():

    def __init__(self, players):

        self.players = players
        self.results = [[] for i in range(4)]

    def _episode(self):
        self.game.reset()
        self.game.bid_round()

        for i in range(13):
            self.game.play_round()

        assert self.game.is_game_over()

        self.game.end_game()

        for p in self.players:
            self.results[p.index].append(p.result())

    def _reset(self):
        self.game = spades(self.players)
        for p in self.players:
            p.points_hist = []

    def run(self, n):
        self._reset()
        for i in range(n):
            self._episode()
            #print("game over, resetting")

    def save(self, name=0):
        for i in range(4):
            f = open('tuned_params/'+ self.players[i].name + '-'+str(i)+'-'+str(name), 'wb')
            pickle.dump(self.players[i], f)
            f.close()
            self.players[i].total_rewards = 0

if __name__=="__main__":
    from gym_spades.envs.agents import rule_based_0
    from gym_spades.envs.agents.fa import fa_agent, qfa, q_lambda, q_nstep_lambda

    # load in the agents
    # names = ['qfa/qfa0-1', 'qfa/qfa1-1', 'qfa/qfa2-1', 'qfa/qfa3-1']
    # agents = []
    # for n in names:
    #     with open(n, 'rb') as f:
    #         agent = pickle.load(f)
    #         agents.append(agent)
    epsilon = 0.1
    alpha = 0.1
    gamma = 0.01
    lambda_v = 0.4

    q = qfa(epsilon, alpha, gamma)
    q_lambda = q_lambda(epsilon, alpha, gamma, lambda_v)
    q_nstep_lambda = q_nstep_lambda(epsilon, alpha, gamma, lambda_v)
    heur = rule_based_0()

    agents = [q.create_player(), q_lambda.create_player(), q_nstep_lambda.create_player(), heur]
    s = SpadesEnv(agents)

    for i in range(0, 100):
        s.run(100)
        s.save(i)

