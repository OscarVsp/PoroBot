from typing import List, Union
from .confirmationView import ConfirmationView, ConfirmationStatus
from .memberSelectionView import MemberSelectionView

import disnake


async def confirmation(
    inter : disnake.Interaction,
    title : str = "Confirmation",
    message : str = "Confirmer l'action ?",
    timeout : int = 180,
    confirmationLabel : str = "Confirmer",
    cancelLabel : str = "Annuler",
    color : disnake.Colour = disnake.Colour.red()) -> ConfirmationStatus:
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
        confirmationLabel (`str`, `optional`): 
            The label for the confirmation button.
            Defaults to `"Confirmer"`.
        cancelLabel (`str`, `optional`): 
            The label for the cancel button.
            Defaults to `"Annuler"`.
        color (`disnake.Colour`, `optional`): 
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `ConfirmationStatus`: 
            `State.CONFIRMED` (`=True`) if the user has confirmed the action.
            `State.CANCELLED` (`=False`) if the user has cancelled the action.
            `State.TIMEOUT` (`=False`) if the user has not answered the action before timeout.
    """
    confirmationView = ConfirmationView(inter=inter, title=title, message=message, timeout=timeout, color=color, confirmationLabel=confirmationLabel, cancelLabel=cancelLabel)
    await confirmationView.send()
    await confirmationView.wait()
    return confirmationView.state

async def memberSelection(
    inter : disnake.Interaction,
    title : str = "Sélection des membres",
    message : str = "",
    size : Union[int, List[int]] = None,
    timeout : int = 180,
    pre_selection : List[disnake.Member] = [],
    check = None) -> List[disnake.Member]:
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
        The list of selected members (`List[disnake.member]`)
    """
    if isinstance(size, int):
        size = [size]
    memberSelectionView = MemberSelectionView(inter=inter, title=title, message=message, timeout=timeout, size=size, pre_selection=pre_selection, check=check)
    await memberSelectionView.send()
    await memberSelectionView.wait()
    return memberSelectionView.selected_members
