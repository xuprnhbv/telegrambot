from telegram.ext import Updater
from colorama import Fore, init
from handlers import add_all_handlers
from dailymeme import init_daily_meme
from consts import TEXT_COLOR, DAILY_MEME_HOUR
import threading
import os

RELATIVE_TOKEN_PATH = r'..\token.key'


def main():
    """
    Main function. Creates bot, adds all handlers and runs.

    :return:
    """
    init()
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    print('{text}Getting bot token from {url}{}{text}...'.format(token_path, text=TEXT_COLOR, url=Fore.LIGHTYELLOW_EX))
    token = get_token()
    print('{text}Token: {tcolor}{}{text}'.format(token, text=TEXT_COLOR, tcolor=Fore.GREEN))

    print('{text}Setting up updater...'.format(text=TEXT_COLOR))
    updater = Updater(token=token, use_context=True)

    print('{text}Adding handlers...'.format(text=TEXT_COLOR))
    add_all_handlers(updater)
    print('{text}Done with handlers.'.format(text=TEXT_COLOR))

    print('{text}Starting the bot...'.format(text=TEXT_COLOR))
    updater.start_polling()
    print('{text}Adding daily meme task...'.format(text=TEXT_COLOR))
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[updater], daemon=True)
    daily_meme_thread.start()
    print('{text}Meme will be sent everyday at {yellow}{}{text}.'.format(DAILY_MEME_HOUR, yellow=Fore.LIGHTYELLOW_EX,
                                                                         text=TEXT_COLOR))
    print('{nice}BOT RUNNING SUCCESSFULLY'.format(nice=Fore.LIGHTGREEN_EX))
    print('{text}Press Enter to close...'.format(text=TEXT_COLOR))
    input()
    print('{text}Stopping Daily Meme thread...'.format(text=TEXT_COLOR))
    print('{text}Stopping updater...'.format(text=TEXT_COLOR))
    updater.stop()
    print('{red}BOT STOPPED SUCCESSFULLY{default}'.format(red=Fore.LIGHTRED_EX, default=Fore.WHITE))


def get_token():
    """
    Reads token file and returns it.
    :return: bot token. None if something is invalid.
    """
    with open(RELATIVE_TOKEN_PATH, 'r') as token_file:
        return token_file.read()
    return None


main()
