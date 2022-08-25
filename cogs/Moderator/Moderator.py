from enum import Enum
from typing import Union
import disnake
from disnake.ext import commands
import modules.FastSnake as FS
from modules.FastSnake.Views import memberSelection


class ColorEnum(disnake.Colour, Enum):
    Blue = (disnake.Colour.blue().value,)
    Blurple = (disnake.Colour.blurple().value,)
    Brand_green = (disnake.Colour.brand_green().value,)
    Brand_red = (disnake.Colour.brand_red().value,)
    Dark_blue = (disnake.Colour.dark_blue().value,)
    Dark_gold = (disnake.Colour.dark_gold().value,)
    Dark_green = (disnake.Colour.dark_green().value,)
    Dark_magenta = (disnake.Colour.dark_magenta().value,)
    Dark_orange = (disnake.Colour.dark_orange().value,)
    Dark_purple = (disnake.Colour.dark_purple().value,)
    Dark_red = (disnake.Colour.dark_red().value,)
    Dark_teal = (disnake.Colour.dark_teal().value,)
    Dark_theme = (disnake.Colour.dark_theme().value,)
    Fuchsia = (disnake.Colour.fuchsia().value,)
    Gold = (disnake.Colour.gold().value,)
    Green = (disnake.Colour.green().value,)
    Lighter_gray = (disnake.Colour.lighter_gray().value,)
    Magenta = (disnake.Colour.magenta().value,)
    Og_blurple = (disnake.Colour.og_blurple().value,)
    Orange = (disnake.Colour.orange().value,)
    Purple = (disnake.Colour.purple().value,)
    Random = (disnake.Colour.random().value,)
    Red = (disnake.Colour.red().value,)
    Teal = (disnake.Colour.teal().value,)
    Yellow = disnake.Colour.yellow().value


class Moderator(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(name="emotes")
    async def emotes(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @emotes.sub_command(name="serveur", description="Obtenir la list de toutes les emotes du serveur")
    async def emotes_guild(self, inter: disnake.ApplicationCommandInteraction, id: bool = False):
        if id:
            await inter.response.send_message(
                embed=FS.Embed(
                    title="__**EMOTES DU SERVEUR**__",
                    description="\n".join(
                        [
                            f"""{e.name.upper()} : str = "`<{'a' if e.animated else ''}:{e.name}:{e.id}>`" """
                            for e in inter.guild.emojis
                        ]
                    ),
                )
            )
        else:
            await inter.response.send_message(
                embed=FS.Embed(
                    title="__**EMOTES DU SERVEUR**__",
                    description="\n".join(
                        [f"""{e} `<{'a' if e.animated else ''}:{e.name}:{e.id}>` """ for e in inter.guild.emojis]
                    ),
                )
            )

    @emotes.sub_command(name="all", description="Obtenir la liste des toutes les émotes accéssible par le bot.")
    async def emotes_guild(self, inter: disnake.ApplicationCommandInteraction, id: bool = False):
        await inter.response.defer()
        if id:
            embeds = FS.Embed.flex(
                title="__**EMOTES DU BOT**__",
                description="\n".join(
                    [
                        f"""{e.name.upper()} : str = "`<{'a' if e.animated else ''}:{e.name}:{e.id}>`" """
                        for e in self.bot.emojis
                    ]
                ),
            )
            await inter.edit_original_message(embed=embeds[0])
            if len(embeds) > 1:
                for embed in embeds[1:]:
                    await inter.channel.send(embed=embed)
        else:
            embeds = FS.Embed.flex(
                title="__**EMOTES DU BOT**__",
                description="\n".join(
                    [f"""{e} `<{'a' if e.animated else ''}:{e.name}:{e.id}>`""" for e in self.bot.emojis]
                ),
            )
            await inter.edit_original_message(embed=embeds[0])
            if len(embeds) > 1:
                for embed in embeds[1:]:
                    await inter.channel.send(embed=embed)

    @commands.slash_command(
        name="clear",
        default_member_permissions=disnake.Permissions.all(),
        guild_ids=[281403075506339840, 533360564878180382, 1008343697097760800],
        dm_permission=False,
    )
    async def clear(self, inter):
        pass

    @clear.sub_command(name="message", description="Supprimer les derniers messages du channel")
    async def clearMessage(
        self,
        inter: disnake.ApplicationCommandInteraction,
        nombre: int = commands.Param(description="le nombre de message à supprimer", gt=0),
    ):
        confirm: FS.ConfirmationReturnData = await FS.confirmation(
            inter,
            title=f"__**Suppression de {nombre} message(s)**__",
            description=f"Êtes-vous sûr de vouloir supprimer les {nombre} dernier(s) message(s) de ce channel ?\nCette action est irréversible !",
            timeout=30,
        )
        if confirm:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f"Suppression de {nombre} message(s) en cours... ⌛", color=disnake.Colour.green()
                ),
                view=None,
            )
            await inter.channel.purge(limit=nombre)
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f":broom: {nombre} messages supprimés ! :broom:", color=disnake.Colour.green()
                )
            )
        elif confirm.is_cancelled:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f":o: Suppresion de {nombre} message(s) annulée", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )
        else:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f":o: Suppresion de {nombre} message(s) timeout", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )

    @clear.sub_command(name="category", description="Supprimer une categorie")
    async def clearCat(
        self,
        inter: disnake.ApplicationCommandInteraction,
        categorie: disnake.CategoryChannel = commands.Param(description="Choisissez categorie à suppimer"),
    ):

        if await FS.confirmation(
            inter,
            title=f"__**Suppression de la categorie *{categorie.name}***__",
            description=f"Êtes-vous sûr de vouloir supprimer la catégorie ***{categorie.mention}*** ?\nCela supprimera également les {len(categorie.channels)} channels contenus dans celle-ci :\n"
            + "\n".join(channel.mention for channel in categorie.channels)
            + "\nCette action est irréversible !",
        ):
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f"Suppression de la catégorie *{categorie.name}* en cours... ⌛",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        description=f":broom: **Catégorie** *{categorie.name}* **supprimée** ! :broom:",
                        color=disnake.Colour.green(),
                    )
                )
            except disnake.NotFound:
                pass
        else:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f":o: Suppression de la catégorie {categorie.mention} annulée !",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )

    @commands.slash_command(
        name="create",
        default_member_permissions=disnake.Permissions.all(),
        guild_ids=[281403075506339840, 533360564878180382, 1008343697097760800],
        dm_permission=False,
    )
    async def export(self, inter):
        pass

    @export.sub_command_group(name="role")
    async def export_role(self, inter):
        pass

    @export_role.sub_command(name="from_event", description="Créer un role à partir des participants d'un évennement.")
    async def export_role_from_event(
        self,
        inter: disnake.ApplicationCommandInteraction,
        event: str = commands.Param(description="L'évennement depuis lequel exporter les membres"),
        name: str = commands.Param(description='Le nom du role à créer (default = "event.name role")', default=None),
    ):
        await inter.response.defer(ephemeral=True)
        events = await inter.guild.fetch_scheduled_events()
        event: disnake.GuildScheduledEvent = next((e for e in events if e.name == event), None)
        if not name:
            name = f"{event.name} role"
        event_members = []
        async for member in event.fetch_users():
            event_members.append(member)

        response = await FS.memberSelection(
            inter,
            title="Export role from event",
            description="Select members below",
            timeout=300,
            pre_selection=event_members,
        )
        if response:
            await inter.edit_original_message(
                embed=FS.Embed(description=f"{FS.Emotes.LOADING} Création du role en cours..."), view=None
            )
            new_role: disnake.Role = await inter.guild.create_role(name=name)
            for member in response.members:
                await member.add_roles(new_role)
            await inter.edit_original_message(
                embed=FS.Embed(
                    description="\n".join(member.display_name for member in response.members)
                    if (response.members and len(response.members) > 0)
                    else "*Aucun membre sélectionné*"
                )
            )
        else:
            inter.edit_original_message(embed=FS.Embed(description=":o: Annulé"), view=None)

    @export_role_from_event.autocomplete("event")
    async def autocomp_event(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        events = []
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                events.append(event.name)
        return events

    @export_role.sub_command(name="from_role", description="Créer un role à partir d'un role existant.")
    async def export_role_from_role(
        self,
        inter: disnake.ApplicationCommandInteraction,
        role: disnake.Role = commands.Param(description="Le role depuis lequel exporter les members"),
        name: str = commands.Param(description='Le nom du role à créer (default = "role.name copy")', default=None),
    ):
        await inter.response.defer(ephemeral=True)
        if not name:
            name = f"{role.name} copy"

        response = await FS.memberSelection(
            inter,
            title="Export role from role",
            description="Select members to export to the new role",
            timeout=300,
            pre_selection=role.members,
        )
        if response:
            await inter.edit_original_message(
                embed=FS.Embed(description=f"{FS.Emotes.LOADING} Création du role en cours..."), view=None
            )
            new_role: disnake.Role = await inter.guild.create_role(name=name)
            for member in response.members:
                await member.add_roles(new_role)
            await inter.edit_original_message(
                embed=FS.Embed(
                    description="\n".join(member.display_name for member in response.members)
                    if (response.members and len(response.members) > 0)
                    else "*Aucun membre sélectionné*"
                )
            )
        else:
            inter.edit_original_message(embed=FS.Embed(description=":o: Annulé"), view=None)

    @commands.slash_command(
        name="embed",
        description="Envoyer un embed",
        dm_permission=False,
        guild_ids=[281403075506339840, 533360564878180382, 1008343697097760800],
        default_member_permissions=disnake.Permissions.all(),
    )
    async def embed(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @embed.sub_command(name="guild", description="Envoyer un embed dans un channel d'un server")
    async def embed_guild(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel = commands.Param(
            description="The channel where to send the embed (default : here)", default=None
        ),
        titre: str = commands.Param(description="Le titre", default=disnake.Embed.Empty),
        contenu: str = commands.Param(description="Le contenu", default=disnake.Embed.Empty),
        mention: Union[disnake.Role, disnake.Member] = commands.Param(
            description="Un role ou un membre à mentionner", default=None
        ),
        color: ColorEnum = commands.Param(description="La couleur", default=None),
        url: str = commands.Param(description="L'url", default=disnake.Embed.Empty),
        thumbnail_url: str = commands.Param(description="L'url du thumbnail", default=disnake.Embed.Empty),
        thumbnail_file: disnake.Attachment = commands.Param(description="Le fichier du thumbnail", default=None),
        image_url: str = commands.Param(description="L'url de l'image", default=disnake.Embed.Empty),
        image_file: disnake.Attachment = commands.Param(description="Le fichier de l'image", default=None),
        author_name: str = commands.Param(description="Le nom de l'auteur (defaut : ton nom)", default=None),
        author_icon_url: str = commands.Param(description="L'icon de l'auteur", default=disnake.Embed.Empty),
        footer_text: str = commands.Param(description="Le text du footer", default=disnake.Embed.Empty),
        footer_icon_url: str = commands.Param(description="L'url de l'icon du footer", default=disnake.Embed.Empty),
    ):
        await inter.response.defer(ephemeral=True)
        if titre != disnake.Embed.Empty or contenu != disnake.Embed.Empty:
            if not channel:
                channel = inter.channel
            embed = FS.Embed(
                title=titre,
                description=contenu,
                color=disnake.Colour(color) if color else disnake.Colour.default(),
                url=url,
                thumbnail=await thumbnail_file.to_file() if thumbnail_file else thumbnail_url,
                image=await image_file.to_file() if image_file else image_url,
                author_name=author_name,
                author_icon_url=author_icon_url,
                footer_text=footer_text,
                footer_icon_url=footer_icon_url,
            )
            if await FS.confirmation(
                inter, embeds=[embed], description="Confirmer l'envoie du message ?", color=disnake.Colour.purple()
            ):
                await channel.send(content=mention.mention if mention else None, embed=embed)
                await inter.edit_original_message(embed=FS.Embed(description=f"Embed envoyé !"), view=None)
            else:
                await inter.edit_original_message(embed=FS.Embed(description=":o: Envoie du message annulé"), view=None)
        else:
            await inter.edit_original_message(embed=FS.Embed(description="Impossible d'envoyer un embed vide"))

    @embed.sub_command(name="private", description="Envoyer un embed en priver")
    async def embed_private(
        self,
        inter: disnake.ApplicationCommandInteraction,
        target: Union[disnake.Role, disnake.Member] = commands.Param(
            description="Le role ou le member à qui envoye l'embed"
        ),
        titre: str = commands.Param(description="Le titre", default=disnake.Embed.Empty),
        contenu: str = commands.Param(description="Le contenu", default=disnake.Embed.Empty),
        color: ColorEnum = commands.Param(description="La couleur", default=None),
        url: str = commands.Param(description="L'url", default=disnake.Embed.Empty),
        thumbnail_url: str = commands.Param(description="L'url du thumbnail", default=disnake.Embed.Empty),
        thumbnail_file: disnake.Attachment = commands.Param(description="Le fichier du thumbnail", default=None),
        image_url: str = commands.Param(description="L'url de l'image", default=disnake.Embed.Empty),
        image_file: disnake.Attachment = commands.Param(description="Le fichier de l'image", default=None),
        author_name: str = commands.Param(description="Le nom de l'auteur (defaut : ton nom)", default=None),
        author_icon_url: str = commands.Param(description="L'icon de l'auteur", default=disnake.Embed.Empty),
        footer_text: str = commands.Param(description="Le text du footer", default=disnake.Embed.Empty),
        footer_icon_url: str = commands.Param(description="L'url de l'icon du footer", default=disnake.Embed.Empty),
    ):
        await inter.response.defer(ephemeral=True)
        if (
            titre != disnake.Embed.Empty
            or contenu != disnake.Embed.Empty
            or thumbnail_file != None
            or thumbnail_url != disnake.Embed.Empty
            or image_file != None
            or image_url != disnake.Embed.Empty
            or author_name != disnake.Embed.Empty
            or author_icon_url != disnake.Embed.Empty
        ):
            embed = FS.Embed(
                title=titre,
                description=contenu,
                color=disnake.Colour(color) if color else disnake.Colour.default(),
                url=url,
                thumbnail=await thumbnail_file.to_file() if thumbnail_file else thumbnail_url,
                image=await image_file.to_file() if image_file else image_url,
                author_name=author_name,
                author_icon_url=author_icon_url,
                footer_text=footer_text,
                footer_icon_url=footer_icon_url,
            )

            if await FS.confirmation(
                inter, embeds=[embed], description="Confirmer l'envoie du message ?", color=disnake.Colour.purple()
            ):
                if isinstance(target, disnake.Role):
                    for member in target.members:
                        await member.send(embed=embed)
                elif isinstance(target, disnake.Member):
                    await target.send(embed=embed)
                await inter.edit_original_message(embed=FS.Embed(description=f"Embed envoyé !"), view=None)
            else:
                await inter.edit_original_message(embed=FS.Embed(description=":o: Envoie du message annulé"), view=None)
        else:
            await inter.edit_original_message(embed=FS.Embed(description="Impossible d'envoyer un embed vide"))


def setup(bot: commands.InteractionBot):
    bot.add_cog(Moderator(bot))
