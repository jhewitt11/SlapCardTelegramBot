import os
import json
import logging
import requests
import asyncio

from tools.commands import GameBot

from telegram import Update


# Enable logging
logging.basicConfig(filename = 'app.log',
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:

    my_game = GameBot()
    my_game.run()
    


if __name__ == "__main__":
    main()