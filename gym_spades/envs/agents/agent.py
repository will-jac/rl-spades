from gym_spades.envs.spades import cards, player, spades
from gym import error, spaces, utils

from typing import Any, List

# breaking change: agent has players, is not a player itself
# 'normal' tabular based agent
class agent(player):

    def create_player(self):
        return agent_player(self)

class agent_player(player):

    def __init__(self, parent: agent):
        super().__init__()
        self.parent = parent

    def _play(self, game: spades) -> 'cards':
        self.parent._play(game)

    def set_reward(self, winning_player):
        # called by game after each trick

        if winning_player in [self.index, self.partner_index]:
            self.team_tricks += 1

        # can we make our bid still?
        if (self.team_bid - self.team_tricks) > (13 - len(self.rewards)):
            self.can_make_bid = False

        if self.lost_bid:
            self.reward = 0
        # did we bid nil?
        elif self.bid_amount != 0:
            if self.can_make_bid:
                if winning_player == self.index:
                    if self.team_tricks < self.team_bid:
                        self.reward = 10
                    else:
                        self.reward = 1
                elif winning_player == self.partner_index:
                    self.reward = 0
                else:
                    # opponents took the trick
                    self.reward = 0
            else:
                self.reward = -1*(sum(self.rewards) + 10*self.team_bid)
        # we bid nil
        else:
            if winning_player == self.index:
                self.reward = -100
            elif len(self.rewards) == 12:
                self.reward = 100
            else:
                self.reward = 0

        if not self.can_make_bid:
            self.lost_bid = True

        self.rewards.append(self.reward)

    def _discrete(self, result, size):
        ret = [0]*size
        ret[result] = 1
        return ret

    def _get_round_type(self, game):
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

    def _partner_is_winning(self, game):
        if game.winning == (self.index + 2) % 4:
            return 1
        return 0


class td_player(agent_player):

    def _play(self, game):
        return 0

    # DO NOT USE FOR FUNCTION APPROXIMATION
    # this is actually probably pretty good for state though (although pretty large - 44!)
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
        # 7: nil vs nil    each has one nil
        # 8: double nil    both players in a partnership bid nil

        if self.round_type is None:
            self.round_type = [0]*9
            self.round_type[self._get_round_type(game)] = 1

        # [1,0,0,0] = our lead
        # [0,1,0,0] = prev player lead (second to play)
        # [0,0,1,0] = partner lead (third to play)
        # [0,0,0,1] = last to play
        player_lead = [0]*4
        player_lead[self.index - game.starting_player] = 1
        # [0,0,0,0] = no lead yet (our lead)
        # [1,0,0,0] = spades
        # [0,1,0,0] = hearts
        # [0,0,1,0] = clubs
        # [0,0,0,1] = diamonds
        suit_lead = [0]*4
        if game.suit_lead != game.NO_LEAD:
            suit_lead[game.suit_lead] = 1
        self.legal_cards = self.get_legal_cards(game)

        if game.spades_played:
            spades_played = 1
        else:
            spades_played = 0

        # flatten the list
        state = [
            self.round_type,
            player_lead,
            suit_lead,
            self._have_next_highest_in_suit(game),
            self._smallest_suit(),
            self._player_does_not_have_suit(game),
            game.num_suit_lead_in_round,
            [
                spades_played,
                self._can_win(game),
                self._partner_is_winning(game),
                # trick num
                game.round_counter,
            ],
        ]
        print(state)
        ret = list(itertools.chain.from_iterable(state))

        print(len(ret))
        print(ret)
        return(ret)

    def _can_win(self, game):
        for c in self.legal_cards:
            if cards.suit(c) == game.winning_suit: # either lead or spades
                if cards.rank(c) > game.winning_rank:
                    return 1
        return 0

    def _have_next_highest_in_suit(self, game):
        ret = [0]*4
        for i, discard in enumerate(game.discard_by_suit):
            if len(self.hand_by_suit[i]) == 0:
                continue

            if len(discard) == 0:
                # if there's no cards played in this suit and we have the ace, ret 1
                if cards.rank(self.hand_by_suit[i][-1]) == cards.ACE:
                   ret[i] = 1
                continue

            # TODO: figure out a faster way to do this
            for rank in range(cards.ACE, cards.TWO, -1):
                if cards.rank in discard:
                    continue
                elif rank == cards.rank(self.hand_by_suit[i][-1]):
                    ret[i] = 1
                    break
                # not found in either
                else:
                    break
        return ret

    # _discrete(4)
    def _smallest_suit(self):
        ret = [0]*4
        n = 14
        index = 0
        for i, s in enumerate(self.hand_by_suit):
            if len(s) != 0 and len(s) < n:
                n = len(s)
                index = i
        ret[index] = 1
        return ret

    # _discrete(3*4)
    def _player_does_not_have_suit(self, game):
        r = []
        for i in range(4):
            if i != self.index:
                r.append(game.player_played_off_in_suit[i])
        return list(itertools.chain.from_iterable(r))

