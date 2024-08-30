from telegram.ext import Updater
from colorama import Fore, init
from handlers import add_all_handlers
from dailymeme import init_daily_meme
from consts import TEXT_COLOR, DAILY_MEME_HOUR, RELATIVE_TOKEN_PATH
import logger
import threading
import os
import sys


def get_token():
    """
    Reads token file and returns it.
    :return: bot token. None if something is invalid.
    """
    with open(RELATIVE_TOKEN_PATH, 'r') as token_file:
        return token_file.read()

def main():
    """
    Main function. Creates bot, adds all handlers and runs.

    :return:
    """
    init()
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    logger.log_setup()
    logger.print_log('Getting bot token from {}...'.format(token_path))
    token = get_token()
    logger.print_log('Token: {}'.format(token))

    logger.print_log('Setting up updater...')
    updater = Updater(token=token, use_context=True)

    logger.print_log('Adding handlers...')
    add_all_handlers(updater)
    logger.print_no_log('Done with handlers.')

    logger.print_log('Starting the bot...')
    updater.start_polling()
    logger.print_log('Adding daily meme task...')
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[updater], daemon=True)
    daily_meme_thread.start()
    logger.print_log('Meme will be sent everyday at {}.'.format(DAILY_MEME_HOUR))
    logger.print_no_log('BOT RUNNING SUCCESSFULLY')
    logger.print_no_log('Press Enter to close...')
    input()
    logger.print_log('Stopping Daily Meme thread...')
    logger.print_log('Stopping updater...')
    updater.stop()
    logger.print_no_log('BOT STOPPED SUCCESSFULLY')


def main_bg():
    init()
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    logger.log_setup(print_console=False)
    logger.print_log('Getting bot token from {}...'.format(token_path))
    token = get_token()
    logger.print_log('Token: {}'.format(token))

    logger.print_log('Setting up updater...')
    updater = Updater(token=token, use_context=True)

    logger.print_log('Adding handlers...')
    add_all_handlers(updater)

    logger.print_log('Starting the bot...')
    updater.start_polling()
    logger.print_log('Adding daily meme task...')
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[updater], daemon=True)
    daily_meme_thread.start()
    logger.print_log('Meme will be sent everyday at {}.'.format(DAILY_MEME_HOUR))
    updater.idle()


if __name__ == '__main__':
    if "bg" in sys.argv:
        main_bg()
    else:
        main()
