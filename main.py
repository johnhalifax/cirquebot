from discord import Game, Intents
from discord.ext import commands
from lib.prefixes import get_prefix, DEFAULT_PREFIX
from secrets import BOT_TOKEN_DEV, BOT_TOKEN_LITE, BOT_TOKEN_PROD
from sys import argv

BOT_STATUS = DEFAULT_PREFIX + 'help'

CONFIG_LITE = 'LITE'
CONFIG_PROD = 'PROD'
CONFIG_DEV = 'DEV'

intents = Intents.default()
intents.members = True
intents.guild_typing = True

bot = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents)

def initialize_bot(config):
    # Extensions that should be loaded for all bot configurations.
    bot.load_extension('cogs.help')
    bot.load_extension('cogs.prefix')
    bot.load_extension('cogs.reactions')

    if config == CONFIG_LITE:
        return BOT_TOKEN_LITE

    # Extensions that should only be loaded for PROD and DEV configurations.
    bot.load_extension('cogs.abs_game')
    bot.load_extension('cogs.audio_player')
    bot.load_extension('cogs.easter_eggs')
    bot.load_extension('cogs.rewrite')

    if config == CONFIG_PROD:
        return BOT_TOKEN_PROD

    return BOT_TOKEN_DEV

@bot.event
async def on_ready():
    print(f'Successfully logged in as: {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

if __name__ == '__main__':
    config_arg = '' if len(argv) != 2 else argv[1].upper()
    config_option = config_arg if config_arg in [CONFIG_LITE, CONFIG_PROD, CONFIG_DEV] else CONFIG_PROD
    bot_token = initialize_bot(config_option)
    print(f'[Configuration: {config_option}] Logging in...')
    bot.run(bot_token)
