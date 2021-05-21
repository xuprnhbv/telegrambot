from telegram.ext import Updater
from colorama import Fore
from consts import DAILY_MEME_HOUR, TEXT_COLOR, MEMES_PATH, SEND_MEME_TO, BOKER_TOV
from files import delete_meme
import schedule
import time
import os
import random

def init_daily_meme(updater):
    """
    Initiates the daily meme schedule
    :param updater: the bot's updater object
    """
    #schedule.every().day.at(DAILY_MEME_HOUR).do(send_random_meme, updater=updater)
    time.sleep(1)
    send_random_meme(updater)

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
        print('{red}NO MEME TO SEND!!!!!')
        return

    print('{text}Choosing daily meme...'.format(text=TEXT_COLOR))
    meme = choose_random_meme()
    print('{text}Chosen {green}{}{text}! Sending meme...'.format(meme, green=Fore.LIGHTGREEN_EX, text=TEXT_COLOR))
    meme_caption = BOKER_TOV + meme[16:-4]
    try:
        print(os.path.join(MEMES_PATH, meme))
        with open(os.path.join(MEMES_PATH, meme), 'rb') as meme_file:
            print('i opened the file')
            print(SEND_MEME_TO)
            for cid in SEND_MEME_TO:
                print(cid)
                updater.bot.send_video(chat_id=cid, caption=meme_caption, video=meme_file)
                print('{text}Meme sent to {yellow}{}{text}!'.format(cid, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
        print('{green}Finished sending daily meme!'.format(green=Fore.LIGHTGREEN_EX))
        delete_meme(meme)
        print('{text}Deleted file {yellow}{}{text}'.format(meme, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
    except Exception as e:
        print('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX, text=TEXT_COLOR))


def choose_random_meme():
    """
    Chooses a random file from the memes folder.
    :return: the filename of the random file.
    """
    return random.choice(os.listdir(MEMES_PATH))
