import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from typing import List

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
        
    async def unmute_all(self):
        for user in self.channel.members:
            if user.voice.mute == True:
                await user.edit(mute=False)
                await user.send(embed=FastEmbed(
                    title=f"🔓 Channel déverrouillé !",
                    description="Le channel dans lequel tu te trouves vient d'être déverrouillé !\nTu peux donc désormais parler normalement."
                ))
                
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
        
    def get_locked_channel(self, channel : disnake.VoiceChannel) -> LockedChannel:
        for locked_channel in self.locked_channels:
            if locked_channel == channel:
                return locked_channel
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
                           channel : disnake.VoiceChannel = commands.Param(description="Le channel vocal à verrouillé"),
                           raison : str = commands.Param(description="Raison du verrouillage (tournois, tryhard, ...)",default="Non spécifié")
                           ):
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
            
            
            
    @channel.sub_command(
        name="unlock",
        description="Déverrouiller un channel vocal verrouillé"
        )
    async def channel_unlock(self, inter : ApplicationCommandInteraction,
                           channel : disnake.VoiceChannel = commands.Param(description="The channel vocal à déverrouiller")
                           ):
        if channel in self.locked_channels:
            channel_to_unlock = self.get_locked_channel(channel)
            self.locked_channels.remove(self.get_locked_channel(channel_to_unlock))
            await channel_to_unlock.unmute_all()
            await inter.response.send_message(embed=FastEmbed(
                description=f"Channel {channel.name} déverrouilé !"
            ), ephemeral=True)
            if channel.name.startswith("🔒 "):
                await channel.edit(name=channel.name[2:])
        else:
            await inter.response.send_message(embed=FastEmbed(
                description=f"Channel {channel.name} n'est pas actuellement verrouillé !"
            ), ephemeral=True)   
        
    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_state_update(self, member : disnake.Member, before : disnake.VoiceState, after : disnake.VoiceState):
        if after.channel != None:
            after_locked_channel = self.get_locked_channel(after.channel)
            if after_locked_channel != None:
                if member not in after_locked_channel.authorized_users: 
                    await after_locked_channel.mute(member)
            else:
                if member.voice.mute == True:
                    await member.edit(mute=False)
                    
                


def setup(bot):
    bot.add_cog(Server(bot))