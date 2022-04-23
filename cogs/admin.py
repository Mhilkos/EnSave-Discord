# -----------------------------------------------------------
# This is a discord bot by ArikSquad and you are viewing the source code of it.
#
# (C) 2022 MikArt
# Released under the CC BY-NC 4.0 (BY-NC 4.0)
#
# -----------------------------------------------------------
import asyncio
import json
import random
import string

import discord
import psutil as psutil
from better_profanity import profanity
from discord.ext import commands

from utils import database, buttons


def convert(time):
    pos = ["s", "m", "h", "d"]

    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]


def get_string():
    letters = ''.join((random.choice(string.ascii_letters) for i in range(6)))
    digits = ''.join((random.choice(string.digits) for i in range(2)))
    sample_list = list(letters + digits)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string


class Admin(commands.Cog, description="Gather information"):
    EMOJI = "📜"

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='admin', help="Admin commands for debugging", hidden=True,
                    brief='Debugging the features of the bot')
    async def admin(self, ctx):
        if ctx.invoked_subcommand is None:
            if ctx.author.id in database.get_owner_ids():
                await ctx.send('Wow, an admin user!')

    @admin.command(name="profanity-test", aliases=["p-t"], hidden=True,
                   help="Test the profanity filter used in some commands",
                   brief="Profanity filter tester")
    async def profanity_test(self, ctx, *, text):
        if ctx.author.id in database.get_owner_ids():
            embed = discord.Embed(title="Profanity Test",
                                  description="Results of the debug profanity-test",
                                  color=0x00ff00)

            embed.add_field(name="Original", value=text)
            embed.add_field(name="Censored", value=profanity.censor(text))
            await ctx.send(embed=embed)

    @admin.command(name="exec", help="Executing code using python eval", hidden=True,
                   brief="Try python code")
    async def exec(self, ctx, *, code):
        if ctx.author.id in database.get_owner_ids():
            try:
                exec(code)
            except Exception as e:
                await ctx.send(f"```py\n{e}```")

    @admin.command(name="shutdown", help="Logout from discord.", aliases=["logout"], hidden=True,
                   brief="Close connection to discord")
    async def shutdown(self, ctx):
        if ctx.author.id in database.get_owner_ids():
            view = buttons.YesNo()
            sure = discord.Embed(title="Are you sure?", description="This will logout "
                                                                    "from discord and exit the python program.",
                                 color=ctx.author.color)
            message = await ctx.send(embed=sure, view=view)
            await view.wait()
            if view.value is None:
                return
            elif view.value:
                await message.delete()
                await self.bot.close()

    @admin.command(name='cog-unload', help='Unload a cog.', hidden=True,
                   brief='Disable a cog.')
    async def unload_cog(self, ctx, cog):
        if ctx.author.id in database.get_owner_ids():
            try:
                await self.bot.unload_extension(f'cogs.{cog.lower()}')
                await ctx.send(f"Unloaded `{cog}`.")
                print(f"Unloaded extension {cog}")
            except commands.ExtensionNotLoaded:
                await ctx.send(f'The extension {profanity.censor(cog)} is not loaded or has not been found.')

    @admin.command(name='cog-load', help='Load a cog.', hidden=True,
                   brief='Enable a cog.')
    async def load_cog(self, ctx, cog):
        if ctx.author.id in database.get_owner_ids():
            try:
                await self.bot.load_extension(f'cogs.{cog.lower()}')
                await ctx.send(f'Loaded `{cog}`.')
                print(f'Loaded extension {cog}')
            except commands.ExtensionNotFound:
                await ctx.send(f'There is no extension called {profanity.censor(cog)}')
            except commands.ExtensionAlreadyLoaded:
                await ctx.send('The extension is already loaded.')

    @admin.command(name='cog-restart', aliases=['cog-reload'], help='Restart a cog', hidden=True,
                   brief='Reload a cog.')
    async def restart_cog(self, ctx, cog):
        if ctx.author.id in database.get_owner_ids():
            try:
                await self.bot.unload_extension(f'cogs.{cog.lower()}')
                await self.bot.load_extension(f'cogs.{cog.lower()}')
                await ctx.send(f"Reloaded `{cog}`.")
                print(f"Reloaded extension {cog}")
            except commands.ExtensionFailed:
                await ctx.send('The extension failed.')
            except commands.ExtensionNotLoaded:
                await ctx.send('The extension is not loaded or has not been found.')

    @admin.command(name="info", aliases=["information", "about"], help="Gather information about the bot.",
                   hidden=True, brief='See information about bot or a user')
    async def info(self, ctx, user: discord.User = None):
        if user is None and ctx.author.id in database.get_owner_ids():
            embed = discord.Embed(title="Information", color=ctx.author.color)
            embed.add_field(name="Authors", value=str(database.get_owners_discord())[1:-1], inline=False)
            embed.add_field(name="Author IDs", value=str(database.get_owner_ids())[1:-1], inline=False)
            embed.add_field(name="Library", value="discord")
            embed.add_field(name="Version", value=discord.__version__)
            embed.add_field(name="Guilds", value=len(self.bot.guilds))
            embed.add_field(name="Users", value=len(self.bot.users))
            embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.2f}ms")
            embed.add_field(name="Memory", value=str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB",
                            inline=False)
            embed.add_field(name="OS Last Boot", value=f"{psutil.boot_time()}")
            embed.add_field(name="CPU Percentage", value=f"{psutil.cpu_percent()}%")
            return await ctx.send(embed=embed)
        elif user is not None and not user.bot and ctx.author.id in database.get_owner_ids():
            with open("db/users.json", "r") as f:
                data = json.load(f)
                msg_count = data[str(ctx.author.id)]['messages']
            embed = discord.Embed(title="Information", color=user.color)
            embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="Username", value=user.name)
            embed.add_field(name="Discriminator", value=user.discriminator, inline=False)
            embed.add_field(name="ID", value=user.id, inline=False)
            embed.add_field(name="Created at", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
            embed.add_field(name="Messages sent", value=msg_count if msg_count is not None else "No messages sent yet",
                            inline=False)
            embed.add_field(name="Premium", value="Yes" if database.get_premium(user.id) is True else "No",
                            inline=False)
            embed.add_field(name="Bot Status", value="Yes" if user.bot is True else "No", inline=False)
            embed.add_field(name="Bot Owner", value="Yes" if user.id in database.get_owner_ids() else "No",
                            inline=False)
            await ctx.send(embed=embed)

    @admin.command(name='set-premium', help='Set premium state of a user.', hidden=True,
                   brief='Change user premium state')
    async def set_premium(self, ctx, user: discord.Member, state: bool = None):
        if ctx.author.id in database.get_owner_ids():
            if user.id in database.get_owner_ids():
                await ctx.send("You can't set the premium state of an owner.")
            else:
                if state:
                    database.set_premium(user.id, state)
                else:
                    database.set_premium(user.id)
                await ctx.send(f"{user.mention}'s new state of premium: {state}")

    @admin.command(name='get-premium', help='Get premium state of a user.', hidden=True,
                   brief='Get user premium state')
    async def get_premium(self, ctx, user: discord.Member):
        if ctx.author.id in database.get_owner_ids():
            await ctx.send(f"{user.mention}'s premium state: {database.get_premium(user.id)}")

    @admin.command(name='keydrop', help='Drop a key.', hidden=True,
                   brief='Drop a key')
    async def keydrop(self, ctx, time: str = "1m", key: str = get_string()):
        if ctx.author.id in database.get_owner_ids():
            embed = discord.Embed(title="Key", color=discord.Color.blue())
            wait = convert(time)

            with open('db/codes.json', 'r') as f:
                data = json.load(f)

            number = 0
            for _ in data["codes"]:
                number = number + 1

            data["codes"][number] = key

            with open('db/codes.json', 'w') as f:
                json.dump(data, f, indent=4)

            embed.add_field(name="Key", value=f"Coming in {wait} seconds", inline=False)
            embed.add_field(name="How to redeem?", value=f"Use `{ctx.prefix}redeem <key>`", inline=False)
            embed.set_footer(text=f"Created by {ctx.author.name}")
            message = await ctx.send(embed=embed)
            await asyncio.sleep(wait)
            embed.set_field_at(0, name="Key", value=f"{key}")
            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
