import disnake 
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from .scraper import Almanax_scraper
import asyncio

class AlmanaxView(disnake.ui.View):
    
    MONTHS = {
        "01":"janvier",
        "02":"février",
        "03":"mars",
        "04":"avril",
        "05":"mai",
        "06":"juin",
        "07":"juillet",
        "08":"août",
        "09":"septembre",
        "10":"octobre",
        "11":"novembre",
        "12":"décembre",
        }
    
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(emoji = ":calendar_spiral:", label = "Semaine", style=disnake.ButtonStyle.primary)
    async def week(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.get_almanax(7)))
        
    @disnake.ui.button(emoji = ":calendar_spiral:", label = "Mois", style=disnake.ButtonStyle.primary)
    async def month(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.get_almanax(31)))
        
    @disnake.ui.button(emoji = ":calendar_spiral:", label = "Année", style=disnake.ButtonStyle.primary)
    async def year(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.get_almanax(365)))

    @classmethod
    def data_to_embed(cls,data):
        if type(data) == list:
            max_embed_size = 4000
            offrandes = "\n".join([f"{d['date']} : **{d['item_quantity']}x** {d['item']}" for d in data])
            size = len(offrandes)
            offrandes = [offrandes[i: i + max_embed_size] for i in range(0, len(offrandes), max_embed_size)]
            embed = FS.Embed(
                title = f":calendar_spiral:__**Almanax des {len(data)} prochains jours**__:calendar_spiral:",
                description = offrandes[0]
            )
            if len(offrandes) >= 2:
                embeds = [embed]
                offrandes.pop(0)
                for offrande in offrandes:
                    embeds.append(FS.Embed(
                        description = offrande
                    ))
                return embeds
            return embed
        
        return FS.Embed(
            title = f":calendar_spiral:__**Almanax du {data['date']}**__:calendar_spiral:",
            fields = [
                {"name" : "__Offrande :__",
                    "value" : f"**{data['item_quantity']}x** {data['item']}"},
                {"name" : "__Bonus :__",
                    "value" : f"{data['description']}"}
            ],
            thumbnail = f"{data['item_picture_url']}"
        )
        
