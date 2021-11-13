from consts import CHAT_IDS_PATH
import logger
import json


def _get_chats():
    try:
        with open(CHAT_IDS_PATH, 'r') as fd:
            return json.load(fd)
    except FileNotFoundError:
        logger.print_log(f"No chat_ids.json file in {CHAT_IDS_PATH}")
    except Exception as e:
        raise e