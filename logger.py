import logging
from consts import LOG_PATH


def log_setup():
    logging.basicConfig(filename=LOG_PATH, encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s', datefmt=
                        "%m/%d/%Y %I:%M:%S %p")


def print_log(text, level='info'):
    """
    Prints to console and logs to log.

    :param text: text to log.
    :param level: logging leve.
    :return:
    """
    print(text)
    level = level.lower()
    if level == 'info':
        logging.info(_strip_unprintables(text))
    elif level == 'error':
        logging.error(_strip_unprintables(text))
    elif level == 'critical':
        logging.critical(_strip_unprintables(text))


def _strip_unprintables(text):
    return "".join(c for c in text if c.isprintable())
