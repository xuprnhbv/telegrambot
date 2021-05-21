from telegram import File
from colorama import Fore
import time
import os

MEMES_PATH = r"../videos/"


def download_meme(file: File, name: str):
    """
    Download file from chat and save it, with the caption as the <current time>_<name>.mp4
    name should be only emojies. these are the ones that will come after the boker tov.
    :param name: caption to add after 'boker tov'. should be emojis :)
    :param file: the video to download
    :type file: telegram.File
    :return: the new file path
    """
    path = os.path.abspath(os.path.join(MEMES_PATH, time.strftime("%Y%m%d-%H%M%S") + '_' + name + '.mp4'))
    if os.path.lexists(path):
        path = path = os.path.abspath(os.path.join(MEMES_PATH, name + '.mp4'))
    file.download(path)
    return path
