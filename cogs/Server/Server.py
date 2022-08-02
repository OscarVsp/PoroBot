import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, NotFound
from utils.FastEmbed import FastEmbed
from typing import List

from utils.confirmationView import confirmation,ConfirmationStatus
from utils.memberSelectionView import memberSelection
from .view import Locker
from utils.data import color

class Server(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : commands.InteractionBot = bot
        self.locked_channels : List[Locker] = []
        
    @staticmethod
    def incoming_connection(before : disnake.VoiceState, after : disnake.VoiceState) -> bool:
        return (after.channel != None and before.channel != after.channel)
    
    @staticmethod
    def outgoing_connection(before : disnake.VoiceState, after : disnake.VoiceState) -> bool:
        return (before.channel != None and before.channel != after.channel)
 
    @commands.slash_command(
        name="clear",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False)
    async def clear(self, inter):
        pass
        
        
    @clear.sub_command(
        name='message',
        description = "Supprimer les derniers messages du channel"
    )
    async def clearMessage(self, inter : ApplicationCommandInteraction,
        nombre : int = commands.Param(
            description = "le nombre de message à supprimer",
            gt = 0
        )
    ):
        confirm : ConfirmationStatus = await confirmation(inter,
                               title=f"__**Suppression de {nombre} message(s)**__",
                               message=f"Êtes-vous sûr de vouloir supprimer les {nombre} dernier(s) message(s) de ce channel ?\nCette action est irréversible !",
                               confirmationLabel=f"Supprimer les message(s)",
                               timeout=5)
        if confirm:
            await inter.edit_original_message(embed=FastEmbed(description = f"Suppression de {nombre} message(s) en cours... ⌛", color=color.vert), view=None)
            await inter.channel.purge(limit=nombre)
            await inter.edit_original_message(embed = FastEmbed(description = f":broom: {nombre} messages supprimés ! :broom:", color=color.vert))
        elif confirm.is_cancelled:
            await inter.edit_original_message(embed = FastEmbed(description = f":o: Suppresion de {nombre} message(s) annulée", color=color.gris), view = None)
        else:
            await inter.edit_original_message(embed = FastEmbed(description = f":o: Suppresion de {nombre} message(s) timeout", color=color.gris), view = None)
        
    @clear.sub_command(
        name='category',
        description = "Supprimer une categorie"
    )
    async def clearCat(self, inter : ApplicationCommandInteraction,
        categorie : disnake.CategoryChannel = commands.Param(description = "Choisissez categorie à suppimer")
    ):

        if await confirmation(inter,
                              title=f"__**Suppression de la categorie *{categorie.name}***__",
                              message=f"Êtes-vous sûr de vouloir supprimer la catégorie ***{categorie.mention}*** ?\nCela supprimera également les {len(categorie.channels)} channels contenus dans celle-ci :\n"+"\n".join(channel.mention for channel in categorie.channels)+"\nCette action est irréversible !",
                              confirmationLabel="Supprimer la catégorie"):
            await inter.edit_original_message(embed=FastEmbed(description = f"Suppression de la catégorie *{categorie.name}* en cours... ⌛", color=color.vert), view=None)
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(embed=FastEmbed(description = f":broom: **Catégorie** *{categorie.name}* **supprimée** ! :broom:", color=color.vert))
            except NotFound:
                    pass
        else:
            await inter.edit_original_message(embed=FastEmbed(description = f":o: Suppression de la catégorie {categorie.mention} annulée !", color=color.gris), view = None)
          
    @commands.slash_command(
        name="export",default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
    )    
    async def export(self, inter):
        pass
    
    @export.sub_command_group(
        name="role"
    )
    async def export_role(self, inter):
        pass
    
    
            
    @export_role.sub_command(
        name="from_event",
        description="Créer un role à partir des participants d'un évennement."
    )
    async def export_role_from_event(self, inter : disnake.ApplicationCommandInteraction,
                              event : str = commands.Param(description="L'évennement depuis lequel exporter les membres"),
                              name : str = commands.Param(description='Le nom du role à créer (default = "event.name role")', default=None)):
        await inter.response.defer(ephemeral=True)
        events = await inter.guild.fetch_scheduled_events()
        event : disnake.GuildScheduledEvent = next((e for e in events if e.name == event), None)
        if not name:
            name = f"{event.name} role"
        event_members = []
        async for member in event.fetch_users():
            event_members.append(member)
        
        selected_members = await memberSelection(inter, title="Export role from event", message="Select members below", timeout=300, pre_selected_members=event_members)    
        await inter.edit_original_message(embed=FastEmbed(description="\n".join(member.display_name for member in selected_members) if len(selected_members) > 0 else "*Aucun membre sélectionné*"), view = None)
    
        
    @export_role_from_event.autocomplete("event")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        events = []
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                events.append(event.name)
        return events    
    
    @export_role.sub_command(
        name="from_role",
        description="Créer un role à partir d'un role existant."
    )
    async def export_role_from_event(self, inter : disnake.ApplicationCommandInteraction,
                              role : disnake.Role = commands.Param(description="Le role depuis lequel exporter les members"),
                              name : str = commands.Param(description='Le nom du role à créer (default = "role.name copy")', default=None)):
        await inter.response.defer(ephemeral=True)
        if not name:
            name = f"{role.name} copy"
        
        
        selected_members = await memberSelection(inter, title="Export role from role", size = 4, message="Select members to export to the new role", timeout=300, pre_selected_members=role.members)    
        await inter.edit_original_message(embed=FastEmbed(description="\n".join(member.display_name for member in selected_members) if (selected_members and len(selected_members) > 0 )else "*Aucun membre sélectionné*"), view = None)
    
        

    
    @commands.slash_command(
        name="lock",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
        description="Verrouiller un channel vocal."
        )
    async def channel_lock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="Le channel vocal à verrouiller"),
                           raison : str = commands.Param(description='La raison du verrouillage à préciser aux spectateurs (défaut : "Focus")', default="Focus"),
                           parler : int = commands.Param(description="Est-ce que les spectateurs ont le droit de parler (défaut : non).", choices = {"Oui":1,"Non":0}, default = 0),
                           streamer : int = commands.Param(description="Est-ce que les spectateurs ont le droit de streamer (défaut : non).", choices= {"Oui":1,"Non":0}, default = 0)
        ):  
        await inter.response.defer(ephemeral=True)
        for chan in inter.guild.voice_channels:
            if chan.name == channel:  
                locked_channel = chan   
                break 
        if not locked_channel.permissions_for(inter.guild.default_role).speak:
            await inter.edit_original_message(embed=FastEmbed(description=f"Le channel vocal doit initialement permettre au role {inter.guild.default_role.mention} de parler."))
            return
        newLocker = Locker(inter, self, locked_channel,raison,timeout_on_no_participants=1, parler=bool(parler), streamer = bool(streamer))
        await newLocker.lock(inter)
        
            
    @channel_lock.autocomplete("channel")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        unlocked_channel = []
        for channel in inter.guild.voice_channels:
            if channel not in self.locked_channels:
                unlocked_channel.append(channel.name)
        return unlocked_channel    
    
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_update(self, member : disnake.Member, before : disnake.VoiceState, after : disnake.VoiceState):
        if self.incoming_connection(before, after):
            for locked_channel in self.locked_channels:
                if locked_channel == after.channel:
                    await locked_channel.incoming_connection(member)                
        if self.outgoing_connection(before, after):
            for locked_channel in self.locked_channels:
                if locked_channel == before.channel:
                    await locked_channel.outgoing_connection(member)    
    
    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        channels_dirty_name : List[disnake.VoiceChannel] = []
        for guild in self.bot.guilds:              
            for role in guild.roles:
                if role.name.endswith(Locker.role_name_authorized) or role.name.endswith(Locker.role_name_unauthorized):
                    await role.delete(reason=f"Cleaning old Locker")
                    logging.info(f'Role "{guild.name}:{role.name}" deleted by Locker cleaning')
                    channel_id : int = int(role.name.split(' ')[0])
                    channel = await self.bot.fetch_channel(channel_id)
                    if channel.name.startswith("🔒 ") and channel not in channels_dirty_name:
                        channels_dirty_name.append(channel)
        for channel in channels_dirty_name:
            await channel.edit(name=channel.name[2:], reason="Cleanning old Locker")
            logging.info(f'Channel "{guild.name}:{channel.name}" name cleaned to {channel.name[2:]} by Locker cleaning')
                   
                            
                            
            
        
    
                
                
            
def setup(bot):
    bot.add_cog(Server(bot))