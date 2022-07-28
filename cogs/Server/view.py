import disnake 
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from disnake.ext import commands
from utils import data
import asyncio
from typing import List
import logging

class Locker(disnake.ui.View):
        
    def __init__(self, inter : ApplicationCommandInteraction, channel : disnake.VoiceChannel, reason : str):
        super().__init__(timeout=None)
        self.inter : ApplicationCommandInteraction = inter
        self.channel : disnake.VoiceChannel = channel
        self.guild : disnake.Guild = channel.guild
        self.channel_original_name : str = channel.name
        self.reason : str = reason
        self.authorized_role : disnake.Role = None
        self.unauthorized_role : disnake.Role = None
        
        self.mute.disabled = True
        self.unmute.disabled = False
        
    
    def __eq__(self,other):
        return self.channel == other
        
    def is_authorized(self, member : disnake.Member) -> bool:
        return self.authorized_role and self.authorized_role in member.roles
    
    def is_unauthorized(self, member : disnake.Member) -> bool:
        return self.unauthorized_role and self.unauthorized_role in member.roles
    
    def incoming_connection(self, before : disnake.VoiceState, after : disnake.VoiceState) -> bool:
        return (after.channel != None and before.channel != after.channel and after.channel == self.channel)
    
    def outcoming_connection(self, before : disnake.VoiceState, after : disnake.VoiceState) -> bool:
        return (before.channel != None and before.channel != after.channel and before.channel == self.channel)

       
    @property
    def embed(self) -> disnake.Embed:
        return FastEmbed(
            title = f"🔒 __Channel **#{self.channel_original_name}** verrouillé__",
            fields = [
                {
                    'name':"__**🔊 Participants :**__",
                    'value':"".join([p.mention for p in self.authorized_role.members]) if len(self.authorized_role.members) > 0 else "*Pas de participant*"
                },
                {
                    'name':"__**🔇 Spectateurs :**__",
                    'value':"".join([p.mention for p in self.unauthorized_role.members]) if len(self.unauthorized_role.members) > 0 else "*Pas de spectateur*"
                }
            ]
        ) 
        
    async def refresh_voice(self):
        for member in self.channel.members:
            if self.authorized_role not in member.roles:
                await member.move_to(self.channel)
                
    def refresh_presence(self):
        if len(self.unauthorized_role.members) > 0:
            self.authorize.options = [disnake.SelectOption(label=f"{member.display_name}", value=str(member.id)) for member in self.unauthorized_role.members]
            self.authorize.max_values = min(len(self.unauthorized_role.members),25)
            self.authorize.disabled = False
        else:
            self.authorize.disabled = True
            self.authorize.placeholder = "Aucun spectateur..."
        if len(self.authorized_role.members) > 0:
            self.unauthorize.options = [disnake.SelectOption(label=f"{member.display_name}", value=str(member.id)) for member in self.authorized_role.members]
            self.unauthorize.max_values = min(len(self.authorized_role.members),25)
            self.unauthorize.disabled = False
        else:
            self.unauthorize.disabled = True
            self.unauthorize.placeholder = "Aucun participant..."
            
        
        
    async def update(self, inter : disnake.MessageInteraction):
        await inter.edit_original_message(
                embed = self.embed,
                view = self
            ) 
          
    async def lock(self):
        self.authorized_role = await self.channel.guild.create_role(name=f"{self.channel_original_name} authorized",reason=f"Lock channel - {self.reason}")
        self.unauthorized_role = await self.channel.guild.create_role(name=f"{self.channel_original_name} unauthorized",reason=f"Lock channel - {self.reason}")
        for member in self.channel.members:
            await member.add_roles(self.authorized_role, reason=f"Lock channel - {self.reason}")
        perm = disnake.PermissionOverwrite()
        perm.speak = False
        await self.channel.set_permissions(self.unauthorized_role,overwrite=perm)
        perm.speak = True
        await self.channel.set_permissions(self.authorized_role,overwrite=perm)
        self.refresh_presence()
        logging.info(f"Channel {self.guild.name}#{self.channel_original_name} locked - {self.reason}")

    @disnake.ui.button(emoji = "🔊", label = "Mute", style=disnake.ButtonStyle.primary)
    async def mute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        perm = disnake.PermissionOverwrite()
        perm.speak = False
        await self.channel.set_permissions(self.unauthorized_role, overwrite=perm)
        await self.refresh_voice()
        self.mute.disabled = True
        self.unmute.disabled = False
        await self.update(interaction)
        
    @disnake.ui.button(emoji = "🔇", label = "Unmute", style=disnake.ButtonStyle.primary)
    async def unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        perm = disnake.PermissionOverwrite()
        perm.speak = True
        await self.channel.set_permissions(self.unauthorized_role, overwrite=perm)
        await self.refresh_voice()
        self.unmute.disabled = True
        self.mute.disabled = False
        await self.update(interaction)
        
    async def unlock(self):
        await self.unauthorized_role.delete(reason=f"Unlock channel - {self.reason}")
        await self.authorized_role.delete(reason=f"Unlock channel - {self.reason}")
        await self.refresh_voice()
        await self.inter.delete_original_message()
        self.stop()
        await self.channel.edit(name=self.channel_original_name)
        logging.info(f"Channel {self.guild.name}#{self.channel_original_name} unlocked")
        
    @disnake.ui.button(emoji = "🔓", label = "Unlock", style=disnake.ButtonStyle.danger)
    async def unlock_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        await self.unlock()
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="Restreindre un participant",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def unauthorize(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        for authorized_member in self.authorized_role.members:
            if str(authorized_member.id) in select.values:
                await authorized_member.add_roles(self.unauthorized_role, reason="Unauthorized")
                await authorized_member.remove_roles(self.authorized_role, reason="Unauthorized")
                await authorized_member.move_to(self.channel)
        await self.update(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="Restreindre un participant",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def authorize(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        for unauthorized_member in self.unauthorized_role.members:
            if str(unauthorized_member.id) in select.values:
                await unauthorized_member.add_roles(self.authorized_role, reason="Authorized")
                await unauthorized_member.remove_roles(self.unauthorized_role, reason="Authorized")
                await unauthorized_member.move_to(self.channel)
        await self.update(interaction)
                
   
                
          
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_update(self, member : disnake.Member, before : disnake.VoiceState, after : disnake.VoiceState):
        if self.incoming_connection(before, after):
            if member not in self.authorized_role.members and member not in self.unauthorized_role.members:
                await member.add_roles(self.unauthorized_role, reason = f"Lock channe l - {self.reason}")
                await member.move_to(self.channel)
                await member.send(embed=FastEmbed(
                        title="🔒 Channel vocal verrouillé",
                        description=f"Le channel vocal que tu viens de rejoindre est vérrouillé pour la raison suivante :\n\n**__{self.reason}__**\n\nCela veut dire que tu ne peux pas parler, mais tu peux toujours écouter les autres et regarder des streams."
                    ))
        if self.outcoming_connection(before, after):
            if len(self.channel.members) > 0:
                for member in self.channel.members:
                    if self.authorized_role in member.roles:
                        return
            await self.unlock()
            