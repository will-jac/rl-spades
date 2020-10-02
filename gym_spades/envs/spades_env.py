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

        self.game.bid_round()
        
        self.results = [[] for i in range(4)]

    def episode(self):
        for i in range(13):
            self.game.play_round()

        assert self.game.mode == spades.GAMEOVER

        self.game.end_of_game()

        for a in self.agents:
            self.results[a.index].append(a.result())

        self.reset()

    def reset(self):
        self.game.reset()
        self.game.bid_round()

    def run(self, iter):
        for i in range(iter):
            self.episode()
        
        for i in range(4):
            print(self.results[i][-1])
    
    def save(self):
        for i in range(4):
            f = open('qfa-'+str(i)+'-'+str(datetime.now()).replace(' ','_').replace(':','-'), 'wb')
            pickle.dump(self.agents[i], f)
            f.close()

if __name__=="__main__":
    from gym_spades.envs.agents import fa_agent, qfa
    agents = [qfa(), qfa(), qfa(), qfa()]
    s = SpadesEnv(agents)
    while True:
        s.run(1000)
        s.save()