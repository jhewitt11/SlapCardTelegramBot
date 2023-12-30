import logging
import asyncio

from tools.game_bot import GameBot



logging.basicConfig(filename = 'app.log',
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:

    my_game = GameBot()
    my_game.run()



if __name__ == "__main__":
    main()