import disnake 
from disnake import ApplicationCommandInteraction
from utils.embed import new_embed
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
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.scrape(7)))
        
    @disnake.ui.button(emoji = ":calendar_spiral:", label = "Mois", style=disnake.ButtonStyle.primary)
    async def month(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.scrape(31)))
        
    @disnake.ui.button(emoji = ":calendar_spiral:", label = "Année", style=disnake.ButtonStyle.primary)
    async def year(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed = self.data_to_embed(Almanax_scraper.scrape(365)))

    @staticmethod
    def data_to_embed(data):
        if type(data) == list:
            return new_embed(
                title = f"__**Almanax des {len(data)} prochains jours**__",
                fields= [
                    {"name" : "Dates",
                     
                     "value" : "\n".join([f"{d['date'].strftime('%d %b')}" for d in data]),
                     "inline" : True
                    },
                    {"name" : "Offrandes",
                     "value" : "\n".join([f"**{d['item_quantity']}x** {d['item']}" for d in data]),
                     "inline" : True
                    },
                ]
            )
        else:
            return new_embed(
                title = f"__**Almanax du {data['date'].strftime('%d %b')}**__",
                fields = [
                    {"name" : "__Offrande :__",
                     "value" : f"**{data['item_quantity']}x** {data['item']}"},
                    {"name" : "__Bonus :__",
                     "value" : f"{data['description']}"}
                ],
                thumbnail = f"{data['item_picture_url']}"
            )
        
