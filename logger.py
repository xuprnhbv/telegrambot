import logging
import re
from consts import LOG_PATH

_should_print_to_console = False


def log_setup(print_console=True):
    """
    Set up the logger, must be called before using print_log

    :param print_console: whether to print to console
    :return:
    """
    _should_print_to_console = print_console
    logging.basicConfig(filename=LOG_PATH, encoding='utf-8', level=logging.INFO, format='<%(asctime)s> %(message)s', datefmt=
                        "%m/%d/%Y %I:%M:%S %p")


def print_no_log(text):
    """
    Will print if _should_print_to_console is True.

    :param text: text to print
    :return:
    """
    if _should_print_to_console:
        print(text)


def print_log(text, level='info'):
    """
    Prints to console and logs to log.

    :param text: text to log.
    :param level: logging leve.
    :return:
    """
    if _should_print_to_console:
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
