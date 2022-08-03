from typing import List
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from .view import *
import asyncio
from asyncio.exceptions import TimeoutError

async def is_owner(ctx):
    return ctx.author.id == 281401408597655552


class Basic(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : commands.InteractionBot = bot

    @commands.slash_command(
        description = "Commander un bière (test le ping du bot)"
    )
    async def beer(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(
                title="Voilà tes bières",
                description=f":beer:\n Après {round(self.bot.latency,2)} secondes d'attente seulement !",
                color = disnake.Colour.gold()
            ),
            view = Beer(inter)
        )


    @commands.slash_command(
        description = "Nourrir le poro avec des porosnacks jusqu'à le faire exploser"
    )
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed = FS.Embed(
                description="Nourris le poro !",
                image=FS.Images.Poros.Growings[0],
                footer_text="0/10"
            ),
            view=PoroFeed(inter)
        )
        
    async def update_proc(self, inter : disnake.ApplicationCommandInteraction, branch : str, restart : bool):
        cmd_split = ("git","pull","origin",branch)
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_split, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                embed = FS.Embed(
                        title=f"✅ Update successed",
                        description=f"```{stdout.decode().strip()}```"
                    )
                await inter.edit_original_message(embed=embed)
                if restart:
                    await self.restart_proc(inter)
            else :
                await inter.edit_original_message(embed=FS.Embed(
                    title=f"❌ Update failed with status code {FS.Emotes.Num[process.returncode]}",
                    description=f"```{stderr.decode().strip()}```"
                ))
        except FileNotFoundError as e:
            await inter.edit_original_message(embed=FS.Embed(
                    title=f"❌ Update failed due to *FileNotFoundError*",
                    description=f"```Couldn't find file {cmd_split[0]}```"))
    
    async def restart_proc(self, inter : disnake.ApplicationCommandInteraction):
        cmd_split = ("pm2","restart","poro")
        embeds : List[disnake.Embed] = (await inter.original_message()).embeds
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_split, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            embeds.append(FS.Embed(
                title=f"⌛ Restarting..."
            ))
            await inter.edit_original_message(embeds=embeds)

            stdout, stderr = await process.communicate()
            
        except FileNotFoundError as e:
            embeds.append(FS.Embed(
                    title=f"❌ Restart failed due to *FileNotFoundError*",
                    description=f"Couldn't find file ***{cmd_split[0]}***"))
            await inter.edit_original_message(embeds=embeds)  
        
        
        
    @commands.slash_command(
        description="Update the bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def update(self, inter : disnake.ApplicationCommandInteraction,
                     branch : str = commands.Param(description="The branch to pull", choices=["master","test"], default="master"),
                     restart : bool = commands.Param(description="Restart the bot after update ?", default = True)):
        await inter.response.defer(ephemeral=True)
        if self.bot.test_mode:
            await inter.edit_original_message(embed=FS.Embed(
                description=f"Cannot update in test mode."
            ))
        else:
            await self.update_proc(inter,branch,restart)
            
                
                
    @commands.slash_command(
        description="Restart the bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def restart(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        if self.bot.test_mode:
            await inter.edit_original_message(embed=FS.Embed(
                description=f"Cannot restart in test mode."
            ))
        else:
            await self.restart_proc(inter)

            
    @commands.slash_command(
        description="Send a command to the Rpi through the bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def send_command(self, inter : disnake.ApplicationCommandInteraction,
                           command : str = commands.Param(description="Command to send"),
                           timeout : int = commands.Param(description="Timeout for the command", default = 60)):
        await inter.response.defer(ephemeral=True)
        cmd_split = tuple(command.split(' '))
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_split, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        
                if process.returncode == 0:
                    await inter.edit_original_message(embed=FS.Embed(
                            title=f"✅ command successed",
                            description=f"```{stdout.decode().strip()}```"
                        ))
                else :
                    await inter.edit_original_message(embed=FS.Embed(
                        title=f"❌ Command failed with status code {FS.Emotes.Num[process.returncode]}",
                        description=f"```{stderr.decode().strip()}```"
                    ))
            except TimeoutError:
                await inter.edit_original_message(embed=FS.Embed(
                        title=f"❌ Command timeout"
                    ))
        except FileNotFoundError as e:
            await inter.edit_original_message(embed=FS.Embed(
                    title=f"❌ Command error due to *FileNotFoundError*",
                    description=f"Couldn't find file ****{cmd_split[0]}****"
                ))
    
        
    @commands.slash_command(
        description = "Voir les logs du bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def logs(self, inter : disnake.UserCommandInteraction,
                   level : str = commands.Param(
                       description = "Le level des logs à obtenir.",
                       choices = ["debug","info"],
                       default = "info"
                   ),
                   previous : int = commands.Param(
                       description="Le nombre de fichier en arrière à obtenir",
                       ge = 1,
                       le = 5,
                       default = 1
                   )):
        await inter.response.defer(ephemeral=True)
        if previous == 1:
            file = disnake.File(f"logs/{level}.log")
            await inter.author.send(
                file = file
            )
        else:
            files = [disnake.File(f"logs/{level}.log")]
            for i in range(1, previous):
                try:
                    files.append(disnake.File(f"logs/{level}.log.{i}"))
                except FileNotFoundError as ex:
                    logging.debug(f"logsCmd: file 'logs/{level}.log.{i}' skipped because not found")
            await inter.author.send(
                files = files
            )
        await inter.edit_original_message(embed=FS.Embed(description="Logs sent on private !"))
        
 
    @commands.user_command(
        name = "Voir le lore"
    )
    async def lore(self, inter : disnake.UserCommandInteraction):
        lore_embed = get_lore_embed(inter.target.name)
        if lore_embed == False:
            await inter.response.send_message(
                embed = FS.Embed(
                    description = f"{inter.target.name} n'a pas encore de lore...\nDemande à Hyksos de l'écrire !",
                    thumbnail = FS.Images.Poros.Sweat
                    ),
                ephemeral = True
            )
        else:
            await inter.response.send_message(
                embed = lore_embed,
                delete_after = 60*5
            )
                    
    @commands.user_command(
        name = "Créer / éditer le lore",
        default_member_permissions=disnake.Permissions.all()
    )
    async def addlore(self, inter : disnake.UserCommandInteraction):
        await inter.response.send_modal(
            modal = loreModal(self.bot,inter.target)
        )               
        
    


def setup(bot : commands.InteractionBot):
    bot.add_cog(Basic(bot))