""""
Copyright © Krypton 2022 - https://github.com/OscarVsp/PoroBot
Description:
This is a private multipurpose bot for discord.
Version: 3.0
"""

import json
from dotenv import dotenv_values
import os
import platform
import random
import sys
import logging
import asyncio

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import tasks, commands
from disnake.ext.commands import InteractionBot
from disnake.ext.commands import Context

from utils.embed import new_embed
from utils.tools import tracebackEx
from utils import data

config = dotenv_values(".env")

if bool(config.get("TEST")):    
    print("Starting in test mod...")
    bot = InteractionBot(intents=disnake.Intents.default(), test_guilds = [533360564878180382])
else:
    print('starting in prod mod...')
    bot = InteractionBot(intents=disnake.Intents.default())
@bot.event
async def on_ready() -> None:
    """
    The code in this even is executed when the bot is ready
    """
    bot.log_channel = bot.get_channel(int(bot.config['LOG_CHANNEL']))
    logging.info("-------------------")
    logging.info(f"Logged in as {bot.user.name}")
    logging.info(f"disnake API version: {disnake.__version__}")
    logging.info(f"Python version: {platform.python_version()}")
    logging.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    logging.info(f"Owner : {bot.owner}")
    
    await bot.change_presence(activity = disnake.Activity(name='"/" -> commandes', type=disnake.ActivityType.playing))
    
    logging.info("-------------------")

def load_commands() -> None:
    for extension in os.listdir(f"./cogs"):
        try:
            bot.load_extension(f"cogs.{extension}.{extension}")
            logging.info(f"Loaded extension '{extension}'")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            logging.warning(f"Failed to load extension {extension}\n{exception}\n{tracebackEx(exception)}")

async def send_error_log(interaction: ApplicationCommandInteraction, error: Exception):
    tb = tracebackEx(error)
    await interaction.send(
        embed= new_embed(
            title=":x: __**ERROR**__ :x:",
            description=f"Une erreur s'est produite lors de la commande **/{interaction.application_command.name}**\n{bot.owner.mention} a été prévenu et corrigera ce bug au plus vite !\nUtilise `/beer` pour un bière de consolation :beer:",
            thumbnail = data.images.poros.shock),
        delete_after=10)
    await bot.log_channel.send(
        embed = new_embed(
            title=f":x: __** ERROR**__ :x:",
            description=f"```{error}```",
            fields = [
                {
                    'name':f"Raised on command :",
                    'value':f"**/{interaction.application_command.name}** from {interaction.channel.mention} by {interaction.author.mention}."
                }
            ]
        )
    )
    n = (len(tb) // 4090) 
    for i in range(n):
        await bot.log_channel.send(
            embed=new_embed(
                description=f"```python\n{tb[4096*i:4096*(i+1)]}```")
        )
    await bot.log_channel.send(
        embed=new_embed(
            description=f"```python\n{tb[4096*n:]}```")
    )
    logging.error(f"{error} raised on command /{interaction.application_command.name} from {interaction.channel.mention} by {interaction.author.mention}.\n{tb}")



@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    
@bot.event
async def on_user_command_error(interaction: disnake.UserCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    
@bot.event
async def on_message_command_error(interaction: disnake.UserCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    

if __name__ == "__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    bot.config = config
    bot.owner = disnake.AppInfo.owner

    load_commands()
    bot.run(config['DISCORD_TOKEN'])
