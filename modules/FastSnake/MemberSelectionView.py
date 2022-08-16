import disnake
from typing import List, Optional, Union
from modules.FastSnake.ConfirmationView import ConfirmationReturnData, ConfirmationView, Target

from .Assets import Emotes


class MemberSelectionView(ConfirmationView):
    
    def __init__(self, target : Target, embeds : List[disnake.Embed], title : str, description : str, timeout : int, pre_selection : List[disnake.Member] = None, check = None,  size : Union[List[int],int] = None, color : disnake.Colour = disnake.Colour.default()):
        super().__init__(target, embeds, title, description, timeout, color)
        
        self.size : Union[List[int],int] = size

        self.selected_members : List[disnake.Member] = pre_selection.copy() if pre_selection else []
        if check:
            self.check = check
        else:
            self.check = MemberSelectionView.default_check
            
        self.options_limited : bool = False
        self.refresh_selection()
        
    @staticmethod
    def default_check(**kwargs):
        return True

        
    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.size:
            embed.add_field(
                name="__Nombre de membre possible :__",
                value=(", ".join(f"**{n}**" for n in self.size) if isinstance(self.size, list) else f"**{self.size}**"),
                inline=False
            )
        embed.add_field(
            name=f"{Emotes.Num(len(self.selected_members))} __Membre(s) sélectionné(s) :__",
            value="\n".join(f"> **{member.display_name}**" for member in self.selected_members) if len(self.selected_members) else "> *Aucun membre sélectionné...*",
                inline=False
        )
        if self.options_limited:
            embed.set_footer(text=f"Le nombre d'option limité à 25. Certains membres ne seront pas dans les options.")
        return embed  
    
            
    
    def refresh_selection(self):
        self.remove.options = []
        self.add.options = []
        self.options_limited = False
        for member in self.target.guild.members:
            if member in self.selected_members:
                if len(self.remove.options) < 25:
                    self.remove.options.append(disnake.SelectOption(label=member.display_name, value=str(member.id)))
                else:
                    self.options_limited = True
            elif self.check(member=member, selected_members=self.selected_members, original_interaction=self.target, size=self.size):
                if len(self.add.options) < 25:
                    self.add.options.append(disnake.SelectOption(label=member.display_name, value=str(member.id)))
                else:
                    self.options_limited = True
                
        if self.remove.options == []:
            self.remove.options = [disnake.SelectOption(label="Placeholder",value="0")]
            self.remove.disabled=True           
        self.remove.max_values = len(self.remove.options)
        
        if self.add.options == []:
            self.add.options = [disnake.SelectOption(label="Placeholder",value="0")]
            self.add.disabled=True
        self.add.max_values = len(self.add.options)
        
        if self.size:
            self.confirm.disabled = (not len(self.selected_members) in self.size if isinstance(self.size, list) else len(self.selected_members) != self.size)
            if self.confirm.disabled:
                self.confirm.label = "Nombre de membre invalide"
            else:
                self.confirm.label = "Valider"
   
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="🗑️ Retirer des membres",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def remove(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for member in self.selected_members.copy():
            if str(member.id) in select.values:
                self.selected_members.remove(member)
                self.add.disabled=False
        self.refresh_selection()
        await self.update(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="🆕 Ajouter des membres",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def add(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for member in interaction.guild.members:
            if str(member.id) in select.values and member not in self.selected_members:
                self.selected_members.append(member)
                self.remove.disabled=False
        self.refresh_selection()
        await self.update(interaction)


class MemberSelectionReturnData(ConfirmationReturnData):
    
    def __init__(self, memberSelectionView : MemberSelectionView):
        super().__init__(memberSelectionView)
        if self.is_confirmed:
            self._members = memberSelectionView.selected_members
        else:
            self._members = None
            
    @property
    def members(self) -> Optional[List[disnake.Member]]:
        return self._members
        
        