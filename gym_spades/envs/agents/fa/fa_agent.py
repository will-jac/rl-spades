from __future__ import annotations

from gym_spades.envs.spades import spades, cards, player
from gym_spades.envs.agents import agent, agent_player

import numpy as np
import itertools
import random

class fa_agent(agent):
    def _play(self, state: dict[cards, list[int]]) -> cards:
        ...

    def _get_feature_space(self) -> int:
        return fa_player.get_feature_space()

    def create_player(self):
        return fa_player(self)

# function approximation agent
class fa_player(agent_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.round_type = None

        self.prev_value = None
        self.prev_features = None

        # statistics
        self.rewards = []

        self.cumulative_reward = 0.0

        self.name='fa_player'

    def reset(self, index: int, hand: list[cards]):
        super().reset(index, hand)
        self.prev_value = None
        self.prev_features = None

    def _play(self, game: spades) -> cards:
        # print("playing:",self.index)
        #cards.print_hand(self.hand)
        if game is None:
            state = None
        else:
            state = {}
            actions = self.get_legal_cards(game)
            for action in actions:
                state[action] = self.get_features(game, action)

        if self.prev_value is None:
            self.prev_value, action, self.prev_features = self.parent._get_action(state)
        else:
            self.prev_value, action, self.prev_features = self._backup(state)

        return action

    def _backup(self, state: dict[cards, list[int]]) -> (float, cards):
        value, action, features = self.parent._get_action(state)
        td_error = self.reward + self.parent.discount_factor * value - self.prev_value

        #print(self.index, "backup",  self.parent.learning_rate, td_target, self.prev_features)
        # back up our weights
        # perform stochastic gradient descent (features, q_next)
        # pg 205
        self.parent.weights += self.parent.learning_rate * td_error * self.prev_features

        return value, action, features

    def result(self) -> (list[float], list[float]):
        return (self.rewards, self.parent.weights)

    @staticmethod
    def get_feature_space() -> int:
        return 66 # size of the vector returned by get_state

    def get_features(self, game: spades, action: cards) -> list[int]:

        if game is None or action is None:
            return 1

        # from gym_spades.envs.spades import cards
        # print(cards.card_str(action))
        # game = spades object, the current game being played
        # action = proposed card to be played

        # region round type
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
        # endregion round type
        # region player lead
        # [1,0,0,0] = our lead
        # [0,1,0,0] = prev player lead (second to play)
        # [0,0,1,0] = partner lead (third to play)
        # [0,0,0,1] = last to play
        player_lead = [0]*4
        player_lead[self.index - game.starting_player] = 1
        # endregion player lead
        # region suit lead
        # [0,0,0,0] = no lead yet (our lead)
        # [1,0,0,0] = spades
        # [0,1,0,0] = hearts
        # [0,0,1,0] = clubs
        # [0,0,0,1] = diamonds
        suit_lead = [0]*4
        if game.suit_lead != game.NO_LEAD:
            suit_lead[game.suit_lead] = 1
        # endregion suit lead
        # region action is winning
        self.action_winning = self._action_is_winning(game, action)
        # endregion action is winning
        # region round counter
        round_counter = [0]*13
        round_counter[game.round_counter] = 1
        # endregion round counter
        # flatten the list
        state = [
            [1], # bias term
            self._discrete(self.bid_amount, 13),
            self.round_type,
            player_lead,
            suit_lead,
            [
                # action type
                # wins the trick (eg play Q clubs on 3 clubs lead)
                self.action_winning,
                # play a spade on a non-spade lead
                self._action_is_cutting(game, action),
                # follow suit
                self._action_is_following(game, action),
                # can someone play a higher suit than us?
                self._action_is_boss_in_suit(game, action),
                # Could a future player have a higher card in suit?
                # Are they likely to be out of the suit?
                #self.likelihood_of_action_beaten_by_future_player(game, action),
                self._partner_is_winning(game),
            ],
            # how many times has the lead suit been lead?
            self._discrete(self._num_suit_lead_in_round(game, action), 13),
            # Not including
            # self.action_breaks_spades(game, action)
            # does this action break our bid?
            self._discrete(self._action_breaks_bid(game, action),2),
            #self._discrete(self._can_win(game),2),
            self._discrete(self._partner_is_winning(game),2),
            # trick num
            round_counter
        ]
        # print(state)
        ret = np.array(list(itertools.chain.from_iterable(state)))

        # print(len(ret))
        # print(np.shape(ret))
        # print(ret)
        return(ret)

    def _action_is_winning(self, game: spades, action: cards) -> int:

        if game.suit_lead == 5:
            # all first cards played are winning
            return 1

        if cards.suit(action) == cards.SPADES:
            if game.winning_suit != cards.SPADES:
                return 1
            elif game.winning_rank < cards.rank(action):
                # we're overtrumping
                return 1
            else:
                # someone else has a larger spade than action
                return 0
        else:
            if game.winning_suit == cards.SPADES:
                return 0
            elif game.winning_rank < cards.rank(action):
                # we're playing over
                return 1
            else:
                # someone else has a larger card in suit than action
                return 0

    def _action_breaks_bid(self, game: spades, action: cards) -> int:
        # if we bid nil, don't take a trick!
        if self.bid == 0:
            if self.action_winning:
                return 1
            return 0
        # if we need this trick in order to make our bid
        # ((num_rounds_remain - num_tricks_needed) == 0) - if > 0, then we've already lost our bid
        if (13 - game.round_counter) - (self.team_bid - self.team_tricks) == 0:
            # we need this trick, and this action isn't winning!
            if not self.action_winning:
                return 1
        return 0

    def _num_suit_lead_in_round(self, game: spades, action: cards) -> int:
        if game.suit_lead == game.NO_LEAD:
            return game.num_suit_lead_in_round[cards.suit(action)]
        else:
            return game.num_suit_lead_in_round[game.suit_lead]

    def _action_is_cutting(self, game: spades, action: cards) -> int:
        from gym_spades.envs.spades import cards

        if game.suit_lead == 5: # no lead
            return 0
        elif cards.suit(action) == cards.SPADES and game.suit_lead != cards.SPADES:
            return 0
        return 1

    def _action_is_following(self, game: spades, action: cards) -> int:
        from gym_spades.envs.spades import cards

        if game.suit_lead == 5: # no lead
            return 0
        elif cards.suit(action) == game.suit_lead:
            return 1
        return 0

    def _action_is_boss_in_suit(self, game: spades, action: cards) -> int:
        from gym_spades.envs.spades import cards

        s = cards.suit(action)

        discard = game.discard_by_suit[s]

        if len(discard) == 0:
            # if there's no cards played in this suit and we have the ace, ret 1
            if cards.rank(action) == cards.ACE:
                return 1
            return 0

        # TODO: figure out a faster way to do this
        for rank in range(cards.ACE, cards.TWO, -1):
            if cards.rank in discard:
                continue
            elif rank == cards.rank(self.hand_by_suit[s][-1]):
                return 1
            # not found in either
            return 0
