import disnake 
from disnake.ext import commands
import modules.FastSnake as FS
import asyncio
from typing import List
import logging

from modules.FastSnake.Views import confirmation

class Locker(disnake.ui.View):
    
    role_name_authorized : str = "LockerAuthorized"
    role_name_unauthorized : str = "LockerUnauthorized"
            
        
    def __init__(self,
                 inter : disnake.ApplicationCommandInteraction,
                 server : commands.Cog,
                 channel : disnake.VoiceChannel,
                 reason : str,
                 timeout_on_no_participants : int = 1
        ):
        super().__init__(timeout=None)
        self.server : commands.Cog = server
        self.channel : disnake.VoiceChannel = channel
        self.guild : disnake.Guild = inter.guild
        self.channel_original_name : str = channel.name
        self.reason : str = reason
        self.author : disnake.Member = inter.author
        self.inter : disnake.Interaction = inter
        self.authorized_role : disnake.Role = None
        self.unauthorized_role : disnake.Role = None
        
        self.timeout_delay : int = timeout_on_no_participants*60
        self.unlock_timeout = False
        
        self.speak_perm : bool = False
        self.stream_perm : bool = False
        
        
    
    def __eq__(self,other):
        return self.channel == other
        
    def is_authorized(self, member : disnake.Member) -> bool:
        return self.authorized_role and self.authorized_role in member.roles
    
    def is_unauthorized(self, member : disnake.Member) -> bool:
        return self.unauthorized_role and self.unauthorized_role in member.roles
    
    @property
    def title(self) -> str:
        return f"🔒 __**Channel** *#{self.channel_original_name}* **verrouillé**__"
       
    @property
    def embed(self) -> disnake.Embed:
        participants : List[str] = [p.mention for p in self.authorized_role.members if p in self.channel.members]
        spectateurs : List[str]= [s.mention for s in self.unauthorized_role.members if s in self.channel.members]
        return FS.Embed(
            title = self.title,
            description="➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖",
            fields = [
                {
                    'name':"🎭 __**Participants :**__",
                    'value':"\n".join(participants) if len(participants) > 0 else "*Pas de participant*"
                },
                {
                    'name':"👀 __**Spectateurs :**__",
                    'value':"\n".join(spectateurs) if len(spectateurs) > 0 else "*Pas de spectateur*"
                }         
            ],
            color = disnake.Colour.green()
        )
        
    @property
    def unauthorized_perm(self) -> disnake.PermissionOverwrite:
        perm = disnake.PermissionOverwrite()
        perm.speak = self.speak_perm
        perm.stream = self.stream_perm
        return perm
        
    @property
    def notification_embed(self) -> disnake.Embed:
        description = f"Le channel vocal que tu viens de rejoindre a été verrouillé par {self.author.display_name} pour la raison suivante :\n\n***{self.reason}***\n\nCela veut dire que tu ne peux pas parler ni streamer, mais tu peux toujours écouter les autres et regarder des streams.\n⚠️ Tu seras automatiquement dé-mute lorsque le channel sera déverrouillé ! "
        for member in self.channel.members:
            if self.is_authorized(member):
                if member.activity and member.activity.type == disnake.ActivityType.streaming:
                    description+=f"\n\n**{member.display_name}** est actuellement en train de stream sur [{member.activity.platform}]({member.activity.url})"
        return FS.Embed(
            title=self.title,
            description=description
        )
        
    async def lock(self, inter : disnake.CommandInteraction):
        authorized_perm = disnake.PermissionOverwrite()
        authorized_perm.speak = True
        authorized_perm.stream = True
        unauthorized_perm = disnake.PermissionOverwrite()
        unauthorized_perm.speak = False
        unauthorized_perm.stream = False
        self.authorized_role = await self.channel.guild.create_role(name=f"{self.channel.id} {Locker.role_name_authorized}",reason=f"Lock channel - {self.reason}")
        self.unauthorized_role = await self.channel.guild.create_role(name=f"{self.channel.id} {Locker.role_name_unauthorized}",reason=f"Lock channel - {self.reason}")
        await inter.author.add_roles(self.authorized_role, reason=f"Lock channel - {self.reason}")
        for member in self.channel.members:
            await member.add_roles(self.authorized_role, reason=f"Lock channel - {self.reason}")
        await self.channel.set_permissions(self.unauthorized_role,overwrite=unauthorized_perm)
        await self.channel.set_permissions(self.authorized_role,overwrite=authorized_perm)
        self.refresh_presence()
        await inter.edit_original_message(embed=self.embed, view=self)
        self.inter = inter
        self.server.locked_channels.append(self)
        if not self.channel.name.startswith("🔒 "):
            await self.channel.edit(name="🔒 "+self.channel.name)
        logging.info(f"Channel {self.guild.name}#{self.channel_original_name} locked - {self.reason}")
                
    def refresh_presence(self):
        if len(self.unauthorized_role.members) > 0:
            self.authorize.options = [disnake.SelectOption(label=f"{member.display_name}", value=str(member.id)) for member in self.unauthorized_role.members]
            if len(self.authorize.options) > 25:
                self.authorize.options = self.authorize.options[:25]
            self.authorize.max_values = len(self.unauthorized_role.members)
            self.authorize.disabled = False
        else:
            self.authorize.disabled = True
        if len(self.authorized_role.members) > 0:
            self.unauthorize.options = [disnake.SelectOption(label=f"{member.display_name}", value=str(member.id)) for member in self.authorized_role.members]
            if len(self.unauthorize.options) > 25:
                self.unauthorize.options = self.unauthorize.options[:25]
            self.unauthorize.max_values = len(self.authorized_role.members)
            self.unauthorize.disabled = False
        else:
            self.unauthorize.disabled = True
            
    async def refresh_voice(self):
        for member in self.channel.members:
            if self.authorized_role not in member.roles:
                await member.move_to(self.channel)
                
            
    async def update(self, inter : disnake.MessageInteraction = None):
        if inter == None:
            await self.inter.edit_original_message(
                embed = self.embed,
                view = self
            )
        elif inter.response.is_done():
            await inter.edit_original_message(
                embed = self.embed,
                view = self
            ) 
        else:
            await inter.response.edit_message(
                embed = self.embed,
                view = self
            ) 
        
    async def incoming_connection(self, member : disnake.Member):
        if member not in self.authorized_role.members and member not in self.unauthorized_role.members:
            await member.add_roles(self.unauthorized_role, reason = f"Lock channel - {self.reason}")
            await member.move_to(self.channel)
            await member.send(embed=self.notification_embed)
        self.refresh_presence()
        await self.update()
        
    async def outgoing_connection(self, member : disnake.Member):
        if len(self.channel.members) > 0:
            self.refresh_presence()
            await self.update()
            for member in self.channel.members:
                if self.authorized_role in member.roles:
                    return
            if self.unlock_timeout == False:
                self.unlock_timeout = True
                logging.info("Start timeout for channel lock")
                timeout_counter = 0
                while timeout_counter < self.timeout_delay:
                    await asyncio.sleep(1)
                    for member in self.channel.members:
                        if self.authorized_role in member.roles:
                            self.unlock_timeout = False
                            logging.info("Interrupt timeout for channel lock")
                            return
                        timeout_counter += 1
                logging.info("Passed timeout for channel lock")
                await self.unlock()
        else:
            await self.unlock()
            
    async def unlock(self, inter : disnake.MessageInteraction = None):
        if inter == None:
            inter = self.inter
        await inter.edit_original_message(
            embed = FS.Embed(
                title = f"🔓 __**Channel** *#{self.channel_original_name}* **verrouillé**__",
                description="Déverrouillage en cours... ⌛"
            ), view = None)
        self.stop()
        self.server.locked_channels.remove(self)
        await self.unauthorized_role.delete(reason=f"Unlock channel - {self.reason}")
        await self.authorized_role.delete(reason=f"Unlock channel - {self.reason}")
        if inter == None:
            inter = self.inter
        await inter.edit_original_message(
            embed = FS.Embed(
                title = f"🔓 __**Channel** *#{self.channel_original_name}* **déverrouillé**__",
                description="Le channel à bien été __**déverrouillé**__ !",
                footer_text="Tu peux rejeter ce message pour le faire disparaitre."
            )) 
        await self.refresh_voice()
        await self.channel.edit(name=self.channel_original_name)
        logging.info(f"Channel {self.guild.name}#{self.channel_original_name} unlocked")
        
    @disnake.ui.button(emoji = "🔈", label = "Autoriser la parole", style=disnake.ButtonStyle.primary)
    async def mute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.speak_perm = not self.speak_perm
        await self.channel.set_permissions(self.unauthorized_role, overwrite=self.unauthorized_perm)
        if self.speak_perm:
            button.label = "Interdir la parole"
            button.style = disnake.ButtonStyle.grey
            button.emoji = "🔇"
        else:
            button.label = "Autoriser la parole"
            button.style = disnake.ButtonStyle.primary
            button.emoji = "🔈"
        await self.update(interaction)
        await self.refresh_voice()
            
 
            
        
    @disnake.ui.button(emoji = "📺", label = "Autoriser les streams", style=disnake.ButtonStyle.primary)
    async def stream(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stream_perm = not self.stream_perm
        await self.channel.set_permissions(self.unauthorized_role, overwrite=self.unauthorized_perm)
        if self.stream_perm:
            button.label = "Interdit les streams"
            button.style = disnake.ButtonStyle.gray
        else:
            button.label = "Autoriser les streams"
            button.style = disnake.ButtonStyle.primary
        await self.update(interaction)

            
      
        
    @disnake.ui.button(emoji = "🔓", label = "Déverrouiller", style=disnake.ButtonStyle.danger)
    async def unlock_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        confirm = await confirmation(target=interaction,embeds=[self.embed])
        if confirm:
            await self.unlock()
        else:
            await self.update(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="🚫 Restreindre des participants",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def unauthorize(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for authorized_member in self.authorized_role.members:
            if str(authorized_member.id) in select.values:
                await authorized_member.add_roles(self.unauthorized_role, reason="Unauthorized")
                await authorized_member.remove_roles(self.authorized_role, reason="Unauthorized")
                if authorized_member.voice and authorized_member.voice.channel == self.channel:
                    await authorized_member.move_to(self.channel)
        self.refresh_presence()
        await self.update(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="✅ Autoriser des spectateurs",options= [
                                disnake.SelectOption(label = "placeholder",value="1")
                            ])
    async def authorize(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        for unauthorized_member in self.unauthorized_role.members:
            if str(unauthorized_member.id) in select.values:
                await unauthorized_member.add_roles(self.authorized_role, reason="Authorized")
                await unauthorized_member.remove_roles(self.unauthorized_role, reason="Authorized")
                if unauthorized_member.voice and unauthorized_member.voice.channel == self.channel:
                    await unauthorized_member.move_to(self.channel)
        
        self.refresh_presence()
        await self.update(interaction)
                
 

                