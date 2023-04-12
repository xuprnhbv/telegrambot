from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from telegram import constants, InlineKeyboardButton, InlineKeyboardMarkup, Chat, Update
from colorama import Fore
from files import download_meme, delete_meme, MEMES_PATH
from dailymeme import send_random_meme, choose_next_meme, get_chat_list, is_next_meme_chosen, get_chosen_meme
from chats import _get_chats
from consts import TEXT_COLOR, MANAGEMENT_CHAT, DATE_REGEX, EFI_ID, CHAT_IDS_PATH, \
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


################### NON INLINE HANDLERS #############################

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


def at_efi(update, context):
    logger.print_log('{text}@ing Efi...'.format(text=TEXT_COLOR))
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'[@Ofir](tg://user?id={EFI_ID})',
                             parse_mode="Markdown")


################### INLINE #############################

#### Handler Initiation ####
def get_inline_handlers():
    return [
        CommandHandler('start', main_inline_menu),
        CallbackQueryHandler(main_inline_menu, pattern='main_menu'),
        CallbackQueryHandler(files_inline_menu, pattern='files_menu'),
        CallbackQueryHandler(chats_inline_menu, pattern='chats_menu'),
        CallbackQueryHandler(get_version_inline, pattern='version'),
        CallbackQueryHandler(force_send_now_inline, pattern='force_send'),
        CallbackQueryHandler(subscribe_inline, pattern='subscribe'),
        CallbackQueryHandler(unsubscribe_inline, pattern='unsubscribe'),
        CallbackQueryHandler(show_next_meme, pattern='show-next-meme'),
        CallbackQueryHandler(reset_next_meme, pattern='reset-next-meme'),
        CallbackQueryHandler(chat_actions_inline_menu, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'cht')),
        CallbackQueryHandler(choose_next_meme_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'c')),
        CallbackQueryHandler(file_actions_inline_menu, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'f')),
        CallbackQueryHandler(force_send_now_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'fsn')),
        CallbackQueryHandler(show_meme_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'shw')),
        CallbackQueryHandler(force_send_now_yn_inline, pattern="^(fsn@_@){1}((yes)|(no)){1}"),
        CallbackQueryHandler(delete_meme_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'd')),
        CallbackQueryHandler(kick_chat_inline, pattern=INLINE_REGEX.replace('COMMAND_CHAR', 'chtkick')),
        CallbackQueryHandler(close_inline_menu, pattern='close'),
    ]


#### Bot ####
def main_inline_menu(update, _):
    try:
        update.callback_query.message.edit_text(
            f'Choose an option to begin, {update.effective_user.first_name}.',
            reply_markup=main_keyboard(update.effective_chat))
    except AttributeError:
        update.message.reply_text(f'Choose an option to begin, {update.effective_user.first_name}.',
                                  reply_markup=main_keyboard(update.effective_chat))
        update.message.delete()  # worse case it'll fail.


def files_inline_menu(update, context):
    length = len(os.listdir(MEMES_PATH))
    update.callback_query.message.edit_text(f'Meme List ({length}). Choose a file to continue.'
                                            , reply_markup=files_keyboard())


def file_actions_inline_menu(update, _):
    file_chosen = update.callback_query.data.split(';')[1]
    update.callback_query.message.edit_text(f'Chose {file_chosen}. Choose an action or go back.',
                                            reply_markup=file_actions_keyboard(file_chosen))


def close_inline_menu(update, _):
    update.callback_query.message.delete()


def chats_inline_menu(update, _):
    update.callback_query.message.edit_text(f'Chat list', reply_markup=chats_keyboard())


def chat_actions_inline_menu(update, _):
    chat_chosen = update.callback_query.data.split(';')[1]
    chats = _get_chats()
    update.callback_query.message.edit_text(f'Choose an action for chat {chats[chat_chosen]}',
                                            reply_markup=chat_actions_keyboard(chat_chosen))


def subscribe_inline(update, context):
    # Since we use inline, we can skip checking whether the user is subbed or not.
    chats = _get_chats()
    if str(update.effective_chat.id) in chats.keys():
        update.callback_query.message.edit_text('You are subscribed already, somehow? Please contact Ido',
                                                reply_markup=main_keyboard(update.effective_chat))
        logger.print_log(f'Chat {update.effective_chat.id} somehow managed to subscribe_inline while being subscribed.'
                         f'Callback data: "{update.callback_query.data}"')
        return

    name = update.effective_chat.username or update.effective_chat.title

    chats.update({update.effective_chat.id: name})
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    # currently, this option is only accessible from the main menu, therefore we return to it. We recall the function
    # to change the button received from _get_proper_sub_button.
    update.callback_query.message.edit_text('Successfully subscribed',
                                            reply_markup=main_keyboard(update.effective_chat))
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
    update.callback_query.message.edit_text("Unsubscribed successfully",
                                            reply_markup=main_keyboard(update.effective_chat))
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=f"!!Removed {name} from daily meme chats!!")


def force_send_now_inline(update, _):
    if update.callback_query.data == 'force_send':
        meme_to_send = None  # its none so we randomize
    else:
        meme_to_send = update.callback_query.data.split(';')[1]
    if meme_to_send and meme_to_send not in os.listdir(MEMES_PATH):
        update.callback_query.message.edit_text(f"File {meme_to_send} does not exist!", reply_markup=files_keyboard())
        return
    # yeah im lazy im doing this menu here. fuck you too!
    message = f"You sure you want to force send {meme_to_send} right now?" if meme_to_send else "Force send right now?"
    update.callback_query.message.edit_text(message,
                                            reply_markup=InlineKeyboardMarkup([[
                                                InlineKeyboardButton('Yes',
                                                                     callback_data=f'fsn@_@yes@_@{meme_to_send}'),
                                                InlineKeyboardButton('No', callback_data=f'fsn@_@no@_@{meme_to_send}' if
                                                meme_to_send else "main_menu")
                                            ]]))


def force_send_now_yn_inline(update, context):
    answer, meme_to_send = update.callback_query.data.split('@_@')[1:3]
    if answer == 'yes':
        choose_next_meme(meme_to_send)
        send_random_meme(context)
        # we return to files menu because the current file is deleted!
        update.callback_query.message.edit_text(f'Sent meme {meme_to_send}. Returned to files menu'
                                                , reply_markup=files_keyboard())
    else:
        update.callback_query.message.edit_text('Did not send meme.', reply_markup=file_actions_keyboard(meme_to_send))


def choose_next_meme_inline(update, _):
    meme_to_send = update.callback_query.data.split(';')[1]
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


def force_send_meme(update, context):
    logger.print_log('{text}Force sending meme...'.format(text=TEXT_COLOR))
    send_random_meme(context)
    update.callback_query.message.edit_text('Force sent meme.')


def show_next_meme(update, _):
    next_meme = get_chosen_meme()
    update.callback_query.message.edit_text(f'Next meme is {next_meme}',
                                            reply_markup=main_keyboard(update.effective_chat))


def reset_next_meme(update, _):
    choose_next_meme(None)
    update.callback_query.message.edit_text('Reset next meme', reply_markup=main_keyboard(update.effective_chat))


def delete_meme_inline(update, _):
    meme_to_delete = update.callback_query.data.split(';')[1]
    if meme_to_delete not in os.listdir(MEMES_PATH):
        update.callback_query.message.edit_text(f'Meme {meme_to_delete} is not a file!',
                                                reply_markup=file_actions_keyboard(meme_to_delete))
        return
    try:
        os.remove(os.path.join(MEMES_PATH, meme_to_delete))
    finally:
        if meme_to_delete not in os.listdir(MEMES_PATH):
            update.callback_query.message.edit_text(f'Meme {meme_to_delete} was successfully deleted!',
                                                    reply_markup=files_keyboard())
        else:
            update.callback_query.message.edit_text('Failed to delete :(',
                                                    reply_markup=file_actions_keyboard(meme_to_delete))


def kick_chat_inline(update, _):
    rmchat_id = update.callback_query.data.split(';')[1]
    chats = _get_chats()
    if rmchat_id not in chats.keys():
        update.callback_query.message.edit_text('Not a valid subbed chat', reply_markup=chats_keyboard())
        return
    chats.pop(rmchat_id)
    with open(CHAT_IDS_PATH, 'w') as fd:
        json.dump(chats, fd)
    update.callback_query.message.edit_text(f'Removed chat {rmchat_id}', reply_markup=chats_keyboard())


def show_meme_inline(update, _):
    meme_to_show = update.callback_query.data.split(';')[1]
    meme_path = os.path.join(MEMES_PATH, meme_to_show)
    right_now = time.asctime()
    if not os.path.isfile(meme_path):
        update.callback_query.message.edit_text(f"No such file!", reply_markup=files_keyboard())
    else:
        with open(meme_path, 'rb') as f:
            update.callback_query.message.edit_text(f"Showing meme {meme_to_show} ({right_now})",
                                                    reply_markup=file_actions_keyboard(meme_to_show))
            update.callback_query.message.reply_video(video=f, reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text='Close', callback_data='close')]
            ]))


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
        keyboard.append(_get_chosen_meme_buttons())
    keyboard.append([InlineKeyboardButton("Close", callback_data='close')])
    return InlineKeyboardMarkup(keyboard)


def _get_proper_sub_button(calling_chat):
    return InlineKeyboardButton('Unsubscribe', callback_data='unsubscribe') if calling_chat.id in get_chat_list() \
        else InlineKeyboardButton("Subscribe", callback_data='subscribe')


def _get_chosen_meme_buttons():
    """
    returns buttons depending on whether or not next meme is chosen
    :return: List of buttons to concat to admin buttons as 1 row
    """
    if is_next_meme_chosen():
        return [
            InlineKeyboardButton('Show Next', callback_data='show-next-meme'),
            InlineKeyboardButton("Reset Next", callback_data='reset-next-meme'),
        ]
    else:
        return []


def files_keyboard():
    keyboard = []
    meme_dir = sorted(os.listdir(MEMES_PATH))
    row_length = 1
    for file_row in [meme_dir[i:i + row_length] for i in range(0, len(meme_dir), row_length)]:
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
         InlineKeyboardButton(text='Show', callback_data=f'shw;{filename}')],  # shw -> show meme
        [InlineKeyboardButton(text='Go Back', callback_data='files_menu')]  # go back to files menu
    ])


def chats_keyboard():
    keyboard = []
    with open(CHAT_IDS_PATH, 'r') as chat_file:
        chats = json.load(chat_file)
    row_length = 2
    for chat_row in [list(chats.keys())[i:i + row_length] for i in range(0, len(chats.keys()), row_length)]:
        row = []
        for chat in chat_row:
            row.append(InlineKeyboardButton(text=f"{chats[chat]} ({chat})", callback_data=f'cht;{chat}'))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text='Go back', callback_data='main_menu')])
    return InlineKeyboardMarkup(keyboard)


def chat_actions_keyboard(chat):
    keyboard = [
        [
            InlineKeyboardButton(text='Kick', callback_data=f'chtkick;{chat}')
        ],
        [
            InlineKeyboardButton(text='Go Back', callback_data='chats_menu')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
