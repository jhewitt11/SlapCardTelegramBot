import os
import random
import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import logging

from .slap_card import Deck
from .slap_card import SlapCard


logger = logging.getLogger(__name__)


class GameBot:

    def __init__(self):
        self.game = None
        self.enrolled = {}

        token_name = 'TELEGRAM_TAD_KEY'
        token = os.environ.get(token_name)

        self.application = Application.builder().token(token).build()
        self.application.add_handler(CommandHandler(["help", "info"], self.info))
        self.application.add_handler(CommandHandler("start", self.enroll_start))
        self.application.add_handler(CommandHandler("stop", self.enroll_stop))
        self.application.add_handler(CommandHandler('join', self.join))
        # TODO self.application.add_handler(CommandHandler('leave', self.leave))

        self.application.add_handler(CommandHandler("slap", self.slap))

        logger.info("GameBot Init completed")
    
    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def print_tasks(self, task_list):
        for task in task_list:
            print(task)

    def remove_job_if_exists(self, name: str, context: ContextTypes.DEFAULT_TYPE):

        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        
        if not current_jobs:
            return False

        for job in current_jobs:
            job.schedule_removal()
        return True

    async def game_start(self, context: ContextTypes.DEFAULT_TYPE):

        k = 0
        while self.game.win_condition_flag == False :

            # play next card
            #
            card = self.game.next_card()

            # display card
            await context.bot.send_message(context.job.chat_id, text = f'{card}')

            # await player input for a bit
            await asyncio.sleep( random.uniform(1, 2))

            ## slaps will resolve in the slap command fx

            self.game.update_game_status()

        if self.game.winner == -1 :
            await context.bot.send_message(context.job.chat_id, text = 'No winner, pot is full.')

        else :
            await context.bot.send_message(context.job.chat_id, text = f'Player {self.game.winner} wins!')

    async def slap(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        # identify which player slapped
        user_id = update.message.from_user.id

        if self.game.resolve_slap(user_id):
            #await context.bot.send_message(context.job.chat_id, text = 'good slap')
            await update.effective_message.reply_text('good slap')

        #else :
            #await update.effective_message.reply_text('bad slap')



        return

    async def game_wrapper(self, context: ContextTypes.DEFAULT_TYPE):

        player_list = list(self.enrolled.keys())

        chat_message = f'The signup period has ended. The game will begin shortly.\n\nPlayers enrolled : \n'

        player_text = ''
        for p in player_list :
            player_text += f'{p}\n'

        await context.bot.send_message(context.job.chat_id, text=chat_message+player_text)
        logger.info(chat_message)

        await asyncio.sleep(1)
        instructions = f'Use the /slap command when a valid card is played. The pot goes to the fastest hand! The game is over when one player has all the cards.'
        await context.bot.send_message(context.job.chat_id, text=instructions)

        await asyncio.sleep(5)
        valid_card_text = f'Valid cards for this round : Hearts'
        await context.bot.send_message(context.job.chat_id, text=valid_card_text)

        await asyncio.sleep(2)


        #
        # Prepare game.
        # 
        self.game = SlapCard()
        self.game.prepare_game(player_list)

        #
        # Start game.
        await self.game_start(context)

        # clean up game
        self.game = None
        self.enrolled = {}

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sends explanation on how to use the bot."""

        text_l = [
        "Welcome to Slap Card! Use /start <seconds> to start a signup period for the next Slap Card game.\n\n",
        "Use /join and /leave during the signup period to reserve your seat or give it up.\n\n",
        "After <seconds> there will be a few instructions and then the game will begin.\n\n",
        "Race the other players to /slap valid cards first and win the pot!\n\n",
        "Valid cards will be announced before each round."
        ]


        all_text = ""
        for text in text_l : 
            all_text += text

        await update.message.reply_text(all_text)

    async def enroll_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''
        Starts an enrollment period that immediately leads to a SlapCard game.

        '''
        chat_id = update.effective_message.chat_id

        try:
            length = float(context.args[0])
            if length < 0:
                await update.effective_message.reply_text("Invalid. Use a positive number.")
                return

            text = ''
            job_removed = self.remove_job_if_exists(str(chat_id), context)
            if job_removed:
                text += "NOTE : Replaced existing enrollment period with a new one.\n\n"

            context.job_queue.run_once(self.game_wrapper, length, chat_id=chat_id, name= f'alarm_{str(chat_id)}', data=length)

            text_l =[
            "Prepare for the next round of Slap Card!\n\n",
            "Use /join and /leave to reserve your seat or give it up."
            ]

            all_text = ""
            for text in text_l : 
                all_text += text

            await update.effective_message.reply_text(all_text)

        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /start <seconds>.")

    async def enroll_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Stop the sign-up period if it has begun.


        """
        chat_id = update.message.chat_id
        job_removed = self.remove_job_if_exists(f'alarm_{str(chat_id)}', context)
        text = "Sign-up and Slap Card game cancelled." if job_removed else "There is no active sign-up period"
        await update.message.reply_text(text)

    async def join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''
        Command for enrolling in a game.

        A user's ID will be added to the enrolled list if the timer is active.
        
        '''

        chat_id = update.message.chat_id

        jobs = context.job_queue.get_jobs_by_name(f'alarm_{str(chat_id)}')

        if not jobs :
            logger.info(f'No active signup period. Use /start <seconds> to begin one.')
        else:

            if self.enrolled.get(update.message.from_user.id) == None :
                self.enrolled[update.message.from_user.id] = 1
                logger.info(f'{update.message.from_user.id} joined!')

        return



    async def leave(self, update : Update, context : ContextTypes.DEFAULT_TYPE):
        '''
        '''

        chat_id = update.message.chat_id

        user_id = update.message.from_user.id

        if self.enrolled.get(user_id) != None :
            self.enrolled.pop(user_id)

        return