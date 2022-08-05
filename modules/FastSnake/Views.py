from typing import List, Optional, Tuple, Union

from modules.FastSnake.ChoicesView import QCMReturnData, QCMView, QRMReturnData, QRMView
from .ConfirmationView import ConfirmationReturnData, ConfirmationView
from .MemberSelectionView import MemberSelectionReturnData, MemberSelectionView

import disnake

async def process(confirmationvView : ConfirmationView) -> ConfirmationView:
    await confirmationvView.send()
    await confirmationvView.wait()
    return confirmationvView

async def confirmation(
    inter : disnake.Interaction,
    title : str = "Confirmation",
    message : str = "Confirmer l'action ?",
    timeout : int = 180,
    color : disnake.Colour = disnake.Colour.red()) -> ConfirmationReturnData:
    """|coro|\n
    Send a confirmation view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        inter (`disnake.Interaction`):
            The interaction for which the confirmation occurs.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        message (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `180`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `ConfirmationReturnData`
    """
    return ConfirmationReturnData((await process(ConfirmationView(inter=inter, title=title, message=message, timeout=timeout, color=color))))


async def memberSelection(
    inter : disnake.Interaction,
    title : str = "Sélection des membres",
    message : str = "",
    size : Union[int, List[int]] = None,
    timeout : int = 180,
    pre_selection : List[disnake.Member] = [],
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
        inter (`disnake.Interaction`):
            The interaction for which the confirmation occurs.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        message (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        size (`int`|`List[int]`, `optional`): 
            The nombre(s) of selected member required to be able to validate the selection.
            Defaults to `None`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `180`.
        pre_selection (`List[disnake.Member]`, `optional`): 
            The member to include into the selection at the beginning.
            Defaults to `[]`.
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
        original_interaction (`disnake.Interaction`):
            The original interaction received by the confirmationView at the beginning.
            

    Returns
    --------
        `MemberSelectionReturnData`
    """
    return MemberSelectionReturnData(await process(MemberSelectionView(inter=inter, title=title, message=message, timeout=timeout, size=size, pre_selection=pre_selection, check=check, color=color)))


async def QCM(
    inter : disnake.Interaction,
    choices : List[str],
    pre_selection : Optional[str],
    title : str = "Choix",
    message : str = "Choisissez parmit les propositions ci-dessous",
    timeout : int = 180,
    color : disnake.Colour = disnake.Colour.red()) -> QCMReturnData:
    """|coro|\n
    Send a QCM view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        inter (`disnake.Interaction`):
            The interaction for which the confirmation occurs.
        choices (`List[str]`)
            The choices available. Either `str` for label only, or `Tuple[str,str]` for `(label,emoji)`.
        pre_selection (`Optional[str]`):
            The pre-selected choice.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        message (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `180`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `QCMReturnData`
    """
    return QCMReturnData(await process(QCMView(inter, title, message, timeout, color, choices, pre_selection)))


async def QRM(
    inter : disnake.Interaction,
    choices : List[str],
    pre_selection : list[str] = None,
    limit : int = None,
    limit_stric : bool = False,
    title : str = "Choix",
    message : str = "Choisissez parmit les propositions ci-dessous",
    timeout : int = 180,
    color : disnake.Colour = disnake.Colour.red()) -> QRMReturnData:
    """|coro|\n
    Send a QCM view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        inter (`disnake.Interaction`):
            The interaction for which the confirmation occurs.
        choices (`List[str]`):
            The choices available. Either `str` for label only, or `Tuple[str,str]` for `(label,emoji)`.
        pre_selection (`List[str]`):
            The preselected choices.
            Defaults to `None`
        limit  (`int`):
            The number of choice that someone can choose. `None` for no limit.
            Defaults to `None`.
        limit_stric (`bool`):
            Is the number of choice should be exactly equal to the limit.
            Defaults to `False`
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        message (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `180`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `QRMReturnData`
    """
    return QRMReturnData(await process(QRMView(inter, title, message, timeout, color, choices, pre_selection, limit, limit_stric)))
