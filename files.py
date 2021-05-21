from telegram import File


def download(file: File):
    """
    Download file from chat and save it, with the caption as the file name.
    in case of duplication will add DUP_ in beginning of name.
    :param file: the video to download
    :type file: telegram.File
    :return: whether download was successful.
    """
