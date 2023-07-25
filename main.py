import asyncio
import discord
from discord.ext import commands
from os import listdir,environ
from dbloader import load_config
from cogs.homucogs import HomuCog
config_loc = environ.get("HOMU_CONFIG_PATH","./config/config.json")
bot_config = load_config(config_loc)
INTENTS = discord.Intents.all()





EXTENSIONS = ["cogs."+ x[:-3] for x in listdir('./cogs') if x.endswith('.py')]

bot = commands.Bot(
    intents=INTENTS,
    command_prefix=bot_config["command_prefix"]
)

@bot.event
async def setup_hook() -> None:
    for extension in EXTENSIONS:
        await bot.load_extension(extension)

bot.run(bot_config["keys"]["discord"])
