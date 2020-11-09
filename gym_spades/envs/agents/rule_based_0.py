import numpy as np
from gym_spades.envs.spades import player, cards
from gym_spades.envs.agents import agent, agent_player

import sys

# This agent is not a learning agent, just a rules-based algorithm
# that picks a card based on the cards taht have been played that round and what it can see in its hand

class rule_based_0(agent):

    def __init__(self):
        super().__init__()

    def create_player(self):
        return rule_based_player(self)

class rule_based_player(agent_player):

    def __init__(self, parent):
        super().__init__(parent)
        self.name = 'heuristic'

    # no choice for bidding - sorry!
    def _play(self, game):

        if game == None:
            return

        #print("The round so far:\t", [cards.card_str(c) for c in game.round_so_far])
        #print("Your hand:\t", [cards.card_str(c) for c in self.hand])

        #Cards in our hand that can be played
        legal_cards = self.get_legal_cards(game) #This array is sorted
        card_suits = np.ndarray.tolist(np.floor_divide(legal_cards, 13))
        card_ranks = np.ndarray.tolist(np.mod(legal_cards, 13))

        #If there is only one card in our hand, there are no decisions to be made
        if len(legal_cards) == 0:
            print("NO LEGAL CARDS!!")
            print("CARDS ARE:", self.hand)
            print("index:", self.index)
            print("hist:", game.round_so_far, game.round_counter)
        if len(legal_cards) == 1:
            card = legal_cards[0]
            return card

        #This vector holds the value for the number of cards for each suit
        num_each_suit = [0,0,0,0]
        for c in card_suits:
            num_each_suit[c] = num_each_suit[c] + 1

        #If there are any non-spades cards, store the list indicies for all the non-spades cards
        if num_each_suit[0] < len(legal_cards):
            non_spades_ids = slice(num_each_suit[0], len(legal_cards))



        #Rules for playing when bid is not nill
        if self.bid_amount != 0:

            #When leading in a round
            if len(game.round_so_far) == 0:
                #If you can't play a spades, play the highest ranking non-spades card
                if num_each_suit[0] == 0:
                    card_id = card_ranks[non_spades_ids].index(max(card_ranks[non_spades_ids])) + num_each_suit[0]
                    card = legal_cards[card_id]
                    return card
                #Otherwise play the highest ranking spades card (this will be the last of the spades)
                else:
                    card_id = num_each_suit[0]-1
                    card = legal_cards[card_id]
                    return card

            #When not leading the round
            else:
                #Find the leading suit
                lead_suit = game.round_so_far[0]//13

                #Find the current winning card
                top_card = game.round_so_far[0]
                suit = lead_suit
                for c in game.round_so_far:
                    if c//13 == 0 and suit != 0:
                        suit = 0
                        top_card = c
                    elif c//13 == suit and c%13 > top_card%13:
                        top_card = c

                top_suit = top_card//13
                top_rank = top_card%13


                #If have cards in the leading suit,
                if num_each_suit[lead_suit] != 0:
                    #the legal_cards list should only contain cards of this one suit


                    #if can win the round
                    #i.e. current winning card is same suit as leading suit
                    #and have card with rank larger than current winning card
                    if lead_suit == top_suit and top_rank < card_ranks[len(legal_cards)-1]:
                        #if 4th player in the round
                        if len(game.round_so_far) == 3:
                            #use smallest possible card to win
                            id = 0
                            while card_ranks[id] <= top_rank:
                                id = id + 1

                            card = legal_cards[id]
                            return card
                        #if 2nd or 3nd in round
                        else:
                            #Use the maximum rank card of this suit
                            card = legal_cards[len(legal_cards)-1]
                            return card

                    #if it's not possible to win the round
                    else:
                        #play smallest card of the suit
                        card = legal_cards[0]
                        return card


                #If don't have cards in leading suit
                else:
                    #if top card is spades and can beat it
                    if top_suit == 0 and num_each_suit[0] != 0 and card_ranks[num_each_suit[0]-1] > top_rank:
                        #if 4th player in round
                        if len(game.round_so_far) == 3:
                            #use smallest possible spades to win
                            id = 0
                            while card_ranks[id] <= top_rank:
                                id = id + 1

                            card = legal_cards[id]
                            return card
                        #if 2nd or 3rd player in round
                        else:
                            #play largest spades card
                            card = legal_cards[num_each_suit[0]-1]
                            return card

                    #if unable to beat the top card
                    else:
                        #if only have spades cards
                        if num_each_suit[0] == len(legal_cards):
                            #play smallest spades
                            card = legal_cards[0]
                            return card
                        #if can use a non-spades card
                        else:
                            #play smallest non-spades card
                            card_id = card_ranks[non_spades_ids].index(min(card_ranks[non_spades_ids])) + num_each_suit[0]
                            card = legal_cards[card_id]
                            return card



        #Rules for playing when bid is nil
        else:
            #When leading in a round
            if len(game.round_so_far) == 0:
                #If you can only play a spades, play the lowest ranking spades card
                if num_each_suit[0] == len(legal_cards):
                    card = legal_cards[0]
                    return card
                #Otherwise play the lowest ranking non-spades card
                else:
                    card_id = card_ranks[non_spades_ids].index(min(card_ranks[non_spades_ids])) + num_each_suit[0]
                    card = legal_cards[card_id]
                    return card

            #When not leading a round
            else:
                #Find the leading suit
                lead_suit = game.suit_lead

                #Find the current winning card
                top_suit = game.winning_suit
                top_rank = game.winning_rank


                #if had card of leading suit
                if num_each_suit[lead_suit] != 0:
                    #if suit of top card is not equal to leading suit
                    if top_suit != lead_suit:
                        #play largest ranked card
                        card = legal_cards[len(legal_cards)-1]
                        return card
                    #if suit of top card is equal to that of leading suit
                    else:
                        #if have card of rank smaller than top card
                        if card_ranks[0] < top_rank:
                            #play largest ranked card that still loses
                            id = len(legal_cards)-1
                            while card_ranks[id] >= top_rank:
                                id = id - 1

                            card = legal_cards[id]
                            return card
                        #if don't have card smaller than top card
                        else:
                            #play smallest ranked card in that suit
                            card = legal_cards[0]
                            return card

                #if didn't have card of leading suit
                else:
                    #if have spade
                    if num_each_suit[0] != 0:
                        #if top card is a spade and have spade of lower value
                        if top_suit == 0 and card_ranks[0] < top_rank:
                            #play largest spade that still loses
                            id = num_each_suit[0]-1
                            while card_ranks[id] >= top_rank:
                                id = id - 1

                            card = legal_cards[id]
                            return card
                        #if either top card is not a spade or didn't have spade of lower value
                        else:
                            #if can avoid playing a spade
                            if num_each_suit[0] != len(legal_cards):
                                #play largest ranked nonspade card
                                card_id = card_ranks[non_spades_ids].index(max(card_ranks[non_spades_ids])) + num_each_suit[0]
                                card = legal_cards[card_id]
                                return card
                            #if must play a spade
                            else:
                                #play smallest ranked card
                                card = legal_cards[0]
                                return card
                    #if don't have spade
                    else:
                        #play largest ranked card
                        card = legal_cards[len(legal_cards)-1]
                        return card
