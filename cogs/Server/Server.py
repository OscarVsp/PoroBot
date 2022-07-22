import logging
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, ChannelFlags
from utils.FastEmbed import FastEmbed
from typing import List, Optional


class LockedChannel:
    
    def __init__(self, channel : disnake.VoiceChannel, reason : str):
        self.channel = channel
        self.authorized_users : List[disnake.Member] = channel.members
        self.reason : str = reason
        self.notified_user : List[disnake.Member] = []
        
    def __eq__(self, other):
        if isinstance(other, LockedChannel):
            return self.channel == other.channel
        elif isinstance(other, disnake.VoiceChannel): 
            return self.channel == other
        else:
            return False
              
    async def mute(self, user : disnake.Member):
        if user.voice.mute == False:
            await user.edit(mute=True)  
        if user not in self.notified_user:
            self.notified_user.append(user)
            await user.send(embed=FastEmbed(
                        title="🔒 Channel verrouillé",
                        description = f"Le channel vocal que tu viens de rejoindre est **verrouillé** pour la raison suivante:\n*{self.reason}*\nTu ne pourras pas parler mais tu peux entendre les autres et regarder des streams."
                    ))


class Server(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot
        self.locked_channels : List[LockedChannel] = []
        self.locked_members : List[disnake.Member] = []
        
    def get_locked_channel(self, channel : disnake.VoiceChannel) -> LockedChannel:
        for locked_channel in self.locked_channels:
            if locked_channel == channel:
                return locked_channel
        return None
    
    def get_channel_by_name(self, channel_name : str, guild : disnake.Guild) -> Optional[disnake.VoiceChannel]:
        for channel in guild.voice_channels:
            if channel.name == channel_name:
                return channel
        return None 
    
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
    
    @channel.sub_command(
        name="lock",
        description="Verrouiller un channel vocal (mute automatiquement les nouveaux arrivant)."
        )
    async def channel_lock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="Le channel vocal à verrouillé"),
                           raison : str = commands.Param(description="Raison du verrouillage (tournois, tryhard, ...)",default="Non spécifié")
                           ):
        channel = self.get_channel_by_name(channel, inter.guild)
        if channel not in self.locked_channels:
            new_locked_channel = LockedChannel(channel,raison)
            self.locked_channels.append(new_locked_channel)
            value = "\n".join([u.display_name for u in new_locked_channel.authorized_users])
            if value == "":
                value = "*N/A*"
            await inter.response.send_message(embed=FastEmbed(
                title=f"Channel __***{channel.name}***___ verrouillé.",
                fields= [
                    {
                        'name':f"**__Membres autorisés :__**",
                        'value':value
                    },{
                        'name':f"**__Raison :__**",
                        'value':new_locked_channel.reason
                    }]
            ),ephemeral=True)
            await channel.edit(name = "🔒 "+channel.name)
        else:
            await inter.response.send_message(embed=FastEmbed(
                description=f"Channel {channel.name} est déjà verrouillé !"
            ), ephemeral=True)
            
    @channel_lock.autocomplete("channel")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [channel.name for channel in inter.guild.voice_channels if (channel not in self.locked_channels and channel.name.lower().startswith(user_input.lower()))]
    
            
            
            
    @channel.sub_command(
        name="unlock",
        description="Déverrouiller un channel vocal verrouillé"
        )
    async def channel_unlock(self, inter : ApplicationCommandInteraction,
                           channel : str = commands.Param(description="The channel vocal à déverrouiller")
                           ):
        channel = self.get_channel_by_name(channel, inter.guild)
        if channel in self.locked_channels:
            channel_to_unlock = self.get_locked_channel(channel)
            self.locked_channels.remove(self.get_locked_channel(channel_to_unlock))
            await channel_to_unlock.unmute_all()
            await inter.response.send_message(embed=FastEmbed(
                description=f"Channel {channel.name} déverrouilé !"
            ), ephemeral=True)
            
        else:
            await inter.response.send_message(embed=FastEmbed(
                description=f"Channel {channel.name} n'est pas actuellement verrouillé !"
            ), ephemeral=True)  
        if channel.name.startswith("🔒 "):
            await channel.edit(name=channel.name[2:]) 
            
    @channel_unlock.autocomplete("channel")
    async def autocomp_unlocked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        return [locked_chan.channel.name for locked_chan in self.locked_channels if (locked_chan.channel.guild == inter.guild and locked_chan.channel.name.lower().startswith(user_input.lower()))]
    
    
        
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_state_update(self, member : disnake.Member, before : disnake.VoiceState, after : disnake.VoiceState):
        #on_connect
        if after.channel != None and (before.channel == None or before.channel != after.channel):
            after_locked_channel = self.get_locked_channel(after.channel)
            #To locked channel
            if after_locked_channel != None:
                await self.on_connect_to_locked_channel(member,after_locked_channel)
            #To unlocked channel
            else:
                await self.on_connect_to_unlocked_channel(member)
        #on_leave
        elif before.channel != None and (after.channel == None or after.channel != before.channel):
            before_locker_channel = self.get_locked_channel(before.channel)
            #From a locked channel
            if before_locker_channel != None:
                await self.on_leave_locked_channel(member, before_locker_channel)
                    
    async def on_connect_to_locked_channel(self, user : disnake.Member, channel : LockedChannel):
        if user in channel.authorized_users:
            if user.voice.mute == True and user in self.locked_members:
                await user.edit(mute=False)
                self.locked_members.remove(user)
                logging.info(f"User {user.name}:{user.id} unmute because channel {channel.channel.name} is locked but he is authorized")
        else:
            if user.voice.mute == False:
                await user.edit(mute=True) 
                self.locked_members.append(user)
                logging.info(f"User {user.name}:{user.id} mute because channel {channel.channel.name} is locked.") 
            if user not in channel.notified_user:
                channel.notified_user.append(user)
                await user.send(embed=FastEmbed(
                            title="🔒 Channel verrouillé",
                            description = f"Le channel vocal que tu viens de rejoindre est **verrouillé** pour la raison suivante:\n*{channel.reason}*\nTu ne pourras pas parler mais tu peux entendre les autres et regarder des streams."
                        ))
        
    async def on_connect_to_unlocked_channel(self, user : disnake.Member):
        if user.voice.mute == True and user in self.locked_members:
            await user.edit(mute=False)
            self.locked_members.remove(user)
            logging.info(f"User {user.name}:{user.id} unmute because not in an locked channel.")
        
    async def on_leave_locked_channel(self, user : disnake.Member, channel: LockedChannel):
        if user in channel.authorized_users:
            used = False
            for authorized_user in channel.authorized_users:
                if authorized_user in channel.channel.members:
                    used = True
                    break
            if not used:
                self.locked_channels.remove(channel)
                for user in channel.channel.members:
                    if user in self.locked_members:
                        await user.edit(mute=False)
                        await user.send(embed=FastEmbed(
                            title=f"🔓 Channel déverrouillé !",
                            description="Le channel dans lequel tu te trouves vient d'être déverrouillé !\nTu peux donc désormais parler normalement."
                        ))

                logging.info(f"Locked channel {channel.channel.name} being unlock because not authorized user are present anymore.")
                if channel.channel.name.startswith("🔒 "):
                    await channel.channel.edit(name=channel.channel.name[2:]) 

def setup(bot):
    bot.add_cog(Server(bot))