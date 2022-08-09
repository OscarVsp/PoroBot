import disnake
from modules import FastSnake as FS

class NotificationModal(disnake.ui.Modal):
    
    def __init__(self, phaseView):
        components = [
            disnake.ui.TextInput(
                label="Le titre du message à envoyer",
                style=disnake.TextInputStyle.short,
                custom_id="title"
            ),
            disnake.ui.TextInput(
                label="Le contenu du message à envoyer",
                style=disnake.TextInputStyle.paragraph,
                custom_id="description"
            ),
            disnake.ui.TextInput(
                label="Bannière",
                placeholder="La bannière du tournoi sera utilisé par défaut.",
                required = False,
                value = None,
                style=disnake.TextInputStyle.short,
                custom_id="banner"
            ),
        ]
        self.phaseView = phaseView
        super().__init__(title="Création d'une annonce", components=components, timeout=600)
            
       
        
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer()
        embed = self.phaseView.annonce_embed(
            title=f"__**{interaction.text_values.get('title')}**__",
            description=interaction.text_values.get("description"),
            banner = interaction.text_values.get("banner")
        )
        msg : disnake.Message = await self.phaseView.channel_overview.send(
            content=self.phaseView.phase.role.mention,
            embed=embed
        )
        msg = await interaction.edit_original_message(embed=FS.Embed(title="✅ __**Notification sent**__",description=f"[Notification]({msg.jump_url}) has been sent to {self.phaseView.channel_overview.mention} !"))
        await msg.delete(delay=2)
        
        
