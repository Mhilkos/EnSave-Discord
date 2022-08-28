# -----------------------------------------------------------
# This is a discord bot by ArikSquad and you are viewing the source code of it
#
# (C) 2021-2022 MikArt
# Released under the CC BY-NC 4.0 (BY-NC 4.0)
#
# -----------------------------------------------------------

# This first file is mostly documented but the others aren't.
# If you want to help me add comments then open a PR on GitHub

import asyncio
import os

import colorama
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from colorama import Fore
from discord.ext import commands, ipc
from dotenv import load_dotenv

from utils import utility, db

# Auto reset settings in colorama
colorama.init(autoreset=True)

# Load the bot token. You should create a file named .env and write the token.
# Example: TOKEN='(your token)'
load_dotenv()
token = os.getenv('TOKEN')


class Main(commands.Bot):
    def __init__(self):
        activity = discord.Activity(type=discord.ActivityType.watching, name=f'24/7')
        super().__init__(command_prefix=utility.get_prefix,
                         case_insensitive=True,
                         description="EnSave offers you moderation, fun and utility commands. "
                                     "We have frequent updates and fix bugs almost instantly. "
                                     "This includes everything you need from a discord bot.",
                         activity=activity,
                         status=discord.Status.idle,
                         intents=discord.Intents.all(),
                         help_command=None)
        self.ipc = ipc.Server(self, secret_key=os.getenv('SECRET_KEY'))
        self.ready = False
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

    def update_db(self):
        # Create tables
        db.execute('CREATE TABLE IF NOT EXISTS "code" ("secret"  TEXT UNIQUE)')
        db.execute('CREATE TABLE IF NOT EXISTS "guild" ( "guildID"  INTEGER UNIQUE, '
                   '"prefix"	TEXT DEFAULT \'.\', '
                   '"spy"	INTEGER DEFAULT 0, "channel"	INTEGER )')
        db.execute('CREATE TABLE IF NOT EXISTS "user" ("userID"	INTEGER UNIQUE, "premium"	INTEGER DEFAULT 0)')

        db.multiexec("INSERT OR IGNORE INTO guild (guildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        users = []
        for guild in self.guilds:
            for member in guild.members:
                if member.id not in users:
                    users.append(member.id)

        db.multiexec("INSERT OR IGNORE INTO user (userID) VALUES (?)",
                     ((user,) for user in users))

        db.commit()

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.ready = True
            self.update_db()
        else:
            print("Reconnected to Discord")


# Create the bot
bot = Main()


# Load all the cogs, then print the cog names that have been loaded
# Also run the bot with token from .env file
async def main():
    await bot.ipc.start()

    for filename in os.listdir('./cogs'):
        # The files starting with '_' are not loaded
        if filename.endswith('.py') and not filename.startswith('_'):
            loader = filename[:-3]
            await bot.load_extension(f'cogs.{loader}')
            print(f'{Fore.LIGHTMAGENTA_EX}{loader.capitalize()} has been loaded')

    async with bot:
        await bot.start(token, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
