import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from .TournamentManager import Tournament2v2Roll
import modules.FastSnake as FS





class Tournament(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : InteractionBot = bot
        
    @commands.slash_command(name="tournament",     
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False
    )
    async def tournament(self, inter):
        pass
    
    
    @tournament.sub_command(
        name="roll2v2",
        description="Créer un tournoi en format 2v2 roll"
    )
    async def roll2v2(self, inter : ApplicationCommandInteraction,
                             nom : str = commands.Param(description="Nom du tournoi"),
                             size : int = commands.Param(description="Nombre de participants", choices=[4,5,8])
                        ):

        await inter.response.defer(ephemeral=True)
        tournament = Tournament2v2Roll(inter.guild,size,name=nom)
        await tournament.build()
        await inter.edit_original_message(embed=FS.Embed(description=f"Tournois [{tournament.name}]({tournament.admin_message.jump_url}) créé !"))  
    

def setup(bot : InteractionBot):
    bot.add_cog(Tournament(bot))