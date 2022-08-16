from math import ceil
from random import shuffle
from typing import Tuple
import pickledb
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from modules.FastSnake.SimpleModal import SimpleModal
from modules.FastSnake.Views import confirmation, memberSelection
from .view import *
from .watcher import *
from .exceptions import *


class Lol(commands.Cog):

    def __init__(self, bot):
        """Initialize a Lol cog object and laod the lore of the members.

        Get the member dict for the lore from the "Members.json" file next to it.
        """
        self.bot: commands.InteractionBot = bot
        Watcher.init(bot.config["RIOT_APIKEY"])
        self.summoners = pickledb.load("cogs/Lol/summoners.db", False)

    @commands.slash_command(
        description="Scouter une team clash à partir du nom d'un des joueurs"
    )
    async def clash(self, inter: ApplicationCommandInteraction,
                    summoner: str = commands.Param(
                        description="Le nom d'invocateur d'un des joueurs"
                    )
                    ):
        await inter.response.defer()
        try:
            team = await ClashTeam.by_summoner_name(summoner)
            if team:
                await inter.edit_original_message(
                    embed=(await team.embed()),
                    components=disnake.ui.Button(label="OPGG", emoji=FS.Emotes.Lol.OPGG, style=disnake.ButtonStyle.link, url=(await team.opgg()))
                )

            else:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        title=f"__**Clash**__",
                        description=f"**{summoner}** ne fait pas parti d'une équipe clash actuellement...",
                        thumbnail=FS.Images.Poros.Question
                    )
                )
        except (SummonerNotFound):
            await inter.edit_original_message(
                embed=FS.Embed(
                    title=f"__**Clash**__",
                    description=f"**{summoner}** n'a pas pu être trouvé...\nVérifiez que le nom d'invocateur soit correct.",
                    thumbnail=FS.Images.Poros.Question
                )
            )

    @commands.slash_command(
        name="lol"
    )
    async def lol(self, inter):
        pass

    async def set_summoner(self, inter: disnake.Interaction, target: disnake.User, invocateur: str):
        try:
            summoner = await Summoner.by_name(invocateur)
        except SummonerNotFound:
            await inter.edit_original_message(embed=FS.Embed(title="Invocateur inconnu", description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
            return

        await inter.edit_original_message(embed=(await summoner.embed(force_update=True)))
        confirm = await confirmation(inter, title="Valider l'invocateur", description=f"Est-ce bien ton compte ?")

        if not confirm:
            await inter.edit_original_message(embed=FS.Embed(title="Invocateur refusé.", description="Nom d'invocateur non changé.", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
            return

        if str(target.id) in self.summoners.getall():
            confirm = await confirmation(inter, title="Invocateur déjà existant", description=("Tu as" if target == inter.author else f"{target.mention} a")+f" déjà le nom d'invocateur suivant enregistré : ***{self.summoners.get(str(target.id))}***\n Veux-tu le remplacer ?", timeout=120)
            if not confirm:
                await inter.edit_original_message(embed=FS.Embed(title="Invocteur inchangé", description="Nom d'invocateur non changé", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
                return

        self.summoners.set(str(target.id), invocateur)
        self.summoners.dump()
        await inter.edit_original_message(embed=FS.Embed(title="Invocateur enregistré", description=f"L'invocateur ***{invocateur}*** à bien été lié avec " + ("ton compte discord !" if inter.author == target else f"le compte discord de {target.mention}"), footer_text="Tu peux rejeter ce message pour le faire disparaitre."), view=None)

    @lol.sub_command(
        description="Lier son compte discord avec son compte League of Legends"
    )
    async def account(self, inter: ApplicationCommandInteraction,
                      invocateur: str = commands.Param(description="Ton nom d'invocateur sur League of Legends")):
        await inter.response.defer(ephemeral=True)
        await self.set_summoner(inter, inter.author, invocateur)

    async def modal_callback(self, interaction: disnake.ModalInteraction, answers: dict, callback_datas: dict):
        await self.set_summoner(interaction, callback_datas.get('target'), answers.get("summoner_name"))

    @commands.user_command(
        name="Nom d'invocateur",
        default_member_permissions=disnake.Permissions.all()

    )
    async def summoner_set(self, inter: ApplicationCommandInteraction, target: disnake.User):
        await inter.response.send_modal(SimpleModal(f"Définir le nom d'invocateur de {target.display_name}", questions=[disnake.ui.TextInput(label="Nom d'invocateur", custom_id="summoner_name")], callback=self.modal_callback, callback_datas={'target': target}))

    async def get_lol_classement(self, members_filter : List[disnake.Member]) -> Tuple[List[disnake.Member],List[Summoner]]:
        members: List[disnake.Member] = []
        summoners: List[Summoner] = []
        
        for member in members_filter:
            if str(member.id) in self.summoners.getall():
                new_summoner = await Summoner.by_name(self.summoners.get(str(member.id)))
                await new_summoner.leagues()
                summoners.append(new_summoner)
                members.append(member)

        sorted_summoners: List[Summoner] = sorted(
            summoners, key=lambda x: x._leagues.first.absolut_score, reverse=True)
        sorted_members: List[disnake.Member] = []

        for summoner in sorted_summoners:
            sorted_members.append(members[summoners.index(summoner)])
            
        return (sorted_members,sorted_summoners)


    @lol.sub_command(
        name="classement",
        description="Classement League of Legends des members du serveur"
    )
    async def classement(self, inter: ApplicationCommandInteraction,
                         filtre: str = commands.Param(description="Filtrer les membres à afficher par un role ou un évenement.", default=None)):
        await inter.response.defer(ephemeral=False)

        filtre_members: List[disnake.Member] = None

        if filtre:
            filtre_clean = filtre.split(' ')[1]
            for role in inter.guild.roles:
                if role.name == filtre_clean:
                    filtre_members = role.members
                    break

            if filtre_members == None:
                for event in inter.guild.scheduled_events:
                    if event.name == filtre_clean:
                        filtre_members = [member async for member in event.fetch_users()]
                        break

        if filtre_members == None or filtre == None:
            filtre_members = inter.guild.members

        (sorted_members,sorted_summoners) = await self.get_lol_classement(filtre_members)
        
        ranks = ""
        players = ""

        for i in range(len(sorted_members)):
            ranks += f"{(await sorted_summoners[i].leagues()).first.tier_emote} **{(await sorted_summoners[i].leagues()).first.rank}**\n"
            players += f"**{sorted_members[i].display_name}** (`{sorted_summoners[i].name}`)\n"

        await inter.edit_original_message(
            embed=FS.Embed(
                title=f"{FS.Assets.Emotes.Lol.Logo} __**CLASSEMENT LOL**__",
                description=(f"> *Filtre : {filtre}*" if filtre else ""),
                fields=[
                    {
                        'name': "◾",
                        'value': ranks,
                        "inline": True
                    },
                    {
                        'name': "◾◾◾◾◾◾◾◾◾◾",
                        'value': players,
                        "inline": True
                    }
                ],
                footer_text="""Tu n'es pas dans le classement ?\nLie ton compte League of Legends en utilisant "/lol account" !"""
            )
        )

    @classement.autocomplete("filtre")
    def autocomple_filtre(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        filtres = []
        for role in inter.guild.roles:
            if role.name.lower().startswith(user_input.lower()):
                filtres.append(f"👥 {role.name}")
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                filtres.append(f"📅 {event.name}")
        if len(filtres) > 25:
            filtres = filtres[:25]
        return filtres
    
    @lol.sub_command(
        name="live",
        description="Info sur une partie en cours"
    )
    async def live(self, inter: ApplicationCommandInteraction,
                         invocateur: str = commands.Param(description="Le nom de l'invocateur.")):
        await inter.response.defer(ephemeral=False)
        
        try:
            summoner = await Summoner.by_name(invocateur)
        except SummonerNotFound:
            await inter.edit_original_message(embed=FS.Embed(title="Invocateur inconnu", description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
            await inter.delete_original_message(delay = 3)
            return
        
        await inter.edit_original_message(embeds=[await summoner.embed(force_update=True),FS.Embed(description="*Recherche de game en cours...*")])

        live_game = await summoner.currentGame()
        if live_game:
            await inter.edit_original_message(embeds=[await summoner.embed(),(await live_game.embed())])
        
        else:
            await inter.edit_original_message(embeds=[(await summoner.embed()),FS.Embed(description="*Pas de partie en cours*")])
            await inter.delete_original_message(delay=30)
            
    @lol.sub_command(
        name="invocateur",
        description="Info sur un invocateur"
    )
    async def invocateur(self, inter: ApplicationCommandInteraction,
                         invocateur: str = commands.Param(description="Le nom de l'invocateur.")):
        await inter.response.defer(ephemeral=False)
        
        try:
            summoner = await Summoner.by_name(invocateur)
            await inter.edit_original_message(embed=await summoner.embed(force_update=True))
        except SummonerNotFound:
            await inter.edit_original_message(embed=FS.Embed(title="Invocateur inconnu", description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
            await inter.delete_original_message(delay = 3)
            
            
    def seeding_check(self, **kwargs) -> bool:
        return str(kwargs.get("member").id) in self.summoners.getall()
            
    @lol.sub_command(
        name="seeding",
        description="Diviser un groupe en sous groupes en utilisant le classement lol comme seeding"
    )
    async def seeding(self, inter: ApplicationCommandInteraction,
                      nombre : int = commands.Param(description="Nombre de sous groupe", gt=1)):
        await inter.response.defer(ephemeral=True)
        selection = await memberSelection(target=inter,description="Compose le groupe de membre à diviser.", check=self.seeding_check)
        if selection:
            await inter.edit_original_message(embed=FS.Embed(description="Composition des groupes..."),view=None)
            (sorted_members,sorted_summoners) = await self.get_lol_classement(selection.members)
            groupes : List[List[Tuple[disnake.Member,Summoner]]] = [[] for _ in range(nombre)]
            for i in range(ceil(len(sorted_members)/nombre)):
                tier_groupe : List[Tuple[disnake.Member,Summoner]] = []
                for j in range(nombre):
                    if i*nombre+j < len(sorted_members):
                        tier_groupe.append((sorted_members[i*nombre+j],sorted_summoners[i*nombre+j]))
                    else:
                        tier_groupe.append(None)
                shuffle(tier_groupe)
                for j,player in enumerate(tier_groupe):
                    if player:
                        groupes[j].append(player)
                    
            ranks = ""
            players = ""

            for i in range(len(sorted_members)):
                ranks += f"{(await sorted_summoners[i].leagues()).first.tier_emote} **{(await sorted_summoners[i].leagues()).first.rank}**\n"
                players += f"**{sorted_members[i].mention}** (`{sorted_summoners[i].name}`)\n"

            await inter.channel.send(
                embed=FS.Embed(
                    title=f"{FS.Assets.Emotes.Lol.Logo} __**CLASSEMENT LOL**__",
                    fields=[
                        {
                            'name': "◾",
                            'value': ranks,
                            "inline": True
                        },
                        {
                            'name': "◾◾◾◾◾◾◾◾◾◾",
                            'value': players,
                            "inline": True
                        }
                    ] + [
                        {'name':f"**Groupe {FS.Emotes.Alpha[i]}**",'value':'\n'.join([f"> {member[0].mention}" for member in members])}
                        for i,members in enumerate(groupes)
                    ]
                ),
                view=None
            )  
            await inter.edit_original_message(embed=FS.Embed(description="Groupes crées !",footer_text="Tu peux rejeter ce message pour le faire disparaitre"),view=None)
        else:
            await inter.edit_original_message(embed=FS.Embed(description=":x Annulé",footer_text="Tu peux rejeter ce message pour le faire disparaitre"),view=None) 

    @commands.slash_command(
        description="Voir combien de temps et d'argent tu as dépensés sur LOL"
    )
    async def wasteonlol(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(
                title="__**Wasted on Lol**__",
                description="Utilise les liens ci-dessous pour découvrir combien de temps et/ou d'argent tu as dépensés dans League of Legends",
                thumbnail=FS.Images.Poros.Neutral

            ),
            components=[
                disnake.ui.Button(label="Temps passé sur lol", emoji="⌛",
                                  style=disnake.ButtonStyle.link, url="https://wol.gg/"),
                disnake.ui.Button(label="Argent dépensé sur lol", emoji="💰", style=disnake.ButtonStyle.link,
                                  url="https://support-leagueoflegends.riotgames.com/hc/fr/articles/360026080634")
            ],
            delete_after=60
        )

    @commands.slash_command(
        description="Obtenir les règles de l'aram à boire"
    )
    async def drink(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(embed=drink_embed)

    @commands.slash_command(
        description="Obtenir le dernier patch the League of Legends"
    )
    async def patchnote(self, inter: ApplicationCommandInteraction,
                        previous: int = commands.Param(
                            description="Nombre de patch en arrière (0 pour le patch en cours)",
                            ge=0,
                            default=0
                        )
                        ):
        patch = PatchNoteView(inter, previous)
        await inter.response.send_message(
            embed=patch.embed,
            view=patch
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(Lol(bot))
