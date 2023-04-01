from colorama import Fore

TEXT_COLOR = Fore.LIGHTWHITE_EX
DAILY_MEME_HOUR = '06:30'
MEMES_PATH = r"../videos/"
RELATIVE_TOKEN_PATH = r'../token.key'
BOKER_TOV = 'בוקר טוב '
MANAGEMENT_CHAT = -1001413795548
CHAT_IDS_PATH = r'./../chat_ids.json'
DATE_REGEX = r'^[0-9]{8}-[0-9]{6}$'
INLINE_REGEX = r'^({command_char}){1};[0-9]{8}-[0-9]{6}.+'
LOG_PATH = r'./../botlog'
EFI_ID = 905200111
HELP_OP = """Ido Moshe 2:
/subscribe
/unsubscribe
/help
"""
MANAGEMENT_HELP_OP = """Management:
/rm <meme date>
/listmemes
/listchats
/rmchat <chat id>
/forcesend
/version"""
