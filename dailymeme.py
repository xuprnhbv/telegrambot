from telegram.ext import Updater
from colorama import Fore
from consts import DAILY_MEME_HOUR, TEXT_COLOR, MEMES_PATH, CHAT_IDS_PATH, BOKER_TOV, MANAGEMENT_CHAT
from files import delete_meme
from chats import _get_chats
import logger
import schedule
import time
import os
import random
import json


def init_daily_meme(updater):
    """
    Initiates the daily meme schedule
    :param updater: the bot's updater object
    """
    schedule.every().day.at(DAILY_MEME_HOUR).do(send_random_meme, updater=updater)

    while True:
        schedule.run_pending()
        time.sleep(1)


def send_random_meme(updater: Updater):
    """
    Chooses a random file from the videos folder and sends it to everyone who wants memes :)
    :param updater: the bot's updater object
    :return:
    """
    if len(os.listdir(MEMES_PATH)) == 0:
        logger.print_log('NO MEME TO SEND!!!!!')
        updater.bot.send_message(chat_id=MANAGEMENT_CHAT, text="NO MEME TO SEND! ADD A MEME AND USE /forcesend!!!!")
        return

    logger.print_log('{text}Choosing daily meme...'.format(text=TEXT_COLOR))
    meme = choose_random_meme()
    logger.print_log('{text}Chosen {green}{}{text}! Sending meme...'.format(meme, green=Fore.LIGHTGREEN_EX, text=TEXT_COLOR))
    meme_caption = BOKER_TOV + meme[16:-4]
    send_count = 0
    send_meme_to = get_chat_list()
    try:
        with open(os.path.join(MEMES_PATH, meme), 'rb') as meme_file:
            for cid in send_meme_to:
                updater.bot.send_video(chat_id=cid, caption=meme_caption, video=meme_file)
                logger.print_log('{text}Meme sent to {yellow}{}{text}!'.format(cid, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
                meme_file.seek(0)
                send_count += 1
        logger.print_log('{green}Finished sending daily meme!'.format(green=Fore.LIGHTGREEN_EX))
    except Exception as e:
        logger.print_log('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        updater.bot.send_message(chat_id=MANAGEMENT_CHAT, text='failed to send meme :(')

    try:
        if send_count > 0:
            delete_meme(meme)
            logger.print_log('{text}Deleted file {yellow}{}{text}'.format(meme, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
            if len(os.listdir(MEMES_PATH)) == 1:
                logger.print_log('1 meme left!')
                updater.bot.send_message(chat_id=MANAGEMENT_CHAT, text="One meme left! Make sure to add another one"
                                                                       " before tomorrow!")
    except Exception as e:
        logger.print_log('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX, text=TEXT_COLOR))


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

