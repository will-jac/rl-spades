import gym
from gym import error, spaces, utils
from gym.utils import seeding

from gym_spades.envs.spades.spades import spades
from gym_spades.envs.spades.cards import cards
from gym_spades.envs.spades.player import player


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
        
    # def render(self, mode='human'):
    #     ...
    # def close(self):
    #     ...  

    # def get_state(self, player):
    #     have_highest = self.have_highest_card_in_lead_suit(player)
    #     return (
    #         # have_highest_card_in_lead_suit
    #         have_highest,
    #         # suit_lead
    #         self.suit_lead,
    #         # spades_played
    #         self.spades_played,
    #         # can_win
    #         self.can_win(player),
    #         # smallest_suit
    #         self.smallest_suit(player),
    #         # trick_num
    #         self.round_counter // 4,
    #         # is_over_bid
    #         self.is_over_bid,

    #     )

if __name__=="__main__":
    from gym_spades.envs.agents import fa_agent, qfa
    agents = [qfa(), fa_agent(), qfa(), fa_agent()]
    s = SpadesEnv(agents)
    s.run(100)