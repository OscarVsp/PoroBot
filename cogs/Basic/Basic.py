import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.embed import new_embed
from utils import data
import asyncio

# Define a simple View that gives us a counter button
class PoroFeed(disnake.ui.View):
    
    
    def __init__(self):
        super().__init__(timeout=None)
        self.counter = 0


    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @disnake.ui.button(emoji = "<:porosnack:908477364135161877>", style=disnake.ButtonStyle.primary)
    async def feed(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.counter < 9:
            self.counter += 1
            embed = new_embed(description="Continue à nourrir le poro !", image=data.images.poros[self.counter], footer = f"{self.counter}/10")
        else:
            self.counter += 1
            embed = new_embed(description="*#Explosion de poros*", image=data.images.poros[self.counter])
            button.disabled = True
        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(embed = await embed, view=self)


class Basic(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot

    @commands.slash_command(
        name="beer",
        description="Commander des bières (permet de tester le ping du bot).")
    async def beer(self, inter: ApplicationCommandInteraction):
        embed = await new_embed(
            title="Voilà tes bières",
            description=':beer:'*randint(1,10)+"\n Après "+str(round(self.bot.latency,2))+" secondes d'attente seulement !",
            color = data.color.gold)
        embed = await inter.send(embed=embed,delete_after=5)


    @commands.slash_command(
        name="help",
        description="Voir la list des commandes disponible")
    async def help(self, inter: ApplicationCommandInteraction):
        commands = self.bot.get_guild_slash_commands(inter.guild_id) 
        embed = await new_embed(
            title="Commandes",
            description="\n".join([' : '.join(line) for line in list(zip([c.name for c in commands],[c.description for c in commands]))]),
            color = data.color.gold)
        embed = await inter.send(embed=embed,delete_after=5)

    @commands.slash_command(
        name="porosnack",
        description="nourrir un poro")
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.send(embed = await new_embed(description="Nourris le poro !", image=data.images.poros[0], footer="0/10"), view=PoroFeed())
               

def setup(bot):
    bot.add_cog(Basic(bot))