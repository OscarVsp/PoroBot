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

from dotenv import dotenv_values
import os
import platform
import logging
import logging.handlers

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot

import modules.FastSnake as FS

import traceback




class PoroBot(InteractionBot):
    
    
    
    def __init__(self, config, logger, logFormatter, test_mode = False):
        self.config = config
        self.logger = logger
        self.logFormatter = logFormatter
        self.test_mode = test_mode
        self.start_succed : bool = True
        intents = disnake.Intents.all()  # Allow the use of custom intents
        
        if test_mode:    
            logging.info("Starting in test mod...")
            super().__init__(intents=intents, test_guilds = [533360564878180382])
        else:
            logging.info('Starting in prod mod...')
            super().__init__(intents=intents)
            
        self.load_commands()
        
    def tracebackEx(self, ex):
        if type(ex) == str:
            return "No valid traceback."
        ex_traceback = ex.__traceback__
        if ex_traceback is None:
            ex_traceback = ex.__traceback__
        tb_lines = [ line.rstrip('\n') for line in
            traceback.format_exception(ex.__class__, ex, ex_traceback)]
        return ''.join(tb_lines)

    async def on_ready(self) -> None:
        """
        The code in this even is executed when the bot is ready
        """
        self.log_channel = self.get_channel(int(self.config['LOG_CHANNEL']))
        logging.info("-"*50)
        logging.info("-"*50)
        logging.info(f"| Logged in as {self.user.name}")
        logging.info(f"| disnake API version: {disnake.__version__}")
        logging.info(f"| Python version: {platform.python_version()}")
        logging.info(f"| Running on: {platform.system()} {platform.release()} ({os.name})")
        logging.info(f"| Owner : {self.owner}")
        logging.info(f"| Cogs loaded : "+", ".join([f'{cog}' for cog in self.cogs.keys()]))
        logging.info("| Started successfully !" if self.start_succed else "| Started with some issues...")
        logging.info(f"| Ready !")
        
        await self.change_presence(activity = disnake.Activity(name='"/" -> commandes', type=disnake.ActivityType.playing))
        
        logging.info("-"*50)
        logging.info("-"*50)

    def load_commands(self) -> None:
        for extension in os.listdir(f"./cogs"):
            try:
                self.load_extension(f"cogs.{extension}.{extension}")
                logging.info(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                logging.warning(f"Failed to load extension {extension}\n{exception}\n{self.tracebackEx(exception)}")
                self.start_succed = False

    async def send_error_log(self, interaction: ApplicationCommandInteraction, error: Exception):
        tb = self.tracebackEx(error)
        logging.error(f"{error} raised on command /{interaction.application_command.name} from {interaction.guild.name} #{interaction.channel.name} by {interaction.author.name}.\n{tb}")
        await interaction.send(
            content=self.owner.mention,
            embed= FS.Embed(
                title=":x: __**ERROR**__ :x:",
                description=f"Une erreur s'est produite lors de la commande **/{interaction.application_command.name}**\n{self.owner.mention} a été prévenu et corrigera ce bug au plus vite !\nUtilise `/beer` pour un bière de consolation :beer:",
                thumbnail = FS.Images.Poros.Shock,
                color=disnake.Colour.red()),
            delete_after=10)
        await self.log_channel.send(
            embed = FS.Embed(
                title=f":x: __** ERROR**__ :x:",
                description=f"```{error}```",
                fields = [
                    {
                        'name':f"Raised on command :",
                        'value':f"**/{interaction.application_command.name}:{interaction.id}** from {interaction.guild.name} #{interaction.channel.mention} by {interaction.author.mention} at {interaction.created_at} with options {interaction.filled_options}" + (f" and target '{interaction.target}'." if interaction.target else ".")
                    }
                ]
            )
        )
        n = (len(tb) // 4090) 
        for i in range(n):
            await self.log_channel.send(
                embed=FS.Embed(
                    description=f"```python\n{tb[4096*i:4096*(i+1)]}```")
            )
        await self.log_channel.send(
            embed=FS.Embed(
                description=f"```python\n{tb[4096*n:]}```")
        )
        
    async def on_slash_command(self, interaction: disnake.ApplicationCommandInteraction) -> None:
        logging.info(f"Slash command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")
        
    async def on_user_command(self, interaction: disnake.UserCommandInteraction) -> None:
        logging.info(f"User command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")

    async def on_message_command(self, interaction: disnake.MessageCommandInteraction) -> None:
        logging.info(f"Message command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' started...")

    async def on_slash_command_error(self, interaction: ApplicationCommandInteraction, error: Exception) -> None:
        await self.send_error_log(interaction, error)
        
    async def on_user_command_error(self, interaction: disnake.UserCommandInteraction, error: Exception) -> None:
        await self.send_error_log(interaction, error)
        
    async def on_message_command_error(self, interaction: disnake.MessageCommandInteraction, error: Exception) -> None:
        await self.send_error_log(interaction, error)
        
    async def on_slash_command_completion(self, interaction: disnake.ApplicationCommandInteraction) -> None:
        logging.info(f"Slash command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' at '{interaction.created_at}' runed with succes")
        
    async def on_user_command_completion(self, interaction: disnake.UserCommandInteraction) -> None:
        logging.info(f"User command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' at '{interaction.created_at}' runed with succes")

    async def on_message_command_completion(self, interaction: disnake.MessageCommandInteraction) -> None:
        logging.info(f"Message command '{interaction.application_command.name}:{interaction.id}' from '{interaction.guild.name} #{interaction.channel.name}' by '{interaction.author.name}' at '{interaction.created_at}' runed with succes")
  

    
  
if __name__ == "__main__":
    
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)

    if platform.system() == 'Linux':
        fileInfoHandler = logging.handlers.RotatingFileHandler(filename="logs/info.log",mode='w',encoding="UTF-8", delay = True, backupCount = 5)
        fileDebugHandler = logging.handlers.RotatingFileHandler(filename="logs/debug.log",mode='w',encoding="UTF-8", delay = True, backupCount = 5)
        fileInfoHandler.setFormatter(logFormatter)
        fileInfoHandler.setLevel(logging.INFO)
        fileInfoHandler.doRollover()
        rootLogger.addHandler(fileInfoHandler)
        fileDebugHandler.setFormatter(logFormatter)
        fileDebugHandler.setLevel(logging.DEBUG)
        fileDebugHandler.doRollover()
        rootLogger.addHandler(fileDebugHandler)
   

    else:
        logging.warning("Non Linux system. Log info and debug file won't be available.")    
    
    config = dotenv_values(".env")  


    if bool(config.get("TEST")): 
        poro = PoroBot(config, rootLogger, logFormatter, test_mode=True)
    else:
        poro = PoroBot(config, rootLogger, logFormatter, test_mode=False)
        
    poro.run(config['DISCORD_TOKEN'])