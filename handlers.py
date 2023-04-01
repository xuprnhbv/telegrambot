from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from telegram import constants, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Update
from colorama import Fore
from files import download_meme, delete_meme, MEMES_PATH
from dailymeme import chosen_meme, send_random_meme, choose_next_meme, get_chat_list
from chats import _get_chats
from consts import TEXT_COLOR, MANAGEMENT_CHAT, DATE_REGEX, EFI_ID, CHAT_IDS_PATH, HELP_OP, MANAGEMENT_HELP_OP, \
    INLINE_REGEX
import logger
import re
import os
import git
import time
import json


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

    name = update.effective_chat.username or update.effective_chat.title

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
    name = update.effective_chat.username or update.effective_chat.title
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
    return [
        CommandHandler('start', main_inline_menu),
        CallbackQueryHandler(main_inline_menu, pattern='main_menu'),
        CallbackQueryHandler(files_inline_menu, pattern='files_menu'),
        CallbackQueryHandler(chats_inline_menu, pattern='chats_menu'),
        CallbackQueryHandler(get_version_inline, pattern='version'),
        CallbackQueryHandler(force_send_meme, pattern='force_send'),
        CallbackQueryHandler(subscribe_inline, pattern='subscribe'),
        CallbackQueryHandler(unsubscribe_inline, pattern='unsubscribe'),
        CallbackQueryHandler(file_actions_inline_menu, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'f')),
        CallbackQueryHandler(force_send_now_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'fsn')),
        CallbackQueryHandler(force_send_now_yn_inline, pattern="^(fsn-){1}((yes)|(no)){1}"),
        #CallbackQueryHandler(None, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'd'))
    ]


#### Bot ####
def main_inline_menu(update, _):
    if update.callback_query.message:
        update.callback_query.message.edit_text('Choose an option to begin.',
                                                reply_markup=main_keyboard(update.effective_chat))
    else:
        update.message.reply_text('Choose an option to begin.', reply_markup=main_keyboard(update.effective_chat))


def files_inline_menu(update, context):
    update.callback_query.message.edit_text('Choose a file to continue', reply_markup=files_keyboard())


def file_actions_inline_menu(update, _):
    file_chosen = update.callback_query.data.split(';')[1]
    update.callback_query.message.edit_text(f'Chose {file_chosen}. Choose an action or go back.',
                                            reply_markup=file_actions_keyboard(file_chosen))


def close_inline_menu(update, _):
    update.callback_query.message.edit_text('Goodbye!', reply_markup=None)


def chats_inline_menu(update, _):
    update.callback_query.message.edit_text('Choose a chat to continue', reply_markup=chats_keyboard())


def subscribe_inline(update, context):
    # Since we use inline, we can skip checking whether the user is subbed or not.
    chats = _get_chats()
    if str(update.effective_chat.id) in chats.keys():
        update.callback_query.message.edit_text('You are subscribed already, somehow? Please contact Ido',
                                                reply_markup=main_keyboard(update.effective_chat))
        logger.print_log(f'Chat {update.effective_chat.id} somehow managed to subscribe_inline while being subscribed.'
                         f'Callback data: "{update.callback_query.callback_data}"')
        return

    name = update.effective_chat.username or update.effective_chat.title

    chats.update({update.effective_chat.id: name})
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    # currently, this option is only accessible from the main menu, therefore we return to it. We recall the function
    # to change the button received from _get_proper_sub_button.
    update.callback_query.message.edit_text('Successfully subscribed', reply_markup=main_keyboard(update.effective_chat))
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=f"!!Added {update.effective_chat.type} to daily memes: "
                                                           f"{name} ({update.effective_chat.id})!!")


def unsubscribe_inline(update, context):
    chats = _get_chats()
    if str(update.effective_chat.id) not in chats.keys():
        update.callback_query.message.edit_text('You are not subscribed, somehow? Please contact Ido')
        return
    chats.pop(str(update.effective_chat.id))
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    name = update.effective_chat.username or update.effective_chat.title
    # currently, this option is only accessible from the main menu, therefore we return to it. We recall the function
    # to change the button received from _get_proper_sub_button.
    update.callback_query.message.edit_text("Unsubscribed successfully", reply_markup=main_keyboard(update.effective_chat))
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=f"!!Removed {name} from daily meme chats!!")


def force_send_now_inline(update, _):
    meme_to_send = update.callback_query.callback_data.split(';')[1]
    if meme_to_send not in os.listdir(MEMES_PATH):
        update.callback_query.message.edit_text(f"File {meme_to_send} does not exist!", reply_markup=files_keyboard())
        return
    # yeah im lazy im doing this menu here. fuck you too!
    update.callback_query.message.edit_text(f"You sure you want to force send {meme_to_send} right now?",
                                            reply_markup=InlineKeyboardMarkup([[
                                                InlineKeyboardButton('Yes', callback_data=f'fsn-yes-{meme_to_send}'),
                                                InlineKeyboardButton('No', callback_data=f'fsn-no-{meme_to_send}')
                                            ]]))


def force_send_now_yn_inline(update, context):
    answer, meme_to_send = update.callback_query.callback_data.split('-')[1:3]
    if answer == 'yes':
        choose_next_meme(meme_to_send)
        send_random_meme(context)
        # we return to files menu because the current file is deleted!
        update.callback_query.message.edit_text(f'Sent meme {meme_to_send}. Returned to files menu'
                                                , reply_markup=files_keyboard())
    else:
        update.callback_query.message.edit_text('Did not send meme.', reply_markup=file_actions_keyboard(meme_to_send))


def choose_next_meme_inline(update, _):
    meme_to_send = update.callback_query.callback_data.split(';')[1]
    choose_next_meme(meme_to_send)
    update.callback_query.message.edit_text(f"Next meme to be sent is {meme_to_send}",
                                            reply_markup=file_actions_keyboard(meme_to_send))


def get_version_inline(update, _):
    repo = git.Repo(search_parent_directories=True)
    current_ver_date = time.ctime(repo.head.commit.committed_date)
    current_ver_sha = repo.head.commit.hexsha
    update.callback_query.message.edit_text(f"Branch: {repo.active_branch.name}\nLast Commit Date: "
                                  f"{current_ver_date}\nCommit SHA: {current_ver_sha}",
                                            reply_markup=main_keyboard(update.effective_chat))


#### Keyboards ####
def main_keyboard(calling_chat):
    """
    Opens up the main keyboard
    :param calling_chat: the chat that this was called from. used to determine whether to show 'subscribe' or
    'unsubscribe'
    :return: inline keyboard
    """
    keyboard = [
        [_get_proper_sub_button(calling_chat)]
    ]  # General keyboard for all users
    if calling_chat.id == MANAGEMENT_CHAT:
        keyboard += [
            [InlineKeyboardButton(text="Memes", callback_data='files_menu'),
             InlineKeyboardButton(text="Chats", callback_data='chats_menu')],
            [InlineKeyboardButton(text="Version", callback_data='version'),
             InlineKeyboardButton(text="Force Send", callback_data="force_send")]
        ]  # Admin keyboard
    keyboard.append([InlineKeyboardButton("Close", callback_data='close')])
    return InlineKeyboardMarkup(keyboard)


def _get_proper_sub_button(calling_chat):
    return InlineKeyboardButton('Unsubscribe', callback_data='unsubscribe') if calling_chat.id in get_chat_list() \
        else InlineKeyboardButton("Subscribe", callback_data='subscribe')


def files_keyboard():
    keyboard = []
    meme_dir = os.listdir(MEMES_PATH)
    for file_row in [meme_dir[i:i+2] for i in range(0, len(meme_dir), 2)]:
        button_row = []
        for file in file_row:
            button_row.append(InlineKeyboardButton(text=file, callback_data=f'f;{file}'))
        keyboard.append(button_row)
    keyboard.append([InlineKeyboardButton(text="Go Back", callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)


def file_actions_keyboard(filename):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Send Next', callback_data=f'c;{filename}'),  # c -> Chosen meme for next send
         InlineKeyboardButton(text='Send Now', callback_data=f'fsn;{filename}')],  # fsn -> force send now.
        [InlineKeyboardButton(text='Delete', callback_data=f'd;{filename}'),  # d -> delete this meme
         InlineKeyboardButton(text='Go Back', callback_data='files_menu')]  # go back to files menu
    ])


def chats_keyboard():
    return InlineKeyboardMarkup([[]])
