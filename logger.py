import logging
import re
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
        logging.info(_escape_ansi(text))
    elif level == 'error':
        logging.error(_escape_ansi(text))
    elif level == 'critical':
        logging.critical(_escape_ansi(text))


def _escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)
