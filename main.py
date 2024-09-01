from telegram.ext import Application, CallbackContext, ContextTypes
from handlers import add_all_handlers
from dailymeme import init_daily_meme
from consts import DAILY_MEME_HOUR, RELATIVE_TOKEN_PATH
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

def main(bg):
    token_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), RELATIVE_TOKEN_PATH))
    logger.log_setup(print_console=bg)
    logger.print_log('Getting bot token from {}...'.format(token_path))
    token = get_token()
    logger.print_log('Token: {}'.format(token))

    logger.print_log('Setting up application...')
    app = Application.builder().token(token).build()
    logger.print_log('Adding handlers...')
    add_all_handlers(app)

    logger.print_log('Adding daily meme task...')
    daily_meme_thread = threading.Thread(target=init_daily_meme, args=[app], daemon=True)
    daily_meme_thread.start()
    logger.print_log('Meme will be sent everyday at {}.'.format(DAILY_MEME_HOUR))
    app.run_polling()

if __name__ == '__main__':
    main("bg" in sys.argv)
