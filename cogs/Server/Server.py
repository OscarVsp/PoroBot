import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, ChannelFlags
from utils.FastEmbed import FastEmbed
from typing import List, Optional



class Server(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot
        self.reason : dict = {}
    
    def get_channel_by_name(self, channel_name : str, guild : disnake.Guild) -> Optional[disnake.VoiceChannel]:
        for channel in guild.voice_channels:
            if channel.name == channel_name:
                return channel
        return None 
    
    @staticmethod
    def original_name(channel : disnake.VoiceChannel) -> str:
        name = channel.name
        while name.startswith("🔒 "):
            name = name[2:]
        return name
    
    @staticmethod
    def is_locked(channel : disnake.VoiceChannel) -> bool:
        for role in channel.guild.roles:
            if role.name == f"{Server.original_name(channel)} authorized":
                return True
        return False
    
    @staticmethod
    def is_authorized(member : disnake.Member, channel : disnake.VoiceChannel) -> bool:
        for role in member.roles:
            if role.name == f"{Server.original_name(channel)} authorized":
                return True
        return False
            
    
    @commands.slash_command(
        description = "Supprimer les derniers messages du channel",
        default_member_permissions=disnake.Permissions.all()
    )
    async def clear(self, inter : ApplicationCommandInteraction,
        nombre : int = commands.Param(
            description = "le nombre de message à supprimer",
            gt = 0
        )
    ):
        await inter.response.defer()
        await inter.channel.purge(limit=nombre)
        await inter.channel.send(
            embed = FastEmbed(
                description = f":broom: {nombre} messages supprimés ! :broom:"),
            delete_after=3)
    

    @commands.slash_command(
        name="channel",     
        default_member_permissions=disnake.Permissions.all()
    )
    async def channel(self, inter : ApplicationCommandInteraction):
        pass
    
    async def lock(self, channel : disnake.VoiceChannel, raison : str):
        authorized_role = await channel.guild.create_role(name=f"{self.original_name(channel)} authorized",reason="Unlock channel")
        for member in channel.members:
            await member.add_roles(authorized_role, reason="Unlock channel")
        everyone = channel.guild.default_role
        perm_everyone = disnake.PermissionOverwrite()
        perm_everyone.speak = False
        await channel.set_permissions(everyone,overwrite=perm_everyone)
        perm_authorized = disnake.PermissionOverwrite()
        perm_authorized.speak = True
        await channel.set_permissions(authorized_role,overwrite=perm_authorized)
        self.reason[f"{channel.guild.name}#{channel.name}"] = raison
        logging.info(f"Channel {channel.guild.name}#{channel.name} locked")
    
    @channel.sub_command(
        name="lock",
        description="Verrouiller un channel vocal (mute automatiquement les nouveaux arrivant)."
        )
    async def channel_lock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="Le channel vocal à verrouillé"),
                           raison : str = commands.Param(description="La raison du verrouillage (Tournois, Tryhard, ...)", default="Non spécifié")
                           ):  
        await inter.response.defer(ephemeral=True)          
        locked_channel : disnake.VoiceChannel = self.get_channel_by_name(channel, inter.guild)
        if len(locked_channel.members) == 0:
            await inter.edit_original_message(embed=FastEmbed(description=f"Il n'y a personne actuellement connecté dans le channel {locked_channel.name}.\nIl faut au moins une personne pour pouvoir verrouillé le channel."))
        else:
            await self.lock(locked_channel, raison)
            await inter.edit_original_message(embed=FastEmbed(description=f"Channel {locked_channel.name} verrouillé !"))
            if not locked_channel.name.startswith("🔒 "):
                await locked_channel.edit(name="🔒 "+self.original_name(locked_channel))
            
    @channel_lock.autocomplete("channel")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        unlocked_channel = []
        for channel in inter.guild.voice_channels:
            if not self.is_locked(channel):
                unlocked_channel.append(channel.name)
        return unlocked_channel
    
    async def unlock(self, channel : disnake.VoiceChannel):
        everyone = channel.guild.default_role
        perm_everyone = disnake.PermissionOverwrite()
        perm_everyone.speak = True
        await channel.set_permissions(everyone,overwrite=perm_everyone)
        authorized_role = next((role for role in channel.guild.roles if role.name == f"{self.original_name(channel)} authorized"), None)
        await authorized_role.delete(reason="Unlock channel")
        for member in channel.members:
            if member.voice.suppress or member.voice.mute:
                await member.edit(mute=False)           #TODO check if dangerous to automatically unmute ?
                await member.send(embed=FastEmbed(
                    title="🔓 Channel vocal déverrouillé",
                    description="Le channel vocal dans lequel tu te trouves vient d'être déverrouillé !\n\nTu peux à nouveau parler normalement."      
                ))   
        self.reason.pop(f"{channel.guild.name}#{channel.name}",None)
        logging.info(f"Channel {channel.guild.name}#{self.original_name(channel)} unlocked")
     
    @channel.sub_command(
        name="unlock",
        description="Déverrouiller le channel vocal verrouillé"
        )
    async def channel_unlock(self, inter : ApplicationCommandInteraction,
                             channel : str = commands.Param(description="Le channel vocal à déverrouillé")
                             ):
        await inter.response.defer(ephemeral=True)
        locked_channel : disnake.VoiceChannel = self.get_channel_by_name(channel, inter.guild)
        await self.unlock(locked_channel)
        await inter.edit_original_message(embed=FastEmbed(description=f"Channel {self.original_name(locked_channel)} déverrouillé !")) 
        if locked_channel.name.startswith("🔒 "):
            await locked_channel.edit(name=self.original_name(locked_channel))
    
    @channel_unlock.autocomplete("channel")
    async def autocomp_unlocked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        locked_channel = []
        for channel in inter.guild.voice_channels:
            if self.is_locked(channel):
                locked_channel.append(channel.name)
        return locked_channel    
    
    async def on_connect_to_locked_channel(self, member : disnake.Member, channel : disnake.VoiceChannel):
        if not self.is_authorized(member, channel):
            raison = self.reason.get(f"{channel.guild.name}#{channel.name}", None)
            if raison != None:
                await member.send(embed=FastEmbed(
                        title="🔒 Channel vocal verrouillé",
                        description=f"Le channel vocal que tu viens de rejoindre est vérrouillé pour la raison suivante :\n\n**__{raison}__**\n\nCela veut dire que tu ne peux pas parler, mais tu peux toujours écouter les autres et regarder des streams.\n\nJe te previendrais quand le channel sera déverrouillé."
                    ))  
            else:
                await member.send(embed=FastEmbed(
                        title="🔒 Channel vocal verrouillé",
                        description="Le channel vocal que tu viens de rejoindre est vérrouillé.\n\nCela veut dire que tu ne peux pas parler, mais tu peux toujours écouter les autres et regarder des streams.\n\nJe te previendrais quand le channel sera déverrouillé."
                    ))  
        
    async def on_disconnect_from_locked_channel(self, channel : disnake.VoiceChannel):
        for member in channel.members:
            if self.is_authorized(member, channel):
                return
        await self.unlock(channel)
        if channel.name.startswith("🔒 "):
            await channel.edit(name=self.original_name(channel))
    
    
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_update(self, member : disnake.Member, before : disnake.VoiceState, after : disnake.VoiceState):
        if after != None and after.channel != None:
            if (before == None or before.channel == None or before.channel != after.channel):
                if self.is_locked(after.channel):
                    await self.on_connect_to_locked_channel(member, after.channel)
        if before != None and before.channel != None:
            if self.is_locked(before.channel):
                await self.on_disconnect_from_locked_channel(before.channel)
                
            
def setup(bot):
    bot.add_cog(Server(bot))