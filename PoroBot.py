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
import traceback

def tracebackEx(ex):
    if type(ex) == str:
        return "No valid traceback."
    ex_traceback = ex.__traceback__
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
        traceback.format_exception(ex.__class__, ex, ex_traceback)]
    return ''.join(tb_lines)


bot = InteractionBot(intents=disnake.Intents.default(), test_guilds = [533360564878180382])

@bot.event
async def on_ready() -> None:
    """
    The code in this even is executed when the bot is ready
    """
    logging.info("-------------------")
    logging.info(f"Logged in as {bot.user.name}")
    logging.info(f"disnake API version: {disnake.__version__}")
    logging.info(f"Python version: {platform.python_version()}")
    logging.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    logging.info(f"Owner : {bot.owner}")
    logging.info("-------------------")

def load_commands() -> None:
    for extension in os.listdir(f"./cogs"):
        try:
            bot.load_extension(f"cogs.{extension}.{extension}")
            logging.info(f"Loaded extension '{extension}'")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            logging.warning(f"Failed to load extension {extension}\n{exception}\n{tracebackEx(exception)}")



@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    """
    The code in this event is executed every time a valid slash command catches an error
    :param interaction: The slash command that failed executing.
    :param error: The error that has been faced.
    """
    tb = tracebackEx(error)
    await interaction.send(
        embed= new_embed(
            title=":x: __**ERROR**__: x:",
            description=f"Une erreur s'est produite lors de la commande **/{interaction.application_command.name}**\n{bot.owner.mention} a été prévenu et corrigera ce bug au plus vite !\nUtilise `/beer` pour un bière de consolation :beer:",
            thumbnail = "https://i.imgur.com/U7rBtRu.png"),
        delete_after=10)
    await bot.get_channel(int(bot.config['LOG_CHANNEL'])).send(
        embed= new_embed(
            title=f":x: __** ERROR**__ :x:",
            description=f"""```{error}```\nRaised on command **/{interaction.application_command.name}** from {interaction.channel.mention} by {interaction.author.mention}."""))
    n = (len(tb) // 4096) 
    for i in range(n):
        await bot.get_channel(int(bot.config['LOG_CHANNEL'])).send(
            embed=new_embed(
                description=f"```python\n{tb[4096*i:4096*(i+1)]}```"))
    await bot.get_channel(int(bot.config['LOG_CHANNEL'])).send(
        embed=new_embed(
            description=f"```python\n{tb[4096*n:]}```"))
    raise error


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed
    :param context: The context of the command that has been executed.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    logging.debug(f"Executed {executed_command} command in {context.guild.name} (ID: {context.message.guild.id}) by {context.message.author} (ID: {context.message.author.id})")


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error
    :param context: The normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = disnake.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = disnake.Embed(
            title="Error!",
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = disnake.Embed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error

if __name__ == "__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    
    config = dotenv_values(".env")
    bot.config = config
    bot.owner = disnake.AppInfo.owner

    load_commands()
    bot.run(config['DISCORD_TOKEN'])
