from gym_spades.envs.spades.spades import spades
from gym_spades.envs.spades.cards import cards
from gym_spades.envs.spades.player import player

import pickle
from datetime import datetime

class SpadesEnv(spades):

    def __init__(self, agents):

        self.agents = agents
        self.results = [[] for i in range(4)]

    def _episode(self):
        self.game.reset()
        self.game.bid_round()

        for i in range(13):
            self.game.play_round()

        assert self.game.is_game_over()

        self.game.end_game()

        for a in self.agents:
            self.results[a.index].append(a.result())

    def _reset(self):
        self.game = spades(self.agents)
        for a in self.agents:
            a.points_hist = []

    def run(self, n):
        self._reset()
        for i in range(n):
            self._episode()

    def save(self, name=0):
        for i in range(4):
            f = open('tmp/qfa-'+str(i)+'-'+str(name), 'wb')
            pickle.dump(self.agents[i], f)
            f.close()
            self.agents[i].total_rewards = 0

if __name__=="__main__":
    from gym_spades.envs.agents import fa_agent, qfa

    # load in the agents
    # names = ['qfa/qfa0-1', 'qfa/qfa1-1', 'qfa/qfa2-1', 'qfa/qfa3-1']
    # agents = []
    # for n in names:
    #     with open(n, 'rb') as f:
    #         agent = pickle.load(f)
    #         agents.append(agent)
    agents = [qfa(), qfa(), qfa(), qfa()]
    s = SpadesEnv(agents)
    iter = 0
    while True:
        s.run(100)
        s.save(iter)
        iter += 1
