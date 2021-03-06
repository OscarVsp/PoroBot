import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from utils import data
from .view import *
import asyncio
import subprocess

async def is_owner(ctx):
    return ctx.author.id == 281401408597655552


class Basic(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot

    @commands.slash_command(
        description = "Commander un bière (test le ping du bot)"
    )
    async def beer(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FastEmbed(
                title="Voilà tes bières",
                description=f":beer:\n Après {round(self.bot.latency,2)} secondes d'attente seulement !",
                color = data.color.gold
            ),
            view = Beer(inter)
        )


    @commands.slash_command(
        description = "Nourrir le poro avec des porosnacks jusqu'à le faire exploser"
    )
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed = FastEmbed(
                description="Nourris le poro !",
                image=data.images.poros.growings[0],
                footer_text="0/10"
            ),
            view=PoroFeed(inter)
        )
        
    @commands.slash_command(
        description="Update the bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def update(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        completedProcess = subprocess.run("cd ~/PoroBot/ && git pull origin master",text=True,capture_output=True)
        if completedProcess.returncode == 0:
            await inter.edit_original_message(embed=FastEmbed(
                title=f"✅ Update succes",
                description=f"```{completedProcess.stdout}```"
            ))
        else :
            await inter.edit_original_message(embed=FastEmbed(
                title=f"❌ Update failed with status code {data.emotes.number_to_emotes[completedProcess.returncode]}",
                description=f"```{completedProcess.stdout}```"
            ))
            
    @commands.slash_command(
        description="Restart the bot",
        default_member_permissions=disnake.Permissions.all()
    )
    @commands.check(is_owner)
    async def restart(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        if self.bot.test_mode:
            await inter.edit_original_message(embed=FastEmbed(
                description=f"Cannot restart in test mode."
            ))
        else:
            completedProcess = subprocess.run("pm2 restart poro",text=True,capture_output=True)
            if completedProcess.returncode == 0:
                await inter.edit_original_message(embed=FastEmbed(
                    title=f"✅ Restart succes",
                    description=f"```{completedProcess.stdout}```"
                ))
            else :
                await inter.edit_original_message(embed=FastEmbed(
                    title=f"❌ Restart failed with status code {data.emotes.number_to_emotes[completedProcess.returncode]}",
                    description=f"```{completedProcess.stdout}```"
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
        await inter.edit_original_message(embed=FastEmbed(description="Logs sent on private !"))
        
 
    @commands.user_command(
        name = "Voir le lore"
    )
    async def lore(self, inter : disnake.UserCommandInteraction):
        lore_embed = get_lore_embed(inter.target.name)
        if lore_embed == False:
            await inter.response.send_message(
                embed = FastEmbed(
                    description = f"{inter.target.name} n'a pas encore de lore...\nDemande à Hyksos de l'écrire !",
                    thumbnail = data.images.poros.sweat
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
        
    


def setup(bot):
    bot.add_cog(Basic(bot))