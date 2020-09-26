import gym
from gym import error, spaces, utils
from gym.utils import seeding

from .spades import spades, player, cards

class SpadesRandomEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    
    self.agent = player()
    self.opponents = [player(), player()]
    self.partner = player()
    self.env = spades([player, opponents[0], partner, opponents[1]])

    # how is the state represented
    # https://github.com/openai/gym/tree/master/gym/spaces
    # http://gym.openai.com/docs/#spaces

    # minimal representation: we know our cards and if one has been played
    self.observation_space = spaces.Dict({
        'held': spaces.Dict({
          'hearts': spaces.Discrete(13),
          'clubs': spaces.Discrete(13),
          'diamonds': spaces.Discrete(13),
          'spades': spaces.Discrete(13),
        }),
        'round': spaces.Tuple(
          spaces.Discrete(53), # no card is an option
          spaces.Discrete(53),
          spaces.Discrete(53)
        ),
        'bid': spaces.Discrete(13)
        # 'bids': spades.Tuple(
        #   spaces.Discrete(13),
        #   spaces.Discrete(13),
        #   spaces.Discrete(13),
        #   spaces.Discrete(13),
        # ),
        # 'unplayed': spaces.Dict({
        #     'hearts': spaces.Discrete(13),
        #     'clubs': spaces.Discrete(13),
        #     'diamonds': spaces.Discrete(13),
        #     'spades': spaces.Discrete(13),
        # }),
        # 'played': spaces.Dict({
        #     'hearts': spaces.Discrete(13),
        #     'clubs': spaces.Discrete(13),
        #     'diamonds': spaces.Discrete(13),
        #     'spades': spaces.Discrete(13),
        # })
    })

    # 52 cards you can play, plus bid of 0-13
    # could also change this to 13, since only 13 cards in hand
    self.action_space = spaces.Discrete(52 + 14)

    # configure the environment

    # configure the player
    
  def play(self, round):
    assert False

  def step(self, action):
    assert False   
    self.take_action(action)
    # wait for the environment to be ready
    done = self.play_randomly_until_turn(self.agent)
    reward = self.get_reward()
    ob = self.env.getState()
    return ob, reward, done

  def take_action(self, action):
    # todo: assert that the action is legal
    if action >= 52:
      # it's a bid!
      self.env.bid(player, action)
    else:
      # playing a card
      self.env.play_card(player, action)

  def reset(self):
    self.env = spades([player, opponents[0], partner, opponents[1]])
    
  def render(self, mode='human'):
    # nothing
    print("rendering")

  def close(self):
    # nothing
    print("closing")
    
  

# spades = SpadesEnv()
