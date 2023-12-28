import os
import asyncio


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import logging

from .slap_card import Deck
from .slap_card import SlapCard
from .slap_card import start_slap_game


logger = logging.getLogger(__name__)


class GameBot:

    def __init__(self):
        self.game = None

        token_name = 'TELEGRAM_TAD_KEY'
        token = os.environ.get(token_name)
        self.application = Application.builder().token(token).build()

        self.application.add_handler(CommandHandler(["info"], self.info))
        self.application.add_handler(CommandHandler("start", self.start_enroll))
        self.application.add_handler(CommandHandler("unset", self.unset))
        self.application.add_handler(CommandHandler('join', self.join))

        logger.info("GameBot Init completed")
    
    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    def print_tasks(self, task_list):
        for task in task_list:
            print(task)

    def remove_job_if_exists(self, name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:

        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        
        if not current_jobs:
            return False

        for job in current_jobs:
            job.schedule_removal()
        return True

    async def alarm(self, context: ContextTypes.DEFAULT_TYPE) -> None:

        chat_message = f'Enrollment over. The game will begin shortly.\nPlayers enrolled : {list(self.game.enrolled.keys())}'

        await context.bot.send_message(context.job.chat_id, text=chat_message)
        logger.info(chat_message)





    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Sends explanation on how to use the bot."""
        await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

    async def start_enroll(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        '''
        Starts an enrollment period that immediately leads to a SlapCard game.

        This command creates a new SlapCard instance.
        '''
        chat_id = update.effective_message.chat_id

        try:
            due = float(context.args[0])
            if due < 0:
                await update.effective_message.reply_text("Invalid. Use a positive number.")
                return

            text = ''
            job_removed = self.remove_job_if_exists(str(chat_id), context)
            if job_removed:
                text += "NOTE : Replaced existing enrollment period with a new one.\n\n"

            context.job_queue.run_once(self.alarm, due, chat_id=chat_id, name= f'alarm_{str(chat_id)}', data=due)
            text += "Prepare for the next round of SlapCard!\nUse the /join command to claim a seat."

            self.game = SlapCard()

            await update.effective_message.reply_text(text)

        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /start <seconds>")

    async def unset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Remove the job if the user changed their mind."""
        chat_id = update.message.chat_id
        job_removed = self.remove_job_if_exists(str(chat_id), context)
        text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
        await update.message.reply_text(text)

    async def join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''
        Command for enrolling in a game.

        A user's ID will be added to the enrolled list if the timer is active.
        
        '''

        chat_id = update.message.chat_id

        jobs = context.job_queue.get_jobs_by_name(f'alarm_{str(chat_id)}')

        if not jobs :
            logger.info(f'Enroll timer not found')
        else:
            logger.info(f'{update.message.from_user.id} enrolled.')

            if self.game.enrolled.get(update.message.from_user.id) == None :
                self.game.enrolled[update.message.from_user.id] = 1
                logger.info(f'{update.message.from_user.id} joined!')

        return
