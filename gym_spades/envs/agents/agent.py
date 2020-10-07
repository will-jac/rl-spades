from gym_spades.envs.spades.player import player
from gym_spades.envs.spades.spades import spades
from gym_spades.envs.spades.cards import cards
from gym import error, spaces, utils

# 'normal' tabular based agent
class agent(player):

    def get_state_space(self):
        return 0

    def get_round_type(self, game):
        nil = []
        for i, b in enumerate(game.bids):
            if b == 0:
                nil.append(i)

        if len(nil) == 1:
            if nil == self.index or nil == ((self.index + 2) % 4):
                return 5 # we nil
            else:
                return 6 # they nil
        if len(nil) == 2:
            if self.index in nil:
                if ((self.index + 2) % 4) in nil:
                    return 8 # double nil (us)
                else:
                    return 7 # nil vs nil
            elif ((self.index + 2) % 4) in nil:
              return 7 # nil vs nil
            else:
                return 8 # double nil (them)

        total_bids = sum(game.bids)
        if total_bids < 8:
            return 0
        if total_bids < 11:
            return 1
        if total_bids < 14:
            return 2
        if total_bids < 15:
            return 3
        else:
            return 4
