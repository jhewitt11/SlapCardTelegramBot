import asyncio
import keyboard
import random

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

class Deck:
    def __init__(self):
        self.suits = ['hearts', 'diamonds', 'spades', 'clubs']

        self.values = ['ace', 'two', 'three', 'four', 'five', 'six',
                        'seven', 'eight', 'nine', 'ten', 'jack',
                        'queen', 'king']

        self.cards = [(value, suit) for suit in self.suits for value in self.values]

    def shuffle(self):
        random.shuffle(self.cards)

        return self.cards


# pass in player list - class

class SlapCard():
    def __init__(self):

        self.player_list = None
        self.player_count = None
        self.k = 0      # k is a counter. It does not hold a player specific value, nor does it count turns accurately
        
        self.pot = []
        self.hands = None
        self.deck = Deck().shuffle()
        self.first_slap_flag = False

        self.winner = -1
        self.win_condition_flag = False


    def prepare_game(self, player_list):
        self.player_list = player_list
        self.player_count = len(player_list)

        # deal deck to different hands
        self.hands = [[] for x in range(self.player_count)]
        for i, card in enumerate(self.deck):
            self.hands[i % self.player_count].append(card)


    def next_card(self):

        while len(self.hands[self.k % self.player_count]) == 0:
            self.k += 1

        card = self.hands[self.k % self.player_count].pop(0)

        self.pot.append(card)
        self.first_slap_flag = False

        return card


    def resolve_slap(self, player_id):

        #ToDo : verify player_id validity

        if self.first_slap_flag == True :
            return False

        # ToDo : Make a separate method that abstracts slap validity
        if self.pot[-1][1] == 'hearts':
            self.first_slap_flag == True

            player_ind = self.player_list.index(player_id)

            self.hands[player_ind] += self.pot
            self.pot = []

            return True

        return False


    def update_game_status(self):

        if len(self.pot) == 52:
            self.win_condition_flag = True

        for i, hand in enumerate(self.hands) :
            if len(hand) == 52 :
                self.win_condition_flag = True
                self.winner = self.player_list[i]




    '''
    def deal(self):
        self.hands = [[] for x in range(self.player_count)]
        for i, card in enumerate(self.deck):
            self.hands[i % self.player_count].append(card)
    '''
