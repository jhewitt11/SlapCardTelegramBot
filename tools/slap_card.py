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

        self.cards = [(suit, value) for suit in self.suits for value in self.values]

    def shuffle(self):
        random.shuffle(self.cards)

        return self.cards


# pass in player list - class
# pass in pace

class SlapCard():
    def __init__(self):

        self.enrolled = {}
        self.players = None
        self.pace = 5 #TODO
        self.winner = -1
        self.pot = []
        self.win_condition_flag = False
        self.hands = None
        self.deck = Deck().shuffle()

    def deal(self):
        self.hands = [[] for x in range(self.players)]
        for i, card in enumerate(self.deck):
            self.hands[i % self.players].append(card)

    async def monitor_player_input(self):
        while True:
            await asyncio.sleep(0.1)
            for i in range(1, self.players+1):
                if keyboard.is_pressed(str(i)):
                    return i

    async def start_game(self):
        k = 0
        while self.win_condition_flag == False :

            # Go to the next player hand that has cards
            while len(self.hands[k % self.players]) == 0 : 
                k += 1

            card = self.hands[k % self.players].pop()
            self.pot.append(card)

            
            print(card)
            input_task = asyncio.create_task(self.monitor_player_input())

            await asyncio.sleep( random.uniform(0.5, 1.5) )

            if not input_task.done():
                input_task.cancel()
            else:
                quickest_player = await input_task

                if card[0] == 'hearts':
                    self.hands[quickest_player] += self.pot
                    self.pot = []
                    print(f'good slap')
                else:
                    print(f'bad slap')

            k += 1
            scores = [len(x) for x in self.hands]
            print(scores, '\n')

            if len(self.pot) == 52:
                self.win_condition_flag = True

            for hand in self.hands :
                if len(hand) == 52 :
                    self.win_condition_flag = True


async def start_slap_game():
    game = SlapCard()
    game.deal()
    await game.start_game()

#asyncio.run(start_slap_game())


'''
token_name = 'TELEGRAM_TAD_KEY'
token = os.environ.get(token_name)

# Create the Application and pass it your bot's token.
application = Application.builder().token(token).build()

'''