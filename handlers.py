from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from colorama import Fore
from files import download_meme, delete_meme, MEMES_PATH
from consts import TEXT_COLOR
import emoji
import re
import os

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
    print('{text}Setting up dispatcher...'.format(text=TEXT_COLOR))
    dispatcher = updater.dispatcher
    handler_arr = [
        MessageHandler(Filters.video & Filters.chat(MANAGEMENT_CHAT), save_meme),
        CommandHandler('rm', remove_meme, filters=Filters.chat(MANAGEMENT_CHAT)),
        CommandHandler('listmemes', listdir, filters=Filters.chat(MANAGEMENT_CHAT)),
        MessageHandler(Filters.regex('cs') & (~Filters.command), at_efi),
    ]

    failed_handlers = []
    for handler in handler_arr:
        print('{text}Adding Handler {}...'.format(str(handler), text=Fore.LIGHTYELLOW_EX))
        try:
            dispatcher.add_handler(handler)
        except Exception as e:
            print('{error}Exception raised: {}{text}'.format(str(e), error=Fore.LIGHTRED_EX))
            failed_handlers.append(handler)

    return failed_handlers


def save_meme(update, context):
    print('{text}Saving meme...'.format(text=TEXT_COLOR))
    file = update.message.effective_attachment.get_file()
    name = update.message.caption
    filename = ''
    try:
        filename = download_meme(file, name)
    except Exception as e:
        print('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))

    if filename:
        print('{text}Saved new meme: {yellow}{}{text}'.format(filename, text=TEXT_COLOR, yellow=Fore.LIGHTYELLOW_EX))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Saved successfully as {}'.format(filename))


def remove_meme(update, context):
    if len(context.args) != 1:
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Please specify date of file to remove.')
        return

    datestr = context.args[0]
    print('{text}Removing meme...'.format(text=TEXT_COLOR))

    if not re.search(DATE_REGEX, datestr):
        print('{red}Bad input {}. Does not match regex.{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Write date in format {} like specified when '
                                                               'uploaded initially.'.format(DATE_REGEX))
        return

    did_delete = False
    for filename in os.listdir(MEMES_PATH):
        if filename.startswith(datestr):
            try:
                delete_meme(filename)
                print('{text}Deleted file {yellow}{}{text}'.format(filename, yellow=Fore.LIGHTYELLOW_EX, text=TEXT_COLOR))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='Deleted {} successfully.'.format(filename))
                did_delete = True
                break
            except Exception as e:
                print('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))
                context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='{error}Exception raised: {}'.format(str(e),
                                                                                                            error=Fore.LIGHTRED_EX))
                break

    if not did_delete:
        print('{text}No file starts with {red}{}{text}'.format(datestr, red=Fore.LIGHTRED_EX, text=TEXT_COLOR))
        context.bot.send_message(chat_id=MANAGEMENT_CHAT, text='No such file {}'.format(datestr))


def listdir(update, context):
    print('{text}Listing memes dir...'.format(text=TEXT_COLOR))
    memes = 'Memes directory:\n'
    for filename in os.listdir(MEMES_PATH):
        memes += '>' + filename + '\n'
    context.bot.send_message(chat_id=MANAGEMENT_CHAT, text=memes)


def test(update, context):
    print('Ran /test')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="hi, this chat is {}".format(update.effective_chat.id))


def emoji_test(update, context):
    print('Ran /emojitest')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=emoji.emojize('cool thing :thumbsup:', use_aliases=True))


def hebrew(update, context):
    print('Ran /hebrew')
    context.bot.send_message(chat_id=update.effective_chat.id, text='בוקר טוב :turtle:')


def resend_vid(update, context):
    print('Ran resend_vid')
    context.bot.send_video(chat_id=update.effective_chat.id, caption='this was what you sent right? and the text w'
                                                                     'as {}'.format(update.message.caption),
                           video=update.message.effective_attachment)


def at_efi(update, context):
    print('{text}@ing Efi...'.format(text=TEXT_COLOR))
    context.bot.send_message(chat_id=update.effective_chat.id, text='@efi')
