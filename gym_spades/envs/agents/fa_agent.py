from gym_spades.envs.spades.player import player
from gym import error, spaces, utils

import itertools
import random

# function approximation agent
class fa_agent(player):

    def __init__(self):
        self.round_type = None

    def _play(self, state, round_so_far, spades_broken):
        return random.choice(self.get_legal_cards(round_so_far, spades_broken))

    def get_state_space(self):
        return 44 # size of the vector returned by get_state

    def get_state(self, game):
        # https://arxiv.org/pdf/1912.11323v1.pdf page 10, top right
        
        # round type of:
        # 0: strong under  no nils, sum of bids < 8
        # 1: under         no nils, sum of bids in {8-10}
        # 2: over          no nils, sum of bids in {11-13}
        # 3: 14            no nils, sum of bids == 14 
        # 4: strong over   no nils, sum of bids > 14
        # 5: we nil        single nil bid in partnership
        # 6: opponents nil single nil bid in opponents
        # 7: nil vs nil    each has one nil                        # illegal
        # 8: double nil    both players in a partnership bid nil   # illegal
        
        if self.round_type is None:
            self.round_type = [0]*8
            self.round_type[self.get_round_type(game)] = 1

        player_lead = [0]*4
        player_lead[game.starting_player] = 1
        suit_lead = [0]*4
        if game.suit_lead != game.NO_LEAD:
            suit_lead[game.suit_lead] = 1
        self.legal_cards = self.get_legal_cards(game.round_so_far, game.spades_broken)

        if game.spades_played:
            spades_played = 1
        else:
            spades_played = 0

        # flatten the list
        ret = list(itertools.chain.from_iterable([
            self.round_type,
            player_lead, 
            suit_lead,
            self.have_next_highest_in_suit(game),
            self.smallest_suit(),
            self.player_has_suit(game),
            game.num_suit_lead_in_round,
            [
                spades_played,
                self.can_win(game),
                self.partner_is_winning(game),
                # trick num
                game.round_counter,
            ],
        ]))
        print(len(ret))
        print(ret)
        return(ret)

    # discrete(8)
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

    # binary
    def can_win(self, game):
        from gym_spades.envs.spades import cards

        for c in self.legal_cards:
            if cards.suit(c) == game.winning_suit: # either lead or spades
                if cards.rank(c) > game.winning_rank:
                    return 1
        return 0
    
    # binary
    def partner_is_winning(self, game):
        if game.winning == (self.index + 2) % 4:
            return 1
        return 0

    # discrete(4)
    def have_next_highest_in_suit(self, game):
        from gym_spades.envs.spades import cards

        ret = [0]*4
        for i, discard in enumerate(game.discard_by_suit):
            if len(self.hand_by_suit[i]) == 0:
                continue

            if len(discard) == 0:
                if self.hand_by_suit[i][-1] == cards.KING:
                   ret[i] = 1
                continue 
            discard.sort()
            if discard[-1] < self.hand_by_suit[i][-1]:
                ret[i] = 1
        return ret

    # discrete(4)
    def smallest_suit(self):
        ret = [0]*4
        n = -1
        index = 0
        for i, s in enumerate(self.hand_by_suit):
            if len(s) != 0 and len(s) < n:
                n = len(s)
                index = i
        ret[index] = 1
        return ret

    # discrete(3*4)
    def player_has_suit(self, game):
        r = []
        for i in range(4):
            if i != self.index:
                r.append(game.player_played_off_in_suit[i])
        return list(itertools.chain.from_iterable(r))
