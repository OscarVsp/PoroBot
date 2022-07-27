import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, ChannelFlags, NotFound, UserCommandInteraction
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
    
    @staticmethod
    def get_authorized_role(channel : disnake.VoiceChannel) -> Optional[disnake.Role]:
        return next((role for role in channel.guild.roles if role.name == f"{Server.original_name(channel)} authorized"), None)
            
    
    @commands.slash_command(
        name="clear",
        default_member_permissions=disnake.Permissions.all())
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
        await inter.response.defer(ephemeral=True)
        await inter.channel.purge(limit=nombre)
        await inter.edit_original_message(embed = FastEmbed(description = f":broom: {nombre} messages supprimés ! :broom:"))
        
        
    @clear.sub_command(
        name='category',
        description = "Supprimer channels d'une category"
    )
    async def clearCat(self, inter : ApplicationCommandInteraction,
        categorie : disnake.CategoryChannel = commands.Param(description = "Choisissez category à suppimer"),
        confirmation : disnake.CategoryChannel = commands.Param(description = "Confirmez la catégorie à suppimer"),
    ):
        await inter.response.defer(ephemeral=True)
        if categorie == confirmation:
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(embed=FastEmbed(description = f":broom: Catégorie {categorie.name} supprimé ! :broom:"))
            except NotFound:
                pass

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
        authorized_role = self.get_authorized_role(channel)
        await authorized_role.delete(reason="Unlock channel")
        for member in channel.members:
            if member.voice.suppress or member.voice.mute:
                await member.move_to(channel)
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
                
    @commands.user_command(name="Channel authorisé", default_member_permissions=disnake.Permissions.all())
    async def authorize_member(self, inter : UserCommandInteraction):
        await inter.response.defer(ephemeral=True)
        if inter.target.voice != None and inter.target.voice.channel != None:
            if self.is_locked(inter.target.voice.channel):
                if not self.is_authorized(inter.target, inter.target.voice.channel):
                    await inter.target.add_roles(self.get_authorized_role(inter.target.voice.channel), reason="Channel authorized UserCmd")
                    await inter.target.move_to(inter.target.voice.channel)
                    await inter.target.send(embed=FastEmbed(title="🔓 Autorisé", description="Tu as été autorisé à parler dans le channel vocal verrouillé dans lequel tu te trouve actuellement."))
                    await inter.edit_original_message(embed=FastEmbed(title="✅ Autorisé", description=f"{inter.target.display_name} a bien été authorisé à parler dans le channel verrouillé."))
                else:
                    await inter.edit_original_message(embed=FastEmbed(title="✅ Déjà autorisé", description=f"{inter.target.display_name} était déjà authorisé à parler dans le channel verrouillé."))
            else:
                await inter.edit_original_message(embed=FastEmbed(title="❌ Non verrouillé", description=f"Le channel vocal dans lequel se trouve {inter.target.display_name} n'est pas verrouillé."))
        else:
            await inter.edit_original_message(embed=FastEmbed(title="❌ Non connecté", description=f"{inter.target.display_name} n'est connecter dans aucun channel vocal actuellement."))
                
    
    @commands.user_command(name="Channel restreint", default_member_permissions=disnake.Permissions.all())
    async def unauthorize_member(self, inter : UserCommandInteraction):
        await inter.response.defer(ephemeral=True)
        if inter.target.voice != None and inter.target.voice.channel != None:
            if self.is_locked(inter.target.voice.channel):
                if self.is_authorized(inter.target, inter.target.voice.channel):
                    await inter.target.remove_roles(self.get_authorized_role(inter.target.voice.channel), reason="Channel authorized UserCmd")
                    await inter.target.move_to(inter.target.voice.channel)
                    await inter.target.send(embed=FastEmbed(title="🔒 Restreint", description="Tu as été restreint à ne pas pouvoir parler dans le channel vocal verrouillé dans lequel tu te trouve actuellement.\nJe te préviendrais quand celui-ci sera déverrouillé."))
                    await inter.edit_original_message(embed=FastEmbed(title="✅ Restreint", description=f"{inter.target.display_name} a bien été restreint à ne pas pouvoir parler dans le channel verrouillé."))
                else:
                    await inter.edit_original_message(embed=FastEmbed(title="✅ Déjà restreint", description=f"{inter.target.display_name} était déjà restreint à na pas pouvoir parler dans le channel verrouillé."))
            else:
                await inter.edit_original_message(embed=FastEmbed(title="❌ Non verrouillé", description=f"Le channel vocal dans lequel se trouve {inter.target.display_name} n'est pas verrouillé."))
        else:
            await inter.edit_original_message(embed=FastEmbed(title="❌ Non connecté", description=f"{inter.target.display_name} n'est connecter dans aucun channel vocal actuellement."))
            
                
            
def setup(bot):
    bot.add_cog(Server(bot))