import disnake
from typing import List

from .Embed import Embed
from .Assets import *


class MemberSelectionView(disnake.ui.View):
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, size : List[int], timeout : int, pre_selection : List[disnake.Member], check):
        super().__init__(timeout=timeout)
        self.inter : disnake.Interaction = inter
        self.title : str = title
        self.message : str = message
        self.size : List[int] = size
        self.selected_members : List[disnake.Member] = pre_selection
        if check:
            self.check = check
        else:
            self.check = MemberSelectionView.default_check
        self.is_application_interaction : bool = isinstance(inter, disnake.ApplicationCommandInteraction)
        self.is_view_interaction : bool = isinstance(inter, disnake.MessageInteraction)
        
    @staticmethod
    def default_check(**kwargs):
        return True

        
    @property
    def embed(self) -> disnake.Embed:
        return Embed(
            title = f"__**{self.title.upper()}**__",
            description=self.message,
            fields={
                'name':f"{Emotes.Num[len(self.selected_members)]}__membre(s) sélectionné(s) :__",
                'value':"\n".join(f"> {member.mention}" for member in self.selected_members) if len(self.selected_members) else "> *Aucun membre sélectionné...*"
            },
            footer_text=f"Il faut un nombre de membre sélectionné(s) compris dans {self.size} pour pouvoir valider" if self.confirm.disabled else disnake.Embed.Empty
        )       
    
            
    async def send(self):
        self.refresh_selection()
        if self.is_application_interaction:
            if self.inter.response.is_done():
                original_embeds = (await self.inter.original_message()).embeds
                await self.inter.edit_original_message(embeds=original_embeds+[self.embed], view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
        elif self.is_view_interaction:
            original_embeds = self.inter.message.embeds
            await self.inter.response.edit_message(embeds=original_embeds+[self.embed], view=self)
            
    def refresh_selection(self):
        self.remove.options = []
        self.add.options = []
        for member in self.inter.guild.members:
            if member in self.selected_members:
                self.remove.options.append(disnake.SelectOption(label=member.display_name, value=str(member.id)))
            elif self.check(member=member, selected_members=self.selected_members, original_interaction=self.inter, size=self.size):
                self.add.options.append(disnake.SelectOption(label=member.display_name, value=str(member.id)))
                
        if self.remove.options == []:
            self.remove.options = [disnake.SelectOption(label="Placeholder",value="0")]
            self.remove.disabled=True           
        self.remove.max_values = len(self.remove.options)
        
        if self.add.options == []:
            self.add.options = [disnake.SelectOption(label="Placeholder",value="0")]
            self.add.disabled=True
        self.add.max_values = len(self.add.options)
        
        if self.size:
            self.confirm.disabled = not len(self.selected_members) in self.size
     
    async def update(self, inter : disnake.MessageInteraction = None):
        if inter == None:
            await self.inter.edit_original_message(
                embed = self.embed,
                view = self
            )
        else:
            await inter.response.edit_message(
                embed = self.embed,
                view = self
            ) 
    @disnake.ui.button(emoji = "✅", label = "Valider", style=disnake.ButtonStyle.primary)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        await interaction.response.defer()
        
        
    @disnake.ui.button(emoji = "❌", label = "Annuler", style=disnake.ButtonStyle.danger)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        self.selected_members = None
        await interaction.response.defer()
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="➖ Retirer des membres",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def remove(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for member in self.selected_members.copy():
            if str(member.id) in select.values:
                self.selected_members.remove(member)
                self.add.disabled=False
        self.refresh_selection()
        await self.update(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="➕ Ajouter des membres",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def add(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for member in interaction.guild.members:
            if str(member.id) in select.values:
                self.selected_members.append(member)
                self.remove.disabled=False
        self.refresh_selection()
        await self.update(interaction)

        
