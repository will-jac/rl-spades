import gym

from gym_spades.envs.spades.spades import spades
from gym_spades.envs.spades.cards import cards
from gym_spades.envs.spades.player import player

import pickle
from datetime import datetime

class SpadesEnv(gym.Env, spades):
    metadata = {'render.modes': ['human']}

    def __init__(self, agents):
        
        self.agents = agents
        self.game = spades(self.agents)
        
        self.results = [[] for i in range(4)]

    def episode(self):
        self.reset()
        
        for i in range(13):
            self.game.play_round()

        assert self.game.is_game_over()

        self.game.end_game()

        for a in self.agents:
            self.results[a.index].append(a.result())

    def reset(self):
        self.game.reset()
        self.game.bid_round()

    def run(self, iter):
        for i in range(iter):
            self.episode()
    
    def save(self, name=0):
        for i in range(4):
            f = open('qfa-'+str(i)+'-'+str(name), 'wb')
            pickle.dump(self.agents[i], f)
            f.close()

if __name__=="__main__":
    from gym_spades.envs.agents import fa_agent, qfa
    agents = [qfa(), qfa(), qfa(), qfa()]
    s = SpadesEnv(agents)
    for i in range(10):
        s.run(10)
        s.save(i)
    iter = 0
    exit()
    while True:
    #for i in range(1):
        #for i in range(10):
        s.run(10)
        s.save(iter)
        iter += 1
