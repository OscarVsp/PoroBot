from enum import Enum
import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, NotFound
from typing import List, Union
import modules.FastSnake as FS
from modules.FastSnake.ConfirmationView import ConfirmationReturnData
from modules.FastSnake.ShadowMember import MISSING
from modules.FastSnake.Views import confirmation
from .view import Locker
from deep_translator import GoogleTranslator

class ColorEnum(disnake.Colour, Enum):
    Blue = disnake.Colour.blue().value,
    Blurple = disnake.Colour.blurple().value,
    Brand_green = disnake.Colour.brand_green().value,
    Brand_red = disnake.Colour.brand_red().value,
    Dark_blue = disnake.Colour.dark_blue().value,
    Dark_gold = disnake.Colour.dark_gold().value,
    Dark_green = disnake.Colour.dark_green().value,
    Dark_magenta = disnake.Colour.dark_magenta().value,
    Dark_orange = disnake.Colour.dark_orange().value,
    Dark_purple = disnake.Colour.dark_purple().value,
    Dark_red = disnake.Colour.dark_red().value,
    Dark_teal = disnake.Colour.dark_teal().value,
    Dark_theme = disnake.Colour.dark_theme().value,
    Fuchsia = disnake.Colour.fuchsia().value,
    Gold = disnake.Colour.gold().value,
    Green = disnake.Colour.green().value,
    Lighter_gray = disnake.Colour.lighter_gray().value,
    Magenta = disnake.Colour.magenta().value,
    Og_blurple = disnake.Colour.og_blurple().value,
    Orange = disnake.Colour.orange().value,
    Purple = disnake.Colour.purple().value,
    Random = disnake.Colour.random().value,
    Red = disnake.Colour.red().value,
    Teal = disnake.Colour.teal().value,
    Yellow = disnake.Colour.yellow().value


class Server(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : commands.InteractionBot = bot
        self.locked_channels : List[Locker] = []
        self.translator = GoogleTranslator(source = "auto", target = "en")
        
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
        confirm : ConfirmationReturnData = await FS.confirmation(inter,
                               title=f"__**Suppression de {nombre} message(s)**__",
                               message=f"Êtes-vous sûr de vouloir supprimer les {nombre} dernier(s) message(s) de ce channel ?\nCette action est irréversible !",
                               timeout=30)
        if confirm:
            await inter.edit_original_message(embed=FS.Embed(description = f"Suppression de {nombre} message(s) en cours... ⌛", color=disnake.Colour.green()), view=None)
            await inter.channel.purge(limit=nombre)
            await inter.edit_original_message(embed = FS.Embed(description = f":broom: {nombre} messages supprimés ! :broom:", color=disnake.Colour.green()))
        elif confirm.is_cancelled:
            await inter.edit_original_message(embed = FS.Embed(description = f":o: Suppresion de {nombre} message(s) annulée", color=disnake.Colour.dark_grey()), view = None)
        else:
            await inter.edit_original_message(embed = FS.Embed(description = f":o: Suppresion de {nombre} message(s) timeout", color=disnake.Colour.dark_grey()), view = None)
        
    @clear.sub_command(
        name='category',
        description = "Supprimer une categorie"
    )
    async def clearCat(self, inter : ApplicationCommandInteraction,
        categorie : disnake.CategoryChannel = commands.Param(description = "Choisissez categorie à suppimer")
    ):

        if await FS.confirmation(inter,
                              title=f"__**Suppression de la categorie *{categorie.name}***__",
                              message=f"Êtes-vous sûr de vouloir supprimer la catégorie ***{categorie.mention}*** ?\nCela supprimera également les {len(categorie.channels)} channels contenus dans celle-ci :\n"+"\n".join(channel.mention for channel in categorie.channels)+"\nCette action est irréversible !"):
            await inter.edit_original_message(embed=FS.Embed(description = f"Suppression de la catégorie *{categorie.name}* en cours... ⌛", color=disnake.Colour.green()), view=None)
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(embed=FS.Embed(description = f":broom: **Catégorie** *{categorie.name}* **supprimée** ! :broom:", color=disnake.Colour.green()))
            except NotFound:
                    pass
        else:
            await inter.edit_original_message(embed=FS.Embed(description = f":o: Suppression de la catégorie {categorie.mention} annulée !", color=disnake.Colour.green()), view = None)
          
          
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
        
        selected_members : List[disnake.Member] = await FS.memberSelection(inter, title="Export role from event", message="Select members below", timeout=300, pre_selection=event_members)    
        await inter.edit_original_message(embed=FS.Embed(description="\n".join(member.display_name for member in selected_members) if len(selected_members) > 0 else "*Aucun membre sélectionné*"), view = None)
    
        
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
        
        
        selected_members : List[disnake.Member] = await FS.memberSelection(inter, title="Export role from role", size = 4, message="Select members to export to the new role", timeout=300, pre_selection=role.members)    
        await inter.edit_original_message(embed=FS.Embed(description="\n".join(member.display_name for member in selected_members) if (selected_members and len(selected_members) > 0 )else "*Aucun membre sélectionné*"), view = None)
    
    @commands.slash_command(
        name="embed",
        description="Envoyer un embed",
        dm_permission=False,
        default_member_permissions=disnake.Permissions.all()
    )
    async def embed(self, inter : ApplicationCommandInteraction):
        pass    
        
    @embed.sub_command(
        name="guild",
        description="Envoyer un embed dans un channel d'un server"
    )
    async def embed_guild(self, inter : ApplicationCommandInteraction,
                    channel : disnake.TextChannel = commands.Param(description="The channel where to send the embed (default : here)", default = None),
                    titre : str = commands.Param(description="Le titre", default = disnake.Embed.Empty),
                    contenu : str = commands.Param(description="Le contenu", default = disnake.Embed.Empty),
                    mention : Union[disnake.Role, disnake.Member] = commands.Param(description="Un role ou un membre à mentionner", default=None),
                    color : ColorEnum = commands.Param(description="La couleur", default=None),
                    url : str = commands.Param(description="L'url", default=disnake.Embed.Empty),
                    thumbnail_url : str = commands.Param(description="L'url du thumbnail", default=disnake.Embed.Empty),
                    thumbnail_file : disnake.Attachment = commands.Param(description="Le fichier du thumbnail", default=None),
                    image_url : str = commands.Param(description="L'url de l'image", default=disnake.Embed.Empty),
                    image_file : disnake.Attachment = commands.Param(description="Le fichier de l'image", default=None),
                    author_name : str = commands.Param(description="Le nom de l'auteur (defaut : ton nom)", default = None),
                    author_icon_url : str = commands.Param(description="L'icon de l'auteur", default=disnake.Embed.Empty),
                    footer_text : str = commands.Param(description="Le text du footer", default=disnake.Embed.Empty),
                    footer_icon_url : str = commands.Param(description="L'url de l'icon du footer", default = disnake.Embed.Empty)):
        await inter.response.defer(ephemeral=True)
        if (
            titre != disnake.Embed.Empty 
            or contenu != disnake.Embed.Empty 
            or thumbnail_file != None 
            or thumbnail_url != disnake.Embed.Empty 
            or image_file != None 
            or image_url != disnake.Embed.Empty
            or author_name != disnake.Embed.Empty
            or author_icon_url != disnake.Embed.Empty):
            if not channel:
                channel = inter.channel
            embed = FS.Embed(
                    title=titre,
                    description= contenu,
                    color=disnake.Colour(color) if color else disnake.Colour.default(),
                    url=url,
                    thumbnail=await thumbnail_file.to_file() if thumbnail_file else thumbnail_url,
                    image=await image_file.to_file() if image_file else image_url,
                    author_name=author_name,
                    author_icon_url=author_icon_url,
                    footer_text=footer_text,
                    footer_icon_url=footer_icon_url
                ) 
            await inter.edit_original_message(embed=embed)
            if (await confirmation(inter, message="Confirmer l'envoie du message ?",color=disnake.Colour.purple())):
                await channel.send(
                    content=mention.mention if mention else None,
                    embed=embed
                )
                await inter.edit_original_message(embed=FS.Embed(description=f"Embed envoyé !"),view=None)
            else:
                await inter.edit_original_message(embed=FS.Embed(description=":o: Envoie du message annulé"), view=None)
        else:
            await inter.edit_original_message(embed=FS.Embed(description="Impossible d'envoyer un embed vide"))
            
    @embed.sub_command(
        name="private",
        description="Envoyer un embed en priver"
    )
    async def embed_private(self, inter : ApplicationCommandInteraction,
                    target : Union[disnake.Role, disnake.Member] = commands.Param(description="Le role ou le member à qui envoye l'embed"),
                    titre : str = commands.Param(description="Le titre", default = disnake.Embed.Empty),
                    contenu : str = commands.Param(description="Le contenu", default = disnake.Embed.Empty),
                    color : ColorEnum = commands.Param(description="La couleur", default=None),
                    url : str = commands.Param(description="L'url", default=disnake.Embed.Empty),
                    thumbnail_url : str = commands.Param(description="L'url du thumbnail", default=disnake.Embed.Empty),
                    thumbnail_file : disnake.Attachment = commands.Param(description="Le fichier du thumbnail", default=None),
                    image_url : str = commands.Param(description="L'url de l'image", default=disnake.Embed.Empty),
                    image_file : disnake.Attachment = commands.Param(description="Le fichier de l'image", default=None),
                    author_name : str = commands.Param(description="Le nom de l'auteur (defaut : ton nom)", default = None),
                    author_icon_url : str = commands.Param(description="L'icon de l'auteur", default=disnake.Embed.Empty),
                    footer_text : str = commands.Param(description="Le text du footer", default=disnake.Embed.Empty),
                    footer_icon_url : str = commands.Param(description="L'url de l'icon du footer", default = disnake.Embed.Empty)):
        await inter.response.defer(ephemeral=True)
        if (
            titre != disnake.Embed.Empty 
            or contenu != disnake.Embed.Empty 
            or thumbnail_file != None 
            or thumbnail_url != disnake.Embed.Empty 
            or image_file != None 
            or image_url != disnake.Embed.Empty
            or author_name != disnake.Embed.Empty
            or author_icon_url != disnake.Embed.Empty):
            embed = FS.Embed(
                    title=titre,
                    description= contenu,
                    color=disnake.Colour(color) if color else disnake.Colour.default(),
                    url=url,
                    thumbnail=await thumbnail_file.to_file() if thumbnail_file else thumbnail_url,
                    image=await image_file.to_file() if image_file else image_url,
                    author_name=author_name,
                    author_icon_url=author_icon_url,
                    footer_text=footer_text,
                    footer_icon_url=footer_icon_url
                ) 
            await inter.edit_original_message(embed=embed)
            if (await confirmation(inter, message="Confirmer l'envoie du message ?",color=disnake.Colour.purple())):
                if isinstance(target, disnake.Role):
                    for member in target.members:
                        await member.send(embed=embed)
                elif isinstance(target, disnake.Member):
                        await target.send(embed=embed)
                await inter.edit_original_message(embed=FS.Embed(description=f"Embed envoyé !"),view=None)
            else:
                await inter.edit_original_message(embed=FS.Embed(description=":o: Envoie du message annulé"),view=None)
        else:
            await inter.edit_original_message(embed=FS.Embed(description="Impossible d'envoyer un embed vide"))
    

    
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
            await inter.edit_original_message(embed=FS.Embed(description=f"Le channel vocal doit initialement permettre au role {inter.guild.default_role.mention} de parler."))
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
                   
                            
                            
    def tr(self, text : str) -> str:
        return self.translator.translate(text)
            
            
    @commands.message_command(
        name="Translate" 
    )
    async def translate(self, inter : disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content = self.tr(inter.target.content)
        embeds = []
        if inter.target.embeds:
            for embed in inter.target.embeds:
                embed.title = self.tr(embed.title)
                if embed.description != disnake.Embed.Empty:
                    embed.description = self.tr(embed.description) 
                if embed.footer.text:
                    embed.set_footer(text= self.tr(embed.footer.text), icon_url=embed.footer.icon_url)
                if embed.author.name:
                    embed.set_author(name = self.tr(embed.author.name), url = embed.author.url, icon_url= embed.author.icon_url)
                fields = embed.fields.copy()
                embed.clear_fields()
                for field in fields:
                    embed.add_field(name=self.tr(field.name), value = self.tr(field.value), inline = field.inline)
                    
                embeds.append(embed)
        await inter.edit_original_message(
            content=content,
            embeds = embeds,
        )
    
                
                
        
    
                
                
            
def setup(bot):
    bot.add_cog(Server(bot))