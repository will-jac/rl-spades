import gym
from gym import error, spaces, utils
from gym.utils import seeding

from gym_spades.envs.spades.spades import spades, cards
from gym_spades.envs.spades.player import player

class SpadesEnv(gym.Env, spades):
  metadata = {'render.modes': ['human']}

  def __init__(self, agents):
    
    self.game = spades(agents)

    # how is the state represented?
    # https://github.com/openai/gym/tree/master/gym/spaces
    # http://gym.openai.com/docs/#spaces
    #self.observation_space
    #region alt space definitions 
    # spaces.Dict({
    #     'agent': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     }),
    #     'partner': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     }),
    #     'opponent1': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     }),
    #     'opponent2': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     })
    # })
    # spaces.Dict({
    #     'agent': spaces.Dict({
    #         'aces': spaces.Discrete(4),
    #         'kings': spaces.Discrete(4),
    #         'queens': spaces.Discrete(4),
    #         'jacks': spaces.Discrete(4),
    #         'spades': spaces.Discrete(9),
    #         'others': spaces.Discrete(27)
    #     }),
    #     'partner': spaces.Dict({
    #         'aces': spaces.Discrete(4),
    #         'kings': spaces.Discrete(4),
    #         'queens': spaces.Discrete(4),
    #         'jacks': spaces.Discrete(4),
    #         'spades': spaces.Discrete(9),
    #         'others': spaces.Discrete(27)
    #     }),
    #     'opponent1': spaces.Dict({
    #         'aces': spaces.Discrete(4),
    #         'kings': spaces.Discrete(4),
    #         'queens': spaces.Discrete(4),
    #         'jacks': spaces.Discrete(4),
    #         'spades': spaces.Discrete(9),
    #         'others': spaces.Discrete(27)
    #     }),
    #     'opponent2': spaces.Dict({
    #         'aces': spaces.Discrete(4),
    #         'kings': spaces.Discrete(4),
    #         'queens': spaces.Discrete(4),
    #         'jacks': spaces.Discrete(4),
    #         'spades': spaces.Discrete(9),
    #         'others': spaces.Discrete(27)
    #     })
    # })
    # self.observation_space = spaces.Dict({
    #     'agent': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     }),
    #     'partner': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     })
    #     'opponent1': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     }),
    #     'opponent2': spaces.Dict({
    #         'hearts': spaces.Discrete(13),
    #         'clubs': spaces.Discrete(13),
    #         'diamonds': spaces.Discrete(13),
    #         'spades': spaces.Discrete(13),
    #     })
    # })
    # endregion

    # 52 cards you can play,
    self.action_space = spaces.Tuple(spaces.Discrete(52))
    
    def step(self, action):
        winner = self.play_round()
        # can send to agents, if we want
    def reset(self):
        ...
    def render(self, mode='human'):
        ...
    def close(self):
        ...  

    def get_state(self, player):
        have_highest = self.have_highest_card_in_lead_suit(player)
        return (
            # have_highest_card_in_lead_suit
            have_highest,
            # suit_lead
            self.suit_lead,
            # spades_played
            self.spades_played,
            # can_win
            self.can_win(player),
            # smallest_suit
            self.smallest_suit(player),
            # trick_num
            self.round_counter // 4,
            # is_over_bid
            self.is_over_bid,

        )

spades = SpadesEnv()