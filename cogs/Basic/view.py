import disnake 
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from random import choices
from utils import data
import asyncio
import pickledb

loredb = pickledb.load("cogs/Basic/lore.db", False)

def get_lore_embed(name):
    lore_data = loredb.get(name)
    if lore_data == False:
        return False
    return FastEmbed(
        author_name = lore_data.get('alias'),
        author_icon_url = lore_data.get('icon')[5:-6],
        description = f"*{lore_data.get('lore')}*",
        image = lore_data.get('image')[5:-6],
        footer_text = f"Lore de {name}, créé par Hyksos"
    )

class PoroFeed(disnake.ui.View):
    
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=10)
        self.inter = inter
        self.counter = 0

    @disnake.ui.button(emoji = "<:porosnack:908477364135161877>", label = "Donner un porosnack", style=disnake.ButtonStyle.primary)
    async def feed(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.counter < 9:
            self.counter += 1
            await interaction.response.edit_message(
                embed = FastEmbed(
                    description="Continue à nourrir le poro !", 
                    image=data.images.poros.growings[self.counter], 
                    footer_text = f"{self.counter}/10"),
                view=self)
        else:
            self.counter += 1
            self.remove_item(button)
            await interaction.response.edit_message(
                embed = FastEmbed(
                    description="*#Explosion de poros*", 
                    image=data.images.poros.growings[self.counter]),
                view=self)

    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()

class Beer(disnake.ui.View):
        
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=10)
        self.inter = inter
        self.counter = 1

    @disnake.ui.button(emoji = "🍺", label = "Boire une bière", style=disnake.ButtonStyle.primary)
    async def beer(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.counter += 1
        if self.counter < 10:
            await interaction.response.edit_message(
                embed=FastEmbed(
                    title="Voilà tes bières",
                    description=f"{':beer:'*self.counter} \n Après {round(interaction.bot.latency,2)} secondes d'attente seulement !",
                    color = data.color.gold
                ),
                view = self
            )
        else:
            button.disabled = True
            self.stop()
            await interaction.response.edit_message(
                embed=FastEmbed(
                    title="Déjà 10 bières ?! On va se calmer là...",
                    description=f"{':beer:'*self.counter} \n Après {round(interaction.bot.latency,2)} secondes d'attente seulement !",
                    color = data.color.gold
                ),
                view = self
            )
        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
 
class loreModal(disnake.ui.Modal):
    def __init__(self,bot,member) -> None:
        self.bot = bot
        self.member = member
        data = loredb.get(self.member.name)
        if data == False:
            components = [
                disnake.ui.TextInput(
                    label="alias",
                    placeholder="L'alias du membre",
                    custom_id="alias",
                    style=disnake.TextInputStyle.short,
                ),disnake.ui.TextInput(
                    label="icon",
                    placeholder="""L'icon du membre (site imgur, lien "BBC")""",
                    custom_id="icon",
                    required = False,
                    style=disnake.TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="lore",
                    placeholder="Le lore du membre",
                    custom_id="lore",
                    style=disnake.TextInputStyle.paragraph
                ),
                disnake.ui.TextInput(
                    label="image",
                    placeholder="""L'icon du membre (site imgur, lien "BBC")""",
                    custom_id="image",
                    required = False,
                    style=disnake.TextInputStyle.short
                )
            ]
            super().__init__(title = f"Créer un lore pour {self.member.name}", custom_id="create_lore", components=components)
        else:
            components = [
                disnake.ui.TextInput(
                    label="alias",
                    placeholder="L'alias du membre",
                    custom_id="alias",
                    value = data.get('alias'),
                    style=disnake.TextInputStyle.short,
                ),disnake.ui.TextInput(
                    label="icon",
                    placeholder="""L'icon du membre (site imgur, lien "BBC")""",
                    custom_id="icon",
                    value = data.get('icon'),
                    required = False,
                    style=disnake.TextInputStyle.short,
                ),
                disnake.ui.TextInput(
                    label="lore",
                    placeholder="Le lore du membre",
                    custom_id="lore",
                    value = data.get('lore'),
                    style=disnake.TextInputStyle.paragraph
                ),
                disnake.ui.TextInput(
                    label="image",
                    placeholder="""L'icon du membre (site imgur, lien "BBC")""",
                    custom_id="image",
                    value = data.get('image'),
                    required = False,
                    style=disnake.TextInputStyle.short
                )
            ]
            super().__init__(title = f"Editer le lore pour {self.member.name}", custom_id="create_lore", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        loredb.set(
            self.member.name,
            inter.text_values
        )
        loredb.dump()
        await inter.response.send_message(
            embed = get_lore_embed(self.member.name),
            ephemeral = True
        )
        