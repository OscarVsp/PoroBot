import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.embed import new_embed
from utils import data
from .view import *
import asyncio


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
            embed=new_embed(
                title="Voilà tes bières",
                description=f":beer:\n Après {round(self.bot.latency,2)} secondes d'attente seulement !",
                color = data.color.gold
            ),
            view = Beer(inter)
        )


    @commands.slash_command()
    async def porosnack(self, inter: ApplicationCommandInteraction):
        """Nourrir le poro
        """
        await inter.response.send_message(embed = new_embed(description="Nourris le poro !", image=data.images.poros.growings[0], footer="0/10"), view=PoroFeed(inter))
        
        
    
    @commands.slash_command(
        description = "Supprimer les derniers messages du channel"
    )
    async def clear(self, inter : ApplicationCommandInteraction,
        nombre : int = commands.Param(
            description = "le nombre de message à supprimer",
            gt = 0
        )
    ):
        await inter.response.defer()
        await inter.channel.purge(limit=nombre)
        await inter.response.send_message(
            embed = new_embed(
                description = f":broom: {nombre} messages supprimés ! :broom:"),
            delete_after=3)
        
    @commands.slash_command(
        description = "Lancer des dés"
    )
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
        await inter.response.send_message(
            embed = new_embed(
                title = f"🎲 Lancé de {nombre_de_des} dé(s) à {nombre_de_faces} face(s)",
                description = f"Utilise le bouton pour commencer à lancer les dés !"
            ),
            view = DiceView(inter, nombre_de_faces, nombre_de_des)
        )
        
        
    
               

def setup(bot):
    bot.add_cog(Basic(bot))