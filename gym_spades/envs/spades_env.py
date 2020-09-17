import gym
from gym import error, spaces, utils
from gym.utils import seeding

class SpadesEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    

    # how is the state represented?
    # https://github.com/openai/gym/tree/master/gym/spaces
    # http://gym.openai.com/docs/#spaces
    self.observation_space = spaces.Dict({
        'agent': spaces.Dict({
            'hearts': spaces.Discrete(13),
            'clubs': spaces.Discrete(13),
            'diamonds': spaces.Discrete(13),
            'spades': spaces.Discrete(13),
        }),
        'partner': spaces.Dict({
            'hearts': spaces.Discrete(13),
            'clubs': spaces.Discrete(13),
            'diamonds': spaces.Discrete(13),
            'spades': spaces.Discrete(13),
        }),
        'opponent1': spaces.Dict({
            'hearts': spaces.Discrete(13),
            'clubs': spaces.Discrete(13),
            'diamonds': spaces.Discrete(13),
            'spades': spaces.Discrete(13),
        }),
        'opponent2': spaces.Dict({
            'hearts': spaces.Discrete(13),
            'clubs': spaces.Discrete(13),
            'diamonds': spaces.Discrete(13),
            'spades': spaces.Discrete(13),
        })
    })
    #region alt space definitions
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

    # 52 cards you can play, plus bid of 0-13 (14 total)
    self.action_space = spaces.Tuple(spaces.Discrete(52), spaces.Discrete(14))
    

  def step(self, action):
    self.take_action(action)
    self.status = self.env.step()
  def reset(self):
    ...
  def render(self, mode='human'):
    ...
  def close(self):
    ...  

spades = SpadesEnv()