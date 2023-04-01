from telegram import File
from .consts import MEMES_PATH
import time
import os


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
        path = os.path.abspath(os.path.join(MEMES_PATH, name + '.mp4'))
    file.download(path)
    return path


def delete_meme(filename):
    """
    Deletes meme from meme folder.
    :param filename: name of file.
    """
    os.remove(os.path.join(MEMES_PATH, filename))
