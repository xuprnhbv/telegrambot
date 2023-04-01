from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import constants, InlineKeyboardButton, InlineKeyboardMarkup
from colorama import Fore
from .files import download_meme, delete_meme, MEMES_PATH
from .dailymeme import send_random_meme
from .chats import _get_chats
from .consts import TEXT_COLOR, MANAGEMENT_CHAT, DATE_REGEX, EFI_ID, CHAT_IDS_PATH, HELP_OP, MANAGEMENT_HELP_OP
import logger
import re
import os
import git
import time
import json

DATE_REGEX = r'^[0-9]{8}-[0-9]{6}$'


def add_all_handlers(updater: Updater):
    """
    Main function for adding all bot handlers to dispatcher.
    Takes the 'handlers_arr' and adds all handlers in it one by one.
    When making a new handler make sure to:
    - add it to handler_arr (in get_handler_arr)
    - add prints accordingly.
    :param updater: the bot's updater.
    :return: list of handlers that failed being added.
    """
    logger.print_log('{text}Setting up dispatcher...'.format(text=TEXT_COLOR))
    dispatcher = updater.dispatcher
    handler_arr = [
        MessageHandler(Filters.video & Filters.chat(MANAGEMENT_CHAT), save_meme),
        CommandHandler('help', help),
        CommandHandler('rm', remove_meme, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('listmemes', listdir, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('forcesend', force_send_meme, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('version', get_version, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('listchats', get_chat_ids, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('subscribe', subscribe_to_memes),
        CommandHandler('unsubscribe', unsubscribe_to_memes),
        CommandHandler('rmchat', kick_from_memes, filters=Filters.chat(MANAGEMENT_CHAT)),
        MessageHandler(Filters.regex(r'([cC][sS])+') & (~Filters.command), at_efi),
    ]

    handler_arr += get_inline_handlers()

    failed_handlers = []
    for handler in handler_arr:
        logger.print_log('{text}Adding Handler {}...'.format(str(handler), text=Fore.LIGHTYELLOW_EX))
        try:
            dispatcher.add_handler(handler)
        except Exception as e:
            logger.print_log('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX))
            failed_handlers.append(handler)

    return failed_handlers


def help(update, context):
    msg = HELP_OP
    if update.effective_chat.id == MANAGEMENT_CHAT:
        msg += f'\n{MANAGEMENT_HELP_OP}'
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def force_send_meme(update, context):
    logger.print_log('{text}Force sending meme...'.format(text=TEXT_COLOR))
    send_random_meme(context)


def save_meme(update, context):
    logger.print_log('{text}Saving meme...'.format(text=TEXT_COLOR))
    file = update.message.effective_attachment.get_file()
    name = update.message.caption
    filename = ''
    try:
        filename = download_meme(file, name)
    except Exception as e:
        logger.print_log('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))

    if filename:
        logger.print_log(
            '{text}Saved new meme: {yellow}{}{text}'.format(filename, text=TEXT_COLOR, yellow=Fore.LIGHTYELLOW_EX))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Saved successfully as {}'.format(filename))


def remove_meme(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Please specify date of file to remove.')
        return

    datestr = context.args[0]
    logger.print_log('{text}Removing meme...'.format(text=TEXT_COLOR))

    if not re.search(DATE_REGEX, datestr):
        logger.print_log(
            '{red}Bad input {}. Does not match regex.{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Write date in format {} like specified when '
                                                               'uploaded initially.'.format(DATE_REGEX))
        return

    did_delete = False
    for filename in os.listdir(MEMES_PATH):
        if filename.startswith(datestr):
            try:
                delete_meme(filename)
                logger.print_log(
                    '{text}Deleted file {yellow}{}{text}'.format(filename, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Deleted {} successfully.'.format(filename))
                did_delete = True
                break
            except Exception as e:
                logger.print_log('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='{error}Exception raised: {}'.format(str(e),
                                                                                                            error=Fore.LIGHTRED_EX))
                break

    if not did_delete:
        logger.print_log(
            '{text}No file starts with {red}{}{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='No such file {}'.format(datestr))


def listdir(update, context):
    logger.print_log('{text}Listing memes dir...'.format(text=TEXT_COLOR))
    meme_dir = os.listdir(MEMES_PATH)
    memes = f'Memes directory: {len(meme_dir)}\n'
    for filename in meme_dir:
        memes += '>' + filename + '\n'
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=memes)


def resend_vid(update, context):
    logger.print_log('Ran resend_vid')
    context.bot.send_video(chat_id=update.effective_chat.id, caption='this was what you sent right? and the text w'
                                                                     'as {}'.format(update.message.caption),
                           video=update.message.effective_attachment)


def at_efi(update, context):
    logger.print_log('{text}@ing Efi...'.format(text=TEXT_COLOR))
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'[@Ofir](tg://user?id={EFI_ID})',
                             parse_mode="Markdown")


def get_version(update, context):
    repo = git.Repo(search_parent_directories=True)
    current_ver_date = time.ctime(repo.head.commit.committed_date)
    current_ver_sha = repo.head.commit.hexsha
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Branch: {repo.active_branch.name}\nLast Commit Date: "
                                  f"{current_ver_date}\nCommit SHA: {current_ver_sha}")


def get_chat_ids(update, context):
    chats = _get_chats()
    msg = "Chats that receive daily memes:\n"
    for cid in chats:
        msg += f">> {cid} ({chats[cid]})\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def subscribe_to_memes(update, context):
    chats = _get_chats()
    if str(update.effective_chat.id) in chats.keys():
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're already subscribed!")
        return

    name = update.effective_chat.username if update.effective_chat.type == "private" \
        else update.effective_chat.title

    chats.update({update.effective_chat.id: name})
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=f"!!Added {update.effective_chat.type} to daily memes: "
                                                           f"{name}"
                                                           f" ({update.effective_chat.id})!!")
    context.bot.send_message(chat_id=update.effective_chat.id, text="You've subscribed successfully!")


def unsubscribe_to_memes(update, context):
    chats = _get_chats()
    if str(update.effective_chat.id) not in chats.keys():
        context.bot.send_message(chat_id=update.effective_chat.id, text='You are not subscribed!')
        return
    chats.pop(str(update.effective_chat.id))
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    name = update.effective_chat.username if update.effective_chat.type == "private" \
        else update.effective_chat.title
    context.bot.send_message(chat_id=update.effective_chat.id, text="Unsubscribed successfully")
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=f"!!Removed {name} from "
                                                           f"daily meme chats")


def kick_from_memes(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Use it as /rmchat <chat id>")
        return
    chats = _get_chats()
    rmchat_id = context.args[0]
    if rmchat_id not in chats.keys():
        context.bot.send_message(chat_id=update.effective_chat.id, text='Not a valid subbed chat.')
        return
    chats.pop(rmchat_id)
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Successfully removed {rmchat_id}"
                                                                    f" from daily meme chats.")


################### MENUS #############################

#### Handler Initiation ####
def get_inline_handlers():
    return {
        CommandHandler('start', main_inline_menu),
        CallbackQueryHandler(main_inline_menu, pattern='main_menu'),
        CallbackQueryHandler(files_inline_menu, pattern='files_menu')
    }


#### Bot ####
def main_inline_menu(update, context):
    #  type: (telegram.Update, telegram.ext.Dispatcher) -> None
    update.message.reply_text('Choose an option to begin.', reply_markup=main_keyboard())


def files_inline_menu(update, context):
    #  type: (telegram.Update, telegram.ext.Dispatcher) -> None
    update.callback_query.message.edit_text('Choose a file to begin.', reply_markup=files_keyboard())


def inline_menu_file_context(update, context):
    update.callback_query.message.edit_text(f'Chose {update.callback_query.data}. Choose an action or go back.')


#### Keyboards ####
def main_keyboard(calling_chat):
    #  type: (telegram.Chat) -> list[InlineKeyboardButton]
    """
    Opens up the main keyboard
    :param is_admin: True if in admin chat, for additional options.
    :return: inline keyboard
    """
    keyboard = [
        _get_proper_sub_button(calling_chat),
    ]  # General keyboard for all users
    if calling_chat.id == MANAGEMENT_CHAT:
        keyboard += [
            InlineKeyboardButton(text="Memes", callback_data='files_menu'),
            InlineKeyboardButton(text="Chats", callback_data='chats_menu'),
            InlineKeyboardButton(text="Version", callback_data='version'),
            InlineKeyboardButton(text="Force Send", callback_data="force_send")
        ]  # Admin keyboard
    keyboard.append(InlineKeyboardButton("Close", callback_data='close'))
    return keyboard


def _get_proper_sub_button(calling_chat):
    #  type: (telegram.Chat) -> InlineKeyboardButton
    return InlineKeyboardButton('Unsubscribe', callback_data='unsubscribe') if calling_chat.id in _get_chats().keys() \
        else InlineKeyboardButton("Subscribe", callback_data='subscribe')


def files_keyboard():
    keyboard = []
    meme_dir = os.listdir(MEMES_PATH)
    for meme in meme_dir:
        keyboard.append(InlineKeyboardButton(text=meme, callback_data=meme))
    keyboard.append(InlineKeyboardButton(text="Go Back", callback_data='main_menu'))
    return keyboard


def file_actions_keyboard(filename):
    return [
        InlineKeyboardButton(text='Send Next', callback_data=f'c;{filename}'),  # c -> Chosen meme for next send
        InlineKeyboardButton(text='Send Now', callback_data=f'fsn;{filename}'),  # fsn -> force send now.
        InlineKeyboardButton(text='Delete', callback_data=f'd;{filename}'),  # d -> delete this meme
        InlineKeyboardButton(text='Go back', callback_data='inline_main')  # go back to files menu
    ]

