from PIL import Image
from cogs.help import Help
from discord import File
from discord.ext import commands
from io import BytesIO
from lib.embeds import create_basic_embed, EMOJI_ERROR
from lib.prefixes import *
from lib.utils import log
from re import compile, split, IGNORECASE

FILENAME_BONK = 'assets/bonk.png'
FILENAME_MASK = 'assets/mask.png'
FILENAME_PUSHEEN = 'assets/pusheen.gif'
FILENAME_SUNDER = 'assets/sunder.png'
FILENAME_SPANK_1 = 'assets/spank1.png'
FILENAME_SPANK_2 = 'assets/spank2.png'
FILENAME_WATCH = 'assets/watch.jpg'

REGEX_HELP = compile(r'^\s*\!cb\s*h[ea]lp\s*$', IGNORECASE)
REGEX_SPANK_EMOJI = compile(r'^\s*(<:spank[a-z]*:740455662856831007>\s*)+$', IGNORECASE)

class EasterEggs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bonk(self, ctx):
        await EasterEggs.handle_bonk_command(ctx.message)

    @commands.command()
    async def sunderbonk(self, ctx):
        await EasterEggs.handle_bonk_command(ctx.message, sunder=True)

    @commands.command()
    async def spank(self, ctx):
        await EasterEggs.handle_spank_command(ctx.message)

    @commands.command()
    async def watch(self, ctx):
        await EasterEggs.handle_watch_command(ctx.message)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        elif REGEX_HELP.match(message.content):
            if get_prefix(self.bot, message) != DEFAULT_PREFIX:
                await Help.show_help(self.bot, message)
        elif REGEX_SPANK_EMOJI.match(message.content):
            await EasterEggs.handle_spank_command(message, bot=self.bot)

    @staticmethod
    async def handle_bonk_command(message, sunder=False):
        if len(message.mentions) != 1:
            embed = create_basic_embed('Please specify exactly one person to bonk.', EMOJI_ERROR)
            await message.channel.send(embed=embed)
            return

        async with message.channel.typing():
            bonk_image = Image.open(FILENAME_BONK)
            bonker_image = Image.open(FILENAME_SUNDER) if sunder else await EasterEggs.get_avatar_image(message.author)
            bonkee_image = await EasterEggs.get_avatar_image(message.mentions[0])

            if bonker_image:
                bonk_image = EasterEggs.process_image(
                    bonker_image, new_size=(75, 75), apply_mask=True, bg_image=bonk_image, position=(42, 30))

            if bonkee_image:
                bonk_image = EasterEggs.process_image(
                    bonkee_image, new_size=(100, 32), rotate_angle=28, apply_mask=True,
                    bg_image=bonk_image, position=(270, 94))

        with BytesIO() as image_bytes:
            bonk_image.save(image_bytes, 'png')
            image_bytes.seek(0)
            await message.channel.send(file=File(fp=image_bytes, filename='bonk.png'))

    @staticmethod
    async def handle_watch_command(message, bot=None):
        if len(message.mentions) != 1:
            embed = create_basic_embed('Please specify exactly one watcher.', EMOJI_ERROR)
            await message.channel.send(embed=embed)
            return

        async with message.channel.typing():
            bonk_image = Image.open(FILENAME_WATCH)
            watcher_image = await EasterEggs.get_avatar_image(message.mentions[0])

            if watcher_image:
                bonk_image = EasterEggs.process_image(
                    watcher_image, new_size=(120, 120), apply_mask=True, bg_image=bonk_image, position=(380, 415))

        with BytesIO() as image_bytes:
            bonk_image.save(image_bytes, 'png')
            image_bytes.seek(0)
            await message.channel.send(file=File(fp=image_bytes, filename='watch.png'))

    @staticmethod
    async def handle_spank_command(message, bot=None):
        if len(message.mentions) != 1 and not bot:
            embed = create_basic_embed('Please specify exactly one person to spank.', EMOJI_ERROR)
            await message.channel.send(embed=embed)
            return

        async with message.channel.typing():
            spank_image_1 = Image.open(FILENAME_SPANK_1)
            spank_image_2 = Image.open(FILENAME_SPANK_2)
            spanker_image = await EasterEggs.get_avatar_image(message.author if not bot else bot.user)
            spankee_image = await EasterEggs.get_avatar_image(message.mentions[0] if not bot else message.author)

            if spanker_image:
                spank_image_1 = EasterEggs.process_image(
                    spanker_image, new_size=(64, 64), apply_mask=True, bg_image=spank_image_1, position=(155, 75))
                spank_image_2 = EasterEggs.process_image(
                    spanker_image, new_size=(64, 64), apply_mask=True, bg_image=spank_image_2, position=(142, 75))

            if spankee_image:
                spank_image_1 = EasterEggs.process_image(
                    spankee_image, new_size=(50, 50), apply_mask=True, bg_image=spank_image_1, position=(146, 202))
                spank_image_2 = EasterEggs.process_image(
                    spankee_image, new_size=(50, 50), apply_mask=True, bg_image=spank_image_2, position=(141, 202))

        with BytesIO() as image_bytes:
            spank_image_1.save(image_bytes, 'gif', save_all=True, append_images=[spank_image_2], duration=180, loop=0)
            image_bytes.seek(0)
            await message.channel.send(file=File(fp=image_bytes, filename='spank.gif'))

    @staticmethod
    async def get_avatar_image(user):
        if user:
            asset = user.avatar_url_as(format='png', size=128)
            if asset:
                return Image.open(BytesIO(await asset.read()))
        return None

    @staticmethod
    def process_image(image, new_size=None, rotate_angle=0, apply_mask=False, bg_image=None, position=(0, 0)):
        if new_size:
            image = image.resize(new_size)

        if rotate_angle != 0:
            image = image.rotate(rotate_angle, expand=True)

        if apply_mask:
            mask_image = Image.open(FILENAME_MASK).convert('L')
            mask_image = EasterEggs.process_image(mask_image, new_size=new_size, rotate_angle=rotate_angle)
        else:
            mask_image = None

        if bg_image:
            new_bg_image = bg_image.copy()
            new_bg_image.paste(image, position, mask_image)
            return new_bg_image

        if mask_image:
            new_image = image.copy()
            new_image.putalpha(mask_image)
            return new_image

        return image


def setup(bot):
    bot.add_cog(EasterEggs(bot))
