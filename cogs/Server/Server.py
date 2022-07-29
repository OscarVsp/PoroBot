import logging
from pydoc import describe
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, NotFound
from utils.FastEmbed import FastEmbed
from typing import List, Optional

from utils.view import confirmation
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
        name="test"
    )
    async def test(self, inter : ApplicationCommandInteraction):
        await inter.response.defer(ephemeral = True)
        if (await confirmation(inter.author)):
            await inter.edit_original_message(embed=FastEmbed(description="Confirmed !"))
 
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
        if await confirmation(inter):
            await inter.channel.purge(limit=nombre)
            await inter.edit_original_message(embed = FastEmbed(description = f":broom: {nombre} messages supprimés ! :broom:", color=color.vert))
        
        
    @clear.sub_command(
        name='category',
        description = "Supprimer channels d'une category"
    )
    async def clearCat(self, inter : ApplicationCommandInteraction,
        categorie : disnake.CategoryChannel = commands.Param(description = "Choisissez category à suppimer")
    ):
        if await confirmation(inter):
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(embed=FastEmbed(description = f":broom: **Catégorie** *{categorie.name}* **supprimée** ! :broom:", color=color.vert))
            except NotFound:
                    pass
            

    @commands.slash_command(
        name="lock",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
        description="Verrouiller un channel vocal."
        )
    async def channel_lock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="Le channel vocal à verrouiller"),
                           raison : str = commands.Param(description='La raison du verrouillage à préciser aux spectateurs (défaut : "Focus")', default="Focus"),
                           parler : int = commands.Param(description="Est-ce que les spectateurs on le droit de parler (défaut : non).", choices = {"Oui":1,"Non":0}, default = 0),
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