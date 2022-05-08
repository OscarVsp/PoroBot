import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.embed import new_embed
from utils import data
from .view import PoroFeed
import asyncio


class Basic(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot

    @commands.slash_command()
    async def beer(self, inter: ApplicationCommandInteraction):
        """Commander une bière (permet de tester le ping du bot)
        """
        embed = new_embed(
            title="Voilà tes bières",
            description=':beer:'*randint(1,10)+"\n Après "+str(round(self.bot.latency,2))+" secondes d'attente seulement !",
            color = data.color.gold)
        embed = await inter.send(embed=embed,delete_after=5)


    @commands.slash_command()
    async def porosnack(self, inter: ApplicationCommandInteraction):
        """Nourrir le poro
        """
        await inter.response.send_message(embed = new_embed(description="Nourris le poro !", image=data.images.poros[0], footer="0/10"), view=PoroFeed(inter))
        
        
    
    @commands.slash_command()
    async def clear(self, inter : ApplicationCommandInteraction,
        nombre : commands.Range[1, ...]
    ):
        """Supprime les derniers messages du channel
        
        Parameters
        ----------
        nombre: le nombre de message à supprimer
        """
        await inter.response.defer()
        await inter.channel.purge(limit=nombre)
        await inter.response.send_message(
            embed = new_embed(
                description = f":broom: {nombre} messages supprimés ! :broom:"),
            delete_after=3)
        
    @commands.slash_command()
    async def dice(self, inter : ApplicationCommandInteraction,
        nombre_de_faces : int = commands.Param(
            description = "le nombre de face des dés (6 par default)",
            default = 6,
            gt = 0
            ),
        nombre_de_des : int = commands.Param(
            description = "le nombre dé à lancer (1 par default)",
            default = 1,
            gt = 0
            )
    ):
        sortie = sample([i+1 for i in range(nombre_de_faces)],nombre_de_des)
        resultats = "__" + "__, __".join(sortie) + "__"
        await inter.response.send_message(
            embed = new_embed(
                title = f"Lancé de {nombre_de_des} dé(s) à {nombre_de_faces} face(s)",
                description = f"**Résultats :** {resultats}\n**Total :** __{sum(sortie)}__"
            ), delete_after = 60
        )
        
        
    
               

def setup(bot):
    bot.add_cog(Basic(bot))