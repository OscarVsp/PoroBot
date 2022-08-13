from typing import List, Optional, Tuple, Union

from modules.FastSnake.ChoicesView import ButtonChoice, QCMReturnData, QCMView, QRMReturnData, QRMView
from .ConfirmationView import ConfirmationReturnData, ConfirmationView, Target
from .MemberSelectionView import MemberSelectionReturnData, MemberSelectionView

import disnake

async def process(confirmationvView : ConfirmationView) -> ConfirmationView:
    await confirmationvView.send()
    await confirmationvView.wait()
    return confirmationvView

async def confirmation(
    target : Target,
    embeds : List[disnake.Embed] = [],
    title : str = "Confirmation",
    description : str = "Confirmer l'action ?",
    thumbnail : str = disnake.Embed.Empty,
    timeout : int = None,
    color : disnake.Colour = disnake.Colour.red()) -> ConfirmationReturnData:
    """|coro|\n
    Send a confirmation view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        target (`Target`):
            The interaction for which the confirmation occurs.
        embeds (`List[disnake.Embed]`)
            The embed to send with the view.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        description (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `ConfirmationReturnData`
    """
    return ConfirmationReturnData((await process(ConfirmationView(target=target, embeds=embeds, title=title, description=description, thumbnail = thumbnail, timeout=timeout, color=color))))


async def memberSelection(
    target : Target,
    embeds : List[disnake.Embed] =[],
    title : str = "Sélection des membres",
    description : str = "",
    size : Union[int, List[int]] = None,
    timeout : int = None,
    pre_selection : List[disnake.Member] = None,
    check = None,
    color : disnake.Colour = disnake.Colour.blue()) -> MemberSelectionReturnData:
    """|coro|\n
    Send a member selection view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the selection, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        target (`Target`):
            The interaction for which the confirmation occurs.
        embeds (`List[disnake.Embed]`)
            The embed to send with the view.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        description (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        size (`int`|`List[int]`, `optional`): 
            The nombre(s) of selected member required to be able to validate the selection.
            Defaults to `None`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        pre_selection (`List[disnake.Member]`, `optional`): 
            The member to include into the selection at the beginning.
            Defaults to `None`.
        check (`func(**kwargs) -> bool`, `optional`): 
            A function that can be used to filter if a member can be added to the selection or not.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.
            
    Check function
    --------
    The kwargs passed to the check function are:
        member (`disnake.Member`):
            The member to filter.
        selected_members (`List[disnake.Member]`):
            The list of members that are already selected.
        size (`List[int]`):
            The list of possible nombre(s) of member selected to be able to validate.
        original_interaction (`Target`):
            The original interaction received by the confirmationView at the beginning.
            

    Returns
    --------
        `MemberSelectionReturnData`
    """
    return MemberSelectionReturnData(await process(MemberSelectionView(target=target, embeds=embeds, title=title, description=description, timeout=timeout, size=size, pre_selection=pre_selection, check=check, color=color)))


async def QCM(
    target : Target,
    choices : List[ButtonChoice],
    pre_selection : Optional[str],
    embeds : List[disnake.Embed] = [],
    title : str = "Choix",
    description : str = "Choisissez parmit les propositions ci-dessous",
    timeout : int = None,
    color : disnake.Colour = disnake.Colour.purple()) -> QCMReturnData:
    """|coro|\n
    Send a QCM view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        target (`Target`):
            The interaction for which the confirmation occurs.
        embeds (`List[disnake.Embed]`)
            The embed to send with the view.
        choices (`List[ButtonChoice]`)
            The choices available. Either `str` for label only, or `Tuple[str,str]` for `(label,emoji)`.
        pre_selection (`Optional[str]`):
            The pre-selected choice.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        description (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `QCMReturnData`
    """
    return QCMReturnData(await process(QCMView(target, embeds, title, description, timeout, color, choices, pre_selection)))


async def QRM(
    target : Target,
    choices : List[ButtonChoice],
    embeds : List[disnake.Embed] = [],
    pre_selection : list[ButtonChoice] = None,
    min : int = 0,
    max : int = None,
    title : str = "Choix",
    description : str = "Choisissez parmit les propositions ci-dessous",
    timeout : int = None,
    color : disnake.Colour = disnake.Colour.purple()) -> QRMReturnData:
    """|coro|\n
    Send a QCM view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        target (`Target`):
            The interaction for which the confirmation occurs.
        embeds (`List[disnake.Embed]`)
            The embed to send with the view.
        choices (`List[ButtonChoice]`):
            The choices available.
        pre_selection (`List[ButtonChoice]`):
            The preselected choices.
            Defaults to `None`
        min (`int`):
            The minimum choice that someone can choose.
            Defaults to `0`.
        max (`int`):
            The maximum choice that someone can choose. `None` for no limit
            Defaults to `0`.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Choix"`.
        description (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Choisissez parmit les propositions ci-dessous"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `QRMReturnData`
    """
    return QRMReturnData(await process(QRMView(target, embeds, title, description, timeout, color, choices, pre_selection, min, max)))
