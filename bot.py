import discord
from discord.ext import commands
from modules.helpers import *
from dotenv import load_dotenv

class MyBot(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir(COG_FOLDER):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

client = MyBot(
    command_prefix=PREFIX,
    owner_ids=OWNER_IDS,
    intents=discord.Intents.all()
)

client.remove_command('help')

client.run(TOKEN)