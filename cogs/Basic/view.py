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
 
"""        
class DiceView(disnake.ui.View):
    
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=600)
        self.inter = inter    
        self.nbr_faces = 6
        self.nbr_des = 1   
        
        self.face_input = disnake.ui.TextInput(label = "Choisit le nombre de face des dés", value = f"{self.nbr_faces}", custom_id = "nbr_faces", min_length = 1, style = disnake.TextInputStyle.short)
        self.number_input = disnake.ui.TextInput(label = "Choisit le nombre de dé à lancé", value = f"{self.nbr_des}", custom_id = "nbr_des", min_length = 1, style = disnake.TextInputStyle.short)
        
        self.add_item(self.face_input)
        self.add_item(self.number)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 1)
    async def face_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if 
        if interaction.author == self.activePlayer.member:
            await self.play_turn(interaction, next((p for p in self.players if p.display_name == select.values[0])))
        else:
            await self.unautorized_interaction(interaction)

    @disnake.ui.button(label = "Roll", emoji = "🎲", style=disnake.ButtonStyle.primary)
    async def roll(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            self.nbr_des = int(self.number_input.value)
            self.nbr_faces = int(self.face_input.value)
            sortie = choices([i+1 for i in range(self.nbr_faces)],k=self.nbr_des)
            resultats = "\n".join(["".join(data.emotes.number_to_emotes(nombre,len(str(self.nbr_faces)))) for nombre in sortie])
            total = ''.join(data.emotes.number_to_emotes(sum(sortie)))
            await interaction.response.edit_message(
                embed = new_embed(
                    title = f"🎲 __Lancé de **{self.nbr_des}** dé(s) à **{self.nbr_faces}** face(s)__",
                    fields = [
                        {
                            'name' : '__Résultats du lancé :__',
                            'value' : f"{resultats}"
                        },{
                            'name' : '__Total :__',
                            'value' : f"{total}"
                        }
                    ]
                ),
                view=self
            )
        except ValueError:
            self.face_input.value = self.nbr_faces
            self.number_input.value = self.nbr_des
            await interaction.response.edit_message( 
                embed = new_embed(
                    title = f"🎲 __Lancé de dé(s)__",
                    description = ":x: *le nombre de face et le nombre de dé doivent être des nombres entier.*"
                ),
                view=self
            )
        
    @disnake.ui.button(label = "Stop", style=disnake.ButtonStyle.danger)
    async def stop_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        await self.inter.delete_original_message()
        
 
        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()"""
        
        