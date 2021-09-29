from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from colorama import Fore
from files import download_meme, delete_meme, MEMES_PATH
from dailymeme import send_random_meme
from consts import TEXT_COLOR, MANAGEMENT_CHAT, DATE_REGEX
import logger
import emoji
import re
import os
import git

MANAGEMENT_CHAT = -1001413795548
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
        CommandHandler('rm', remove_meme, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('listmemes', listdir, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('forcesend', force_send_meme, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('version', get_version, filters=Filters.chat(MANAGEMENT_CHAT)),
        MessageHandler(Filters.regex('cs') & (~Filters.command), at_efi),
    ]

    failed_handlers = []
    for handler in handler_arr:
        logger.print_log('{text}Adding Handler {}...'.format(str(handler), text=Fore.LIGHTYELLOW_EX))
        try:
            dispatcher.add_handler(handler)
        except Exception as e:
            logger.print_log('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX))
            failed_handlers.append(handler)

    return failed_handlers


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
        logger.print_log('{text}Saved new meme: {yellow}{}{text}'.format(filename, text=TEXT_COLOR, yellow=Fore.LIGHTYELLOW_EX))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Saved successfully as {}'.format(filename))


def remove_meme(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Please specify date of file to remove.')
        return

    datestr = context.args[0]
    logger.print_log('{text}Removing meme...'.format(text=TEXT_COLOR))

    if not re.search(DATE_REGEX, datestr):
        logger.print_log('{red}Bad input {}. Does not match regex.{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Write date in format {} like specified when '
                                                               'uploaded initially.'.format(DATE_REGEX))
        return

    did_delete = False
    for filename in os.listdir(MEMES_PATH):
        if filename.startswith(datestr):
            try:
                delete_meme(filename)
                logger.print_log('{text}Deleted file {yellow}{}{text}'.format(filename, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Deleted {} successfully.'.format(filename))
                did_delete = True
                break
            except Exception as e:
                logger.print_log('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='{error}Exception raised: {}'.format(str(e),
                                                                                                            error=Fore.LIGHTRED_EX))
                break

    if not did_delete:
        logger.print_log('{text}No file starts with {red}{}{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='No such file {}'.format(datestr))


def listdir(update, context):
    logger.print_log('{text}Listing memes dir...'.format(text=TEXT_COLOR))
    memes = 'Memes directory:\n'
    for filename in os.listdir(MEMES_PATH):
        memes += '>' + filename + '\n'
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=memes)


def test(update, context):
    logger.print_log('Ran /test')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="hi, this chat is {}".format(update.effective_chat.id))


def emoji_test(update, context):
    logger.print_log('Ran /emojitest')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=emoji.emojize('cool thing :thumbsup:', use_aliases=True))


def hebrew(update, context):
    logger.print_log('Ran /hebrew')
    context.bot.send_message(chat_id=update.effective_chat.id, text='בוקר טוב :turtle:')


def resend_vid(update, context):
    logger.print_log('Ran resend_vid')
    context.bot.send_video(chat_id=update.effective_chat.id, caption='this was what you sent right? and the text w'
                                                                     'as {}'.format(update.message.caption),
                           video=update.message.effective_attachment)


def at_efi(update, context):
    logger.print_log('{text}@ing Efi...'.format(text=TEXT_COLOR))
    context.bot.send_message(chat_id=update.effective_chat.id, text='@efi')


def get_version(update, context):
    repo = git.repo(search_parent_directories=True)
    current_ver_date = repo.head.object.commited_datetime
    current_ver_sha = repo.head.object.hexsha
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Branch: {repo.active_branch.name}\nLast Commit Date: "
                                                              f"{current_ver_date}\nCommit SHA: {current_ver_sha}")
