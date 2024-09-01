from telegram.ext import Application
from consts import DAILY_MEME_HOUR, MEMES_PATH, BOKER_TOV, MANAGEMENT_CHAT
from files import delete_meme
from chats import _get_chats
import logger
import schedule
import time
import os
import random

chosen_meme = None


def init_daily_meme(app):
    """
    Initiates the daily meme schedule
    :param app: the bot's app object
    """
    schedule.every().day.at(DAILY_MEME_HOUR).do(send_random_meme, app=app)
    while True:
        schedule.run_pending()
        time.sleep(1)


async def send_random_meme(app):
    """
    Chooses a random file from the videos folder and sends it to everyone who wants memes :)
    :param app: the bot's app object
    :return:
    """
    global chosen_meme
    if len(os.listdir(MEMES_PATH)) == 0:
        logger.print_log('NO MEME TO SEND!!!!!')
        app.bot.send_message(chat_id=MANAGEMENT_CHAT, text="NO MEME TO SEND! ADD A MEME AND USE /forcesend!!!!")
        return

    if chosen_meme is not None:
        logger.print_log('Meme {meme_name} was chosen beforehand! skipping random meme...'.format(
            meme_name=chosen_meme))
        meme = chosen_meme
        chosen_meme = None
    else:
        logger.print_log('Choosing daily meme...')
        meme = choose_random_meme()
    logger.print_log('Chosen {}! Sending meme...'.format(meme))
    meme_caption = BOKER_TOV + meme[16:-4]
    send_count = 0
    send_meme_to = get_chat_list()
    try:
        with open(os.path.join(MEMES_PATH, meme), 'rb') as meme_file:
            for cid in send_meme_to:
                await app.bot.send_video(chat_id=cid, caption=meme_caption, video=meme_file)
                logger.print_log('Meme sent to {}!'.format(cid))
                meme_file.seek(0)
                send_count += 1
        logger.print_log('Finished sending daily meme!')
    except Exception as e:
        logger.print_log('Exception raised: {}'.format(str(e)))
        app.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Failed to send meme :(')

    try:
        if send_count > 0:
            delete_meme(meme)
            logger.print_log('Deleted file {}'.format(meme))
            if len(os.listdir(MEMES_PATH)) == 1:
                logger.print_log('1 meme left!')
                app.bot.send_message(chat_id=MANAGEMENT_CHAT, text="One meme left! Make sure to add another one"
                                                                       " before tomorrow!")
    except Exception as e:
        logger.print_log('Exception raised: {}'.format(str(e)))


def choose_random_meme():
    """
    Chooses a random file from the memes folder.
    :return: the filename of the random file.
    """
    return random.choice(os.listdir(MEMES_PATH))


def get_chat_list():
    """
    Reads from chat_ids.json and returns list of chats.

    :return: list of chat ids.
    """
    chat_dict = _get_chats()
    return [int(i) for i in list(chat_dict.keys())]


def choose_next_meme(filename):
    # type: (str) -> None
    global chosen_meme
    chosen_meme = filename


def is_next_meme_chosen():
    return bool(get_chosen_meme())


def get_chosen_meme():
    global chosen_meme
    return chosen_meme
