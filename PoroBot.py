""""
Discord bot written in python using disnake library.
Copyright (C) 2022 - Oscar Van Slijpe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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

from utils.FastEmbed import FastEmbed
from utils.tools import tracebackEx
from utils import data

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

config = dotenv_values(".env")

if bool(config.get("TEST")):    
    logging.info("Starting in test mod...")
    bot = InteractionBot(intents=disnake.Intents.default(), test_guilds = [533360564878180382])
else:
    logging.info('Starting in prod mod...')
    bot = InteractionBot(intents=disnake.Intents.default())
    
bot.config = config
bot.owner = disnake.AppInfo.owner

    
@bot.event
async def on_ready() -> None:
    """
    The code in this even is executed when the bot is ready
    """
    bot.log_channel = bot.get_channel(int(bot.config['LOG_CHANNEL']))
    logging.info("-"*50)
    logging.info("-"*50)
    logging.info(f"| Logged in as {bot.user.name}")
    logging.info(f"| disnake API version: {disnake.__version__}")
    logging.info(f"| Python version: {platform.python_version()}")
    logging.info(f"| Running on: {platform.system()} {platform.release()} ({os.name})")
    logging.info(f"| Owner : {bot.owner}")
    logging.info(f"| Ready !")
    
    await bot.change_presence(activity = disnake.Activity(name='"/" -> commandes', type=disnake.ActivityType.playing))
    
    logging.info("-"*50)
    logging.info("-"*50)

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
        embed= FastEmbed(
            title=":x: __**ERROR**__ :x:",
            description=f"Une erreur s'est produite lors de la commande **/{interaction.application_command.name}**\n{bot.owner.mention} a été prévenu et corrigera ce bug au plus vite !\nUtilise `/beer` pour un bière de consolation :beer:",
            thumbnail = data.images.poros.shock),
        delete_after=10)
    await bot.log_channel.send(
        embed = FastEmbed(
            title=f":x: __** ERROR**__ :x:",
            description=f"```{error}```",
            fields = [
                {
                    'name':f"Raised on command :",
                    'value':f"**/{interaction.application_command.name}** from {interaction.guild.name} #{interaction.channel.mention} by {interaction.author.mention}."
                }
            ]
        )
    )
    n = (len(tb) // 4090) 
    for i in range(n):
        await bot.log_channel.send(
            embed=FastEmbed(
                description=f"```python\n{tb[4096*i:4096*(i+1)]}```")
        )
    await bot.log_channel.send(
        embed=FastEmbed(
            description=f"```python\n{tb[4096*n:]}```")
    )
    logging.error(f"{error} raised on command /{interaction.application_command.name} from {interaction.guild.name} #{interaction.channel.name} by {interaction.author.name}.\n{tb}")

@bot.event
async def on_slash_command(interaction: disnake.ApplicationCommandInteraction) -> None:
    logging.info(f"Slash command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")
    
@bot.event
async def on_user_command(interaction: disnake.UserCommandInteraction) -> None:
    logging.info(f"User command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")

@bot.event
async def on_message_command(interaction: disnake.MessageCommandInteraction) -> None:
    logging.info(f"Message command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")


@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    
@bot.event
async def on_user_command_error(interaction: disnake.UserCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    
@bot.event
async def on_message_command_error(interaction: disnake.MessageCommandInteraction, error: Exception) -> None:
    await send_error_log(interaction, error)
    
@bot.event
async def on_slash_command_completion(interaction: disnake.ApplicationCommandInteraction) -> None:
    logging.info(f"Slash command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name} by '{interaction.author.name}' run with succes")
    
@bot.event
async def on_user_command_completion(interaction: disnake.UserCommandInteraction) -> None:
    logging.info(f"User command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' run with succes")

@bot.event
async def on_message_command_completion(interaction: disnake.MessageCommandInteraction) -> None:
    logging.info(f"Message command '{interaction.application_command.name}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' run with succes")
    
    
load_commands()
bot.run(config['DISCORD_TOKEN'])