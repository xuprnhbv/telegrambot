from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from colorama import Fore
import emoji

TEXT_COLOR = Fore.LIGHTWHITE_EX


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
        CommandHandler('test', test),
        CommandHandler('emojitest', emoji_test),
        CommandHandler('hebrew', hebrew),
        MessageHandler(Filters.video, resend_vid)
    ]

    failed_handlers = []
    for handler in handler_arr:
        print('{text}Adding Handler {}...'.format(str(handler), text=Fore.LIGHTYELLOW_EX))
        try:
            dispatcher.add_handler(handler)
        except Exception as e:
            print('{error}Exception raised: {}'.format(str(e), error=Fore.LIGHTRED_EX))
            failed_handlers.append(handler)

    return failed_handlers


def test(update, context):
    print('Ran /test')
    context.bot.send_message(chat_id=update.effective_chat.id, text="hi, this chat is {}".format(update.effective_chat.id))


def emoji_test(update, context):
    print('Ran /emojitest')
    context.bot.send_message(chat_id=update.effective_chat.id, text=emoji.emojize('cool thing :thumbsup:', use_aliases=True))


def hebrew(update, context):
    print('Ran /hebrew')
    context.bot.send_message(chat_id=update.effective_chat.id, text='בוקר טוב :turtle:')


def resend_vid(update, context):
    print('Ran resend_vid')
    context.bot.send_video(chat_id=update.effective_chat.id, caption='this was what you sent right?', video=update.message.effective_attachment)
