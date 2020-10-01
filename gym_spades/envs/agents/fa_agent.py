from gym_spades.envs.spades.player import player

import numpy as np
import itertools
import random

# function approximation agent
class fa_agent(player):

    def __init__(self):
        super().__init__()
        self.round_type = None

    def _play(self, game):
        if game == None:
            return
            
        from gym_spades.envs.spades import cards
        # print("playing:",self.index)
        #cards.print_hand(self.hand)
        actions = self.get_legal_cards(game)
        # for action in actions:
        #     self.get_features(game, action)
        # if len(actions) == 0:
        #     return 0
        return random.choice(actions)

    def _get_feature_space(self):
        return [0]*64 # size of the vector returned by get_state

    def get_features(self, game, action):
        
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

    def _discrete(self, result, size):
        ret = [0]*size
        ret[result] = 1
        return ret

    def _action_is_winning(self, game, action):
        from gym_spades.envs.spades import cards

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

    def _action_breaks_bid(self, game, action):
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

    def _num_suit_lead_in_round(self, game, action):
        from gym_spades.envs.spades import cards

        if game.suit_lead == game.NO_LEAD:
            return game.num_suit_lead_in_round[cards.suit(action)]
        else:
            return game.num_suit_lead_in_round[game.suit_lead]
    
    def _action_is_cutting(self, game, action):
        from gym_spades.envs.spades import cards

        if game.suit_lead == 5: # no lead
            return 0
        elif cards.suit(action) == cards.SPADES and game.suit_lead != cards.SPADES:
            return 0
        return 1

    def _action_is_following(self, game, action):
        from gym_spades.envs.spades import cards

        if game.suit_lead == 5: # no lead
            return 0
        elif cards.suit(action) == game.suit_lead:
            return 1
        return 0

    def _action_is_boss_in_suit(self, game, action):
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

    # _discrete(8)
    def _get_round_type(self, game):
        nil = []
        for i, b in enumerate(game.bids):
            if b == 0:
                nil.append(i)
        
        if len(nil) == 1:
            if self.index in nil or ((self.index + 2) % 4) in nil:
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
    def _can_win(self, game):
        from gym_spades.envs.spades import cards

        for c in self.legal_cards:
            if cards.suit(c) == game.winning_suit: # either lead or spades
                if cards.rank(c) > game.winning_rank:
                    return 1
        return 0
    
    # binary
    def _partner_is_winning(self, game):
        if game.winning == (self.index + 2) % 4:
            return 1
        return 0

    # _discrete(4)
    def _have_next_highest_in_suit(self, game):
        from gym_spades.envs.spades import cards

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
