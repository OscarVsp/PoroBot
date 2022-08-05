from typing import List, Optional, Tuple, Union
import disnake
from modules.FastSnake.ConfirmationView import ConfirmationReturnData, ConfirmationView


class ButtonChoice:
    
    def __init__(self, label : str, emoji : Optional[Union[str,disnake.PartialEmoji]] = None):
        self.label : str = label
        self.emoji : Optional[Union[str,disnake.PartialEmoji]] = emoji
        
    def to_button(self, row : int = None, style : disnake.ButtonStyle = disnake.ButtonStyle.secondary) -> disnake.ui.Button:
        return disnake.ui.Button(label=self.label,emoji=self.emoji,style=style,row=row)
    
    @staticmethod
    def from_button(button : disnake.ui.Button):
        return ButtonChoice(label=button.label,emoji=button.emoji)
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, disnake.Button):
            return self.label == __o.label
        elif isinstance(__o, ButtonChoice):
            return self.label == __o.label
        return False
        

class QCMView(ConfirmationView):
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, timeout : int, color : disnake.Colour, choices : List[ButtonChoice], pre_selection : ButtonChoice):
        super().__init__(inter,title,message,timeout,color)
        
        
        if len(choices) > 20:
            raise ValueError("Size of choices should be at max 20")
        
        
        for i,choice in enumerate(choices):
            choice_button = choice.to_button(row = (1+i//5))
            choice_button.callback = self.call_back
            self.add_item(choice_button)
            
        self.response : ButtonChoice = pre_selection
        self.confirm.disabled = not (self.response)
        
    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.response:
            embed.add_field(name="__**Choix actuel**__",value=f"> {self.response.emoji if self.reponse.emoji else '◾'} **{self.response.label}**")
        embed.set_footer(text="Un seul choix possible.")
        return embed
     
    async def call_back(self, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        self.response = ButtonChoice.from_button(interaction.component)
        self.confirm.disabled = False
        await self.update(interaction)
        

class QCMReturnData(ConfirmationReturnData):
    
    def __init__(self, qcmView : QCMView):
        super().__init__(qcmView)
        if self.is_confirmed:
            self._response = qcmView.response
        else:
            self._response = None
            
    @property
    def response(self) -> Optional[ButtonChoice]:
        return self._response
    
    @property
    def label(self) -> Optional[str]:
        if self._response:
            return self._response.label
        
        
    @property
    def emoji(self) -> Optional[disnake.PartialEmoji]:
        if self._response:
            return self._response.emoji
        
    
        
class QRMView(ConfirmationView):
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, timeout : int, color : disnake.Colour, choices : List[ButtonChoice], pre_selection : List[ButtonChoice], limit : int, limit_strict : bool):
        super().__init__(inter,title,message,timeout,color)
        self.limit : int = limit if limit else len(choices)
        self.limit_strict : bool = limit_strict if limit else False
        
        if len(choices) > 20:
            raise ValueError("Size of choices should be at max 20")
        
        
        for i,choice in enumerate(choices):
            choice_button = choice.to_button(row = (1+i//5))
            choice_button.callback = self.call_back
            self.add_item(choice_button)
            
        self.responses : List[ButtonChoice] = pre_selection.copy() if pre_selection else []
        self.check_validity()
        
    def check_validity(self) -> None:
        if self.limit_strict:
            self.confirm.disabled == (len(self.responses) == self.limit)
        else:
            self.confirm.disabled == (len(self.responses) <= self.limit)
        
    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.responses != []:
            embed.add_field(name="__**Choix actuel**__",value="\n".join(f"> {r.emoji if r.emoji else '◾'} **{r.label}**" for r in self.responses))
        if self.limit_strict:
            embed.set_footer(text=f"Exactement {self.limit} réponses nécessaires.")
        else:
            embed.set_footer(text=f"Au maximum {self.limit} réponses possibles.")
        return embed
     
    async def call_back(self, interaction : disnake.MessageInteraction):
        choice = interaction.component
        if choice in self.responses:
            self.responses.remove(choice)
        else:
            self.responses.append(ButtonChoice.from_button(choice))
        self.check_validity()
        await self.update(interaction)

class QRMReturnData(ConfirmationReturnData):
    
    def __init__(self, qRmView : QRMView):
        super().__init__(qRmView)
        if self.is_confirmed:
            self._responses = qRmView.responses
        else:
            self._responses = []
            
    @property
    def responses(self) -> List[ButtonChoice]:
        return self._responses
    
    @property
    def labels(self) -> List[str]:
        return [r.label for r in self._responses]
    
    @property
    def emojis(self) -> List[Optional[disnake.PartialEmoji]]:
        return [r.emoji for r in self._responses]