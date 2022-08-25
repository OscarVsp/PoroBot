import disnake
from modules import FastSnake as FS
from .classes import TournamentData


class NotificationModal(disnake.ui.Modal):
    def __init__(self, tournament: TournamentData):
        components = [
            disnake.ui.TextInput(
                label="Le titre du message à envoyer", style=disnake.TextInputStyle.short, custom_id="title"
            ),
            disnake.ui.TextInput(
                label="Le contenu du message à envoyer", style=disnake.TextInputStyle.paragraph, custom_id="description"
            ),
            disnake.ui.TextInput(
                label="Bannière",
                placeholder="La bannière du tournoi sera utilisé par défaut.",
                required=False,
                value=None,
                style=disnake.TextInputStyle.short,
                custom_id="banner",
            ),
        ]
        self.tournament: TournamentData = tournament
        super().__init__(title="Création d'une annonce", components=components, timeout=600)

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer()
        embed = FS.Embed(
            title=f"__**{interaction.text_values.get('title')}**__",
            description=interaction.text_values.get("description"),
            image=interaction.text_values.get("banner")
            if interaction.text_values.get("banner")
            else self.tournament.banner,
        )
        msg = await self.tournament.notif_channel.send(embed=embed)
        self.tournament.notif_messages.append(msg)
        msg = await interaction.edit_original_message(
            embed=FS.Embed(
                title="✅ __**Notification sent**__",
                description=f"[Notification]({msg.jump_url}) has been sent to {self.tournament.notif_channel.mention} !",
            )
        )
        await msg.delete(delay=2)
