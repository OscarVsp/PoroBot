import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, ChannelFlags, NotFound, UserCommandInteraction, VoiceChannel
from utils.FastEmbed import FastEmbed
from typing import List, Optional
from .view import Locker



class Server(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : commands.InteractionBot = bot
        self.locked_channels : List[Locker] = []
 
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
        name="lock",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
        description="Verrouiller un channel vocal."
        )
    async def channel_lock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="Le channel vocal à verrouiller"),
                           raison : str = commands.Param(description="La raison du verrouillage (Tournois, Tryhard, ...)", default="Non spécifié")
                           ):  
        await inter.response.defer(ephemeral=True)
        for chan in inter.guild.voice_channels:
            if chan.name == channel:  
                locked_channel = chan   
                break 
        if not locked_channel.permissions_for(inter.guild.default_role).speak:
            await inter.edit_original_message(embed=FastEmbed(description=f"Le channel vocal doit initialement permettre au role {inter.guild.default_role.mention} de parler."))
            return
        newLocker = Locker(inter,locked_channel,raison)
        self.locked_channels.append(newLocker)
        await newLocker.lock()
        await inter.edit_original_message(embed=newLocker.embed, view=newLocker)
        if not locked_channel.name.startswith("🔒 "):
            await locked_channel.edit(name="🔒 "+channel)
            
    @channel_lock.autocomplete("channel")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        unlocked_channel = []
        for channel in inter.guild.voice_channels:
            if channel not in self.locked_channels:
                unlocked_channel.append(channel.name)
        return unlocked_channel        
    
    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        for guild in self.bot.guilds:
            for role in guild.roles:
                if role.name.endswith("authorized"):
                    for channel in guild.voice_channels:
                        if channel.name in [role.name[:len(role.name)-11], role.name[:len(role.name)-13],"🔒 "+role.name[:len(role.name)-11],"🔒 "+role.name[:len(role.name)-13]]:
                            perm_everyone = disnake.PermissionOverwrite()
                            perm_everyone.speak = True
                            await channel.set_permissions(guild.default_role,overwrite=perm_everyone)
                            await role.delete(reason=f"Cleaning old Locker")
                            logging.info(f'Role "{guild.name}:{role.name}" deleted by Locker cleaning')
            
        
    
                
                
            
def setup(bot):
    bot.add_cog(Server(bot))