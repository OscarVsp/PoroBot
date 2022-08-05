import disnake 
from disnake.ext import commands
from disnake.ext import commands
import modules.FastSnake as FS
import asyncio
from typing import List
import logging

class Locker(disnake.ui.View):
    
    role_name_authorized : str = "LockerAuthorized"
    role_name_unauthorized : str = "LockerUnauthorized"
        
    help_fields : List[dict] = [
        {
            'name':'__**Fonctionnement :**__',
            'value':"Verrouiller un channel vocal permet aux __**particpants**__ *(personnes présentes au moment du vérrouillage)* de rester focus, en empêchant les __**spectateurs**__ *(nouveaux arrivants)* de **parler** / **streamer**.",
        },
        {  
            'name':"__**Commandes :**__",
            'value':"""🔈/🔇 **(Un)mute** : Temporairement autoriser les spectateurs à **parler** / **streamer**
            🚫 **Restreindre** : Restreindre des participants *(deviennent des spectateurs)*
            ✅ **Autoriser** : Autoriser des spectateurs *(deviennent des participants).
            🔓 **Déverrouiller** : Arrêter le verrouillage du channel vocal.
            ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖"""
        }
    ]
    
    
        
    def __init__(self,
                 inter : disnake.ApplicationCommandInteraction,
                 server : commands.Cog,
                 channel : disnake.VoiceChannel,
                 reason : str,
                 timeout_on_no_participants : int = 1,
                 parler : bool = False,
                 streamer : bool = False
        ):
        super().__init__(timeout=None)
        self.server : commands.Cog = server
        self.channel : disnake.VoiceChannel = channel
        self.guild : disnake.Guild = inter.guild
        self.channel_original_name : str = channel.name
        self.reason : str = reason
        self.author : disnake.Member = inter.author
        self.inter : disnake.Interaction = None
        self.authorized_role : disnake.Role = None
        self.unauthorized_role : disnake.Role = None
        
        self.help_field_state : bool = False
        
        self.muted_perm = disnake.PermissionOverwrite()
        self.muted_perm.speak = parler
        self.muted_perm.stream = streamer
        
        self.unmuted_perm = disnake.PermissionOverwrite()
        self.unmuted_perm.speak = None
        self.unmuted_perm.stream = None
        
        self.authorized_perm = disnake.PermissionOverwrite()
        self.authorized_perm.speak = True
        self.authorized_perm.stream = True
        
        self.timeout_delay : int = timeout_on_no_participants*60
        self.unlock_timeout = False
        
        self.mute.disabled = True
        self.unmute.disabled = False
        
    
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
        if self.help_field_state:
            fields = Locker.help_fields.copy()
        else:
            fields = []
        participants : List[str] = [p.mention for p in self.authorized_role.members if p in self.channel.members]
        spectateurs : List[str]= [s.mention for s in self.unauthorized_role.members if s in self.channel.members]
        fields.append({
                    'name':"🔊 __**Participants :**__",
                    'value':"\n".join(participants) if len(participants) > 0 else "*Pas de participant*"
                })
        fields.append({
                    'name':("🔇" if self.mute.disabled else "🔈")+" __**Spectateurs :**__",
                    'value':"\n".join(spectateurs) if len(spectateurs) > 0 else "*Pas de spectateur*"
                })
        return FS.Embed(
            title = self.title,
            description="➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖",
            fields = fields,
            color = disnake.Colour.green()
        )
        
    @property
    def notification_embed(self) -> disnake.Embed:
        description = f"Le channel vocal que tu viens de rejoindre a été verrouillé par {self.author.display_name} pour la raison suivante :\n\n**__{self.reason}__**\n\nCela veut dire que tu ne peux pas parler ni streamer, mais tu peux toujours écouter les autres et regarder des streams"
        for member in self.channel.members:
            if self.is_authorized(member):
                if member.activity and member.activity.type == disnake.ActivityType.streaming:
                    description+=f"\n\n**{member.display_name}** est actuellement en train de stream sur [{member.activity.platform}]({member.activity.url})"
        FS.Embed(
            title=self.title,
            description=description
        )
        
    async def lock(self, inter : disnake.CommandInteraction):
        self.authorized_role = await self.channel.guild.create_role(name=f"{self.channel.id} {Locker.role_name_authorized}",reason=f"Lock channel - {self.reason}")
        self.unauthorized_role = await self.channel.guild.create_role(name=f"{self.channel.id} {Locker.role_name_unauthorized}",reason=f"Lock channel - {self.reason}")
        await inter.author.add_roles(self.authorized_role, reason=f"Lock channel - {self.reason}")
        for member in self.channel.members:
            await member.add_roles(self.authorized_role, reason=f"Lock channel - {self.reason}")
        await self.channel.set_permissions(self.unauthorized_role,overwrite=self.muted_perm)
        await self.channel.set_permissions(self.authorized_role,overwrite=self.authorized_perm)
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
                timeout_counter = 0
                while timeout_counter < self.timeout_delay:
                    await asyncio.sleep(1)
                    for member in self.channel.members:
                        if self.authorized_role in member.roles:
                            self.unlock_timeout = False
                            return
                        timeout_counter += 1
                await self.unlock()
        else:
            await self.unlock()
            
    async def unlock(self, inter : disnake.MessageInteraction = None):
        await inter.edit_original_message(
            embed = FS.Embed(
                title = f"🔓 __**Channel** *#{self.channel_original_name}* **verrouillé**__",
                description="Déverrouillage en cours... ⌛"
            ), view = None)
        self.stop()
        self.server.locked_channels.remove(self)
        members_to_notify = [s for s in self.channel.members if self.unauthorized_role in s.roles]
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
        for member in members_to_notify:
            await member.send(embed=FS.Embed(
                title=f"🔓 __**Channel** *#{self.channel_original_name}* **déverrouillé**__",
                description=f"Le channel vocal dans lequel tu te trouve vient d'être __**définitivement**__ déverrouillé.\nTu peux maintenant te __**dé-mute**__ pour parler !"
            ))
        await self.channel.edit(name=self.channel_original_name)
        logging.info(f"Channel {self.guild.name}#{self.channel_original_name} unlocked")
        
    @disnake.ui.button(emoji = "🔇", label = "Mute", style=disnake.ButtonStyle.primary)
    async def mute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.channel.set_permissions(self.unauthorized_role, overwrite=self.muted_perm)
        await self.refresh_voice()
        self.mute.disabled = True
        self.unmute.disabled = False
        self.unlock_state = False
        await self.update(interaction)
        
    @disnake.ui.button(emoji = "🔈", label = "Unmute", style=disnake.ButtonStyle.primary)
    async def unmute(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await self.channel.set_permissions(self.unauthorized_role, overwrite=self.unmuted_perm)
        self.unmute.disabled = True
        self.mute.disabled = False
        self.unlock_state = False
        await self.update(interaction)
        for member in self.channel.members:
            if self.unauthorized_role in member.roles:
                await member.send(embed=FS.Embed(
                    title=f"🔈 __**Channel** *#{self.channel_original_name}* **déverrouillé**__",
                    description="Le channel vocal dans lequel tu trouver vient d'être __**temporairement**__ déverrouillé.\nTu peux te __**dé-mute**__ pour parler !"
                ))
        
    @disnake.ui.button(emoji = "ℹ️", label = "Voir l'aide", style=disnake.ButtonStyle.green)
    async def info(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.help_field_state = not self.help_field_state
        if self.help_field_state:
            self.info.label = "Cacher l'aide"
        else:
            self.info.label = "Voir l'aide"
        self.unlock_state = False
        await self.update(interaction)
        
    @disnake.ui.button(emoji = "🔓", label = "Déverrouiller", style=disnake.ButtonStyle.danger)
    async def unlock_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if (await FS.confirmation(interaction, 
                               title=f"🔓 __**Déverrouiller le channel *{self.channel.name}***__", 
                               message=f"Es-tu sûr de vouloir déverrouiller le channel {self.channel.mention} ?")):
            await self.unlock(interaction)
        else:
            await self.update()
        
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
        self.unlock_state = False
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
        self.unlock_state = False
        await self.update(interaction)
                
 

                