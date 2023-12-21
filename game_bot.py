import os
import json
import logging
import requests
import asyncio

from tools.commands import GameBot

from telegram import Update


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def main() -> None:
    my_game = GameBot()
    my_game.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()