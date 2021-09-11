from telegram.ext import Updater
from colorama import Fore, init
from handlers import add_all_handlers
from dailymeme import init_daily_meme
from consts import TEXT_COLOR, DAILY_MEME_HOUR, RELATIVE_TOKEN_PATH
import logger
import threading
import os
import sys


def main():
    """
    Main function. Creates bot, adds all handlers and runs.

    :return:
    """
    init()
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    logger.log_setup()
    logger.print_log('{text}Getting bot token from {url}{}{text}...'.format(token_path, text=TEXT_COLOR, url=Fore.LIGHTYELLOW_EX))
    token = get_token()
    logger.print_log('{text}Token: {tcolor}{}{text}'.format(token, text=TEXT_COLOR, tcolor=Fore.GREEN))

    logger.print_log('{text}Setting up updater...'.format(text=TEXT_COLOR))
    updater = Updater(token=token, use_context=True)

    logger.print_log('{text}Adding handlers...'.format(text=TEXT_COLOR))
    add_all_handlers(updater)
    logger.print_no_log('{text}Done with handlers.'.format(text=TEXT_COLOR))

    logger.print_log('{text}Starting the bot...'.format(text=TEXT_COLOR))
    updater.start_polling()
    logger.print_log('{text}Adding daily meme task...'.format(text=TEXT_COLOR))
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[updater], daemon=True)
    daily_meme_thread.start()
    logger.print_log('{text}Meme will be sent everyday at {yellow}{}{text}.'.format(DAILY_MEME_HOUR, yellow=Fore.LIGHTYELLOW_EX,
                                                                         text=TEXT_COLOR))
    logger.print_no_log('{nice}BOT RUNNING SUCCESSFULLY'.format(nice=Fore.LIGHTGREEN_EX))
    logger.print_no_log('{text}Press Enter to close...'.format(text=TEXT_COLOR))
    input()
    logger.print_log('{text}Stopping Daily Meme thread...'.format(text=TEXT_COLOR))
    logger.print_log('{text}Stopping updater...'.format(text=TEXT_COLOR))
    updater.stop()
    logger.print_no_log('{red}BOT STOPPED SUCCESSFULLY{default}'.format(red=Fore.LIGHTRED_EX, default=Fore.WHITE))


def main_bg():
    init()
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    logger.log_setup(print_console=False)
    logger.print_log('{text}Getting bot token from {url}{}{text}...'.format(token_path, text=TEXT_COLOR, url=Fore.LIGHTYELLOW_EX))
    token = get_token()
    logger.print_log('{text}Token: {tcolor}{}{text}'.format(token, text=TEXT_COLOR, tcolor=Fore.GREEN))

    logger.print_log('{text}Setting up updater...'.format(text=TEXT_COLOR))
    updater = Updater(token=token, use_context=True)

    logger.print_log('{text}Adding handlers...'.format(text=TEXT_COLOR))
    add_all_handlers(updater)

    logger.print_log('{text}Starting the bot...'.format(text=TEXT_COLOR))
    updater.start_polling()
    logger.print_log('{text}Adding daily meme task...'.format(text=TEXT_COLOR))
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[updater], daemon=True)
    daily_meme_thread.start()
    logger.print_log('{text}Meme will be sent everyday at {yellow}{}{text}.'.format(DAILY_MEME_HOUR, yellow=Fore.LIGHTYELLOW_EX,
                                                                         text=TEXT_COLOR))
    updater.idle()
    print('{red}BOT STOPPED SUCCESSFULLY'.format(red=Fore.LIGHTRED_EX))


def get_token():
    """
    Reads token file and returns it.
    :return: bot token. None if something is invalid.
    """
    with open(RELATIVE_TOKEN_PATH, 'r') as token_file:
        return token_file.read()
    return None


if __name__ == '__main__':
    if "bg" in sys.argv:
        main_bg()
    else:
        main()
