from gym_spades.envs.spades.player import player
from gym_spades.envs.spades.spades import cards, spades
from gym import error, spaces, utils

# 'normal' tabular based agent
class agent(player):

    def get_state_space(self):
        return(spaces.Tuple(
            ##### round-specific
            # round_type
            spaces.Discrete(9),
            
            ##### trick-specific
            #'player_lead'
            spaces.Discrete(4),
            #'suit_lead'
            spaces.Discrete(5),
            #'spades_played'
            spaces.Discrete(2),
            #'can_win'
            spaces.Discrete(2),
            #'partner_is_winning'
            spaces.Discrete(2),


            ## hand-specific
            #'have_next_highest_in_suit'
            spaces.MultiBinary(4),
            #'smallest_suit'
            spaces.Discrete(4),
            
            # progression of round
            #'trick_num'
            spaces.Discrete(13),
            #'player_has_suit'
            spaces.MultiBinary(3*4),
            # num_suit_lead_in_round
            spaces.MultiBinary(3*4*4),
            
            # not sure how to implement these...
            #'player_may_be_out_of_suit'
            spaces.MultiBinary(3*4),
            #'player_may_have_boss_in_suit'
            spaces.MultiBinary(3*4)
        ))

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
            self.round_type = self.get_round_type(game)

        return (
            self.round_type,
            # in this, agent == player 0
            4 - len(game.round), 
        )

        # end game conditions
        # partnership can win game this round
        # opponents can win game this round
        
 

        return