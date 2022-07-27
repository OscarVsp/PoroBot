from abc import abstractmethod
import random
import disnake
from utils.data import emotes,color
from utils.FastEmbed import FastEmbed
from utils.ShadowMember import ShadowMember, VocalGuildChannel, Components
import json
import logging
from datetime import datetime
from typing import List, Union, Optional, Sequence, overload
               

class Player(ShadowMember):
    
    def __init__(self, tournament, member : disnake.Member, size_of_scores : int = 1):
        super().__init__(member)
        self._scores : List[int] = [0 for _ in range(size_of_scores)]
        self._tournament : Tournament = tournament
        
    @property
    def score(self, index : int = 0) -> int:
        return self._scores[index]
    
    @property
    def display(self) -> str:
        return f"**{super().display_name}**"
    
    
    @property
    def scores(self) -> List[int]:
        return self._scores
    
    @property
    def points(self) -> int:
        if self._tournament:
            return sum([self._scores[i]*self._tournament.weights[i] for i in range(len(self._scores))])
        else:
            raise AttributeError('Attribut "tournament" need to be set before accessing property "point".')
    
    @property
    def log_id(self) -> str:
        return f"[PLAYER {self.name}:{self.id}]"
    
    def set_tournament(self, tournement) -> None:
        self._tournament : Tournament = tournement
    
    def add_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] += value
        else:
            logging.error(f"{self.log_id} Error on adding score : index {index} is not initialized in the score.")
            
    def add_scores(self, values : List[int]):
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self._scores[i] += value
        else:
            logging.error(f"{self.log_id} Error on adding scores : list of values is not the same size than the number of score ({len(self._scores)}).")
            
    def remove_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] -= value
        else:
            logging.error(f"{self.log_id} Error on removing score : index {index} is not initialized in the score.")
    
    def remove_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self._scores[i] -= value
        else:
            logging.error(f"{self.log_id} Error on removing scores : list of values is not the same size than the number of score ({len(self._scores)}).")        
    
    def set_score(self, value : int, index : int) -> None:
        if len(self._scores) > index:
            self._scores[index] = value
        else:
            logging.error(f"{self.log_id} Error on setting score : index {index} is not initialized in the score.")
            
    def set_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            self._scores = values
        else:
            logging.error(f"{self.log_id} Error on setting scores : list of values is not the same size than the number of score ({len(self._scores)}).") 
      
    def clear_score(self, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] = 0
        else:
            logging.error(f"{self.log_id}Tournament Error on clearing score : index {index} is not initialized in the score.")
    
    def clear_scores(self) -> None:
        self._scores = [0 for _ in range(len(self._scores))]
    
    def __iter__(self):
        yield 'display_name', self.display_name
        yield 'name', self.name
        yield 'id', self.id
        yield 'scores', self._scores
        
class Team:
    
    def __init__(self, tournament, players : List[Player], round_idx : int, match_idx : int, team_idx : int, size_of_scores : int = 1):
        self.tournament : Tournament = tournament
        self._players : List[Player] = players
        self._round_idx : int = round_idx
        self._match_idx : int = match_idx
        self._team_idx : int = team_idx
        self._scores : List[int] = [0 for _ in range(size_of_scores)]
        
    @property
    def round_idx(self) -> int:
        return self._round_idx
    
    @property
    def match_idx(self) -> int:
        return self._match_idx
    
    @property
    def team_idx(self) -> int:
        return self._team_idx
    
    @property
    def indexes(self) -> List[int]:
        return [self._round_idx, self._match_idx, self._team_idx]
        
    @property
    def name(self) -> str:
        return " & ".join([p.name for p in self._players])
    
    @property
    def display_name(self) -> str:
        return " & ".join([p.display_name for p in self._players])
    
    @property
    def display(self) -> str:
        return " & ".join([p.display for p in self._players])
    
    @property
    def ids(self) -> List[int]:
        return [p.id for p in self._players]
        
    @property
    def score(self, index : int = 0) -> int:
        return self._scores[index]
    
    @property
    def scores(self) -> List[int]:
        return self._scores
    
    @property
    def points(self) -> int:
        return sum([self._scores[i]*self.tournament.weights[i] for i in range(len(self._scores))])
    
    @property
    def log_id(self) -> str:
        return f"[TEAM {self._round_idx}:{self._match_idx}:{self._team_idx}]"
    
    @property
    def players(self) -> List[Player]:
        return self._players
    
    def add_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] += value
            for player in self._players:
                player.add_score(value=value, index=index)
        else:
            logging.error(f"{self.log_id} Error on adding score : index {index} is not initialized in the score.")
    
    def add_scores(self, values : List[int]):
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self.add_score(value,i)
        else:
            logging.error(f"{self.log_id} Error on adding scores : list of values is not the same size than the number of score ({len(self._scores)}).")
        
    def remove_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] -= value
            for player in self._players:
                player.remove_score(value=value, index=index)
        else:
            logging.error(f"{self.log_id} Error on removing score : index {index} is not initialized in the score.")
    
    def remove_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self.remove_score(value,i)
        else:
            logging.error(f"{self.log_id} Error on removing scores : list of values is not the same size than the number of score ({len(self._scores)}).")        
        
    def set_score(self, value : int, index : int) -> None:
        if len(self._scores) > index:
            for player in self._players:
                player.remove_score(value=self._scores[index], index=index)
                player.add_score(value=value, index=index)
            self._scores[index] = value
        else:
            logging.error(f"{self.log_id} Error on setting score : index {index} is not initialized in the score.")
            
    def set_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            for player in self._players:
                player.remove_scores(values=self._scores)
                player.add_scores(values=values)
            self._scores = values
        else:
            logging.error(f"{self.log_id} Error on setting scores : list of values is not the same size than the number of score ({len(self._scores)}).") 
    
    def clear_score(self, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] = 0
            for player in self._players:
                player.clear_score(index=index)
        else:
            logging.error(f"{self.log_id} Error on clearing score : index {index} is not initialized in the score.")
            
    def clear_scores(self) -> None:
        self._scores = [0 for _ in range(len(self._scores))]
        for player in self._players:
            player.clear_scores()
            
    async def move_to(self, channel : VocalGuildChannel = None, channels : List[VocalGuildChannel] = None):
        if channel and not channels:
            for player in self._players:
                await player.move_to(channel)
        elif channels and not channel:
            if len(channels) == len(self._players):
                for i,player in enumerate(self._players):
                    await player.move_to(channels[i])
            else:
                logging.error(f"{self.log_id} Error on moving players : size of 'channels' is not compatible with the number of players")
        elif channel and channels:
            logging.error(f"{self.log_id} Error on moving players : Only one of 'channel' or 'channels' should be used.")
        else:
            
            logging.error(f"{self.log_id} Error on moving players : 'channel' and 'channels' are both None. One has to be set.'")
            
    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: disnake.Embed = ...,
        file: disnake.File = ...,
        stickers: Sequence[Union[disnake.GuildSticker, disnake.StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        suppress_embeds: bool = ...,
        allowed_mentions: disnake.AllowedMentions = ...,
        reference: Union[disnake.Message, disnake.MessageReference, disnake.PartialMessage] = ...,
        mention_author: bool = ...,
        view: disnake.ui.View = ...,
        components: Components = ...,
    ) -> disnake.Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embed: disnake.Embed = ...,
        files: List[disnake.File] = ...,
        stickers: Sequence[Union[disnake.GuildSticker, disnake.StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        suppress_embeds: bool = ...,
        allowed_mentions: disnake.AllowedMentions = ...,
        reference: Union[disnake.Message, disnake.MessageReference, disnake.PartialMessage] = ...,
        mention_author: bool = ...,
        view: disnake.ui.View = ...,
        components: Components = ...,
    ) -> disnake.Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: List[disnake.Embed] = ...,
        file: disnake.File = ...,
        stickers: Sequence[Union[disnake.GuildSticker, disnake.StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        suppress_embeds: bool = ...,
        allowed_mentions: disnake.AllowedMentions = ...,
        reference: Union[disnake.Message, disnake.MessageReference, disnake.PartialMessage] = ...,
        mention_author: bool = ...,
        view: disnake.ui.View = ...,
        components: Components = ...,
    ) -> disnake.Message:
        ...

    @overload
    async def send(
        self,
        content: Optional[str] = ...,
        *,
        tts: bool = ...,
        embeds: List[disnake.Embed] = ...,
        files: List[disnake.File] = ...,
        stickers: Sequence[Union[disnake.GuildSticker, disnake.StickerItem]] = ...,
        delete_after: float = ...,
        nonce: Union[str, int] = ...,
        suppress_embeds: bool = ...,
        allowed_mentions: disnake.AllowedMentions = ...,
        reference: Union[disnake.Message, disnake.MessageReference, disnake.PartialMessage] = ...,
        mention_author: bool = ...,
        view: disnake.ui.View = ...,
        components: Components = ...,
    ) -> disnake.Message:
        ...

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: bool = False,
        embed: disnake.Embed = None,
        embeds: List[disnake.Embed] = None,
        file: disnake.File = None,
        files: List[disnake.File] = None,
        stickers: Sequence[Union[disnake.GuildSticker, disnake.StickerItem]] = None,
        delete_after: float = None,
        nonce: Union[str, int] = None,
        suppress_embeds: bool = False,
        allowed_mentions: disnake.AllowedMentions = None,
        reference: Union[disnake.Message, disnake.MessageReference, disnake.PartialMessage] = None,
        mention_author: bool = None,
        view: disnake.ui.View = None,
        components: Components = None,
    ):
        """|coro|

        Sends a message to the destination with the content given.

        The content must be a type that can convert to a string through ``str(content)``.

        At least one of ``content``, ``embed``/``embeds``, ``file``/``files``
        or ``stickers`` must be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`.File` objects.
        **Specifying both parameters will lead to an exception**.

        To upload a single embed, the ``embed`` parameter should be used with a
        single :class:`.Embed` object. To upload multiple embeds, the ``embeds``
        parameter should be used with a :class:`list` of :class:`.Embed` objects.
        **Specifying both parameters will lead to an exception**.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Whether the message should be sent using text-to-speech.
        embed: :class:`.Embed`
            The rich embed for the content to send. This cannot be mixed with the
            ``embeds`` parameter.
        embeds: List[:class:`.Embed`]
            A list of embeds to send with the content. Must be a maximum of 10.
            This cannot be mixed with the ``embed`` parameter.

            .. versionadded:: 2.0

        file: :class:`.File`
            The file to upload. This cannot be mixed with the ``files`` parameter.
        files: List[:class:`.File`]
            A list of files to upload. Must be a maximum of 10.
            This cannot be mixed with the ``file`` parameter.
        stickers: Sequence[Union[:class:`.GuildSticker`, :class:`.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.

            .. versionadded:: 2.0

        nonce: Union[:class:`str`, :class:`int`]
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`.Message`, :class:`.MessageReference`, :class:`.PartialMessage`]
            A reference to the :class:`.Message` to which you are replying, this can be created using
            :meth:`.Message.to_reference` or passed directly as a :class:`.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            .. versionadded:: 1.6

        view: :class:`.ui.View`
            A Discord UI View to add to the message. This cannot be mixed with ``components``.

            .. versionadded:: 2.0

        components: |components_type|
            A list of components to include in the message. This cannot be mixed with ``view``.

            .. versionadded:: 2.4

        suppress_embeds: :class:`bool`
            Whether to suppress embeds for the message. This hides
            all embeds from the UI if set to ``True``.

            .. versionadded:: 2.5

        Raises
        ------
        HTTPException
            Sending the message failed.
        Forbidden
            You do not have the proper permissions to send the message.
        InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`.Message`,
            :class:`.MessageReference` or :class:`.PartialMessage`.

        Returns
        -------
        :class:`.Message`
            The message that was sent.
        """
        for player in self._players:
            await player.send(
                content=content,
                tts=tts, embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                stickers=stickers,
                delete_after=delete_after,
                nonce=nonce,
                suppress_embeds=suppress_embeds,
                allowed_mentions=allowed_mentions,
                reference=reference,
                mention_author=mention_author,
                view=view,
                components=components)   
        
    def __iter__(self):
        yield 'round_idx', self.round_idx
        yield 'match_idx', self.match_idx
        yield 'team_idx', self.team_idx
        yield 'players', [dict(p) for p in self._players]
        yield 'scores', self._scores
                       
Entity = Union[Player,Team]
    
#Class for a match between two teams, with attributs for the teams and the winner, and method to add points to a team
class Match:
    def __init__(self, tournament, round_idx : int, match_idx : int, entities : List[Entity] = None, point_to_win : int = 2):
        self._tournament = tournament
        self._round_idx : int = round_idx
        self._match_idx : int = match_idx
        self._entities : List[Entity] = entities
        self._point_to_win : int = point_to_win
        
    @property
    def round_idx(self) -> int:
        return self._round_idx

    @property
    def match_idx(self) -> int:
        return self._match_idx
    
    @property
    def indexes(self) -> List[int]:
        return [self._round_idx, self._match_idx]

    @property
    def teams(self) -> List[Team]:
        return self._entities
    
    @property
    def player(self) -> List[Player]:
        return self._entities
    
    @property
    def point_to_win(self) -> int:
        return self._point_to_win
            
    @property
    def is_played(self) -> bool:
        played = False
        for entity in self._entities:
            played = played or (entity.points >= self._point_to_win)
        return played
    
    @property
    def title(self) -> str:
        if self.is_played:
            return f"~~__MATCH __{emotes.alpha[self._match_idx]}~~"
        else:
            return f"__MATCH __{emotes.alpha[self._match_idx]}"

    @property
    def field(self) -> dict:
        if self.is_played:
            indicators = ['❌' for _ in range(len(self._entities))]
        else:
            indicators = ['⬛' for _ in range(len(self._entities))]
        for i,entity in enumerate(self._entities):
            if round(entity.points) >= self._point_to_win:
                indicators[i] = '✅'
        return {'name':self.title,'value':"\n".join([f"{indicators[i]}{emotes.num[round(e.points)]} {e.display}" for i,e in enumerate(self._entities)])}
      
    @property
    def field_detailled(self) -> dict:
        if self.is_played:
            indicators = ['❌' for _ in range(len(self._entities))]
        else:
            indicators = ['⬛' for _ in range(len(self._entities))]
        for i,entity in enumerate(self._entities):
            if round(entity.points) >= self._point_to_win:
                indicators[i] = '✅'
        return {'name':self.title,'value':"\n".join([f"{indicators[i]}{''.join([emotes.num[round(score)] for score in e.scores])} {e.display}" for i,e in enumerate(self._entities)])}
      
        
    @property
    def log_id(self) -> str:
        return f"[MATCH {self._round_idx}:{self._match_idx}]" 
    
    def get_entity(self, entity : Union[Entity,int]) -> Optional[Entity]:
        if isinstance(entity, Player) or isinstance(entity, Team):
            if entity in self._entities:
                return entity
            else:
                logging.error(f"{self.log_id} Error getting match : match {entity.log_id} does not belong to this round.")
        elif isinstance(entity, int):
            if entity < len(self._entities):
                return self._entities[entity]
            else:
                logging.error(f"{self.log_id} Error getting match by index : index {entity} is out of the range of this round ({len(self._entities)}).")
        else:
            raise TypeError('Argument "entity" should be either an "Entity", or a "int".')
            
    def add_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.add_score(value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during adding score.")
    
    def add_scores(self,entity : Entity, values : List[int]):
        entity = self.get_entity(entity)
        if entity:
            entity.add_scores(values)
        else:
            logging.error(f"{self.log_id} The above error occurred during adding scores.")
    
    def remove_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.remove_score(value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during removing score.")
    
    def remove_scores(self, entity : Entity, values : List[int]) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.remove_scores(values)
        else:
            logging.error(f"{self.log_id} The above error occurred during removing scores.")
            
    def set_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.set_score(value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during setting score.")
    
    def set_scores(self, entity : Entity, values : List[int]) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.set_scores(values)
        else:
            logging.error(f"{self.log_id} The above error occurred during setting scores.")
    
    def clear_score(self, index : int = 0) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.clear_score(index)
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing score.")
            
    def clear_scores(self) -> None:
        entity = self.get_entity(entity)
        if entity:
            entity.clear_scores()
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing scores.")
            
    async def move_to(self, channel : VocalGuildChannel = None, channels : List[VocalGuildChannel] = None):
        if channel and not channels:
            for entity in self._entities:
                await entity.move_to(channel)
        elif channels and not channel:
            if len(channels) == len(self._entities):
                for i,entity in enumerate(self._entities):
                    await entity.move_to(channels[i])
            else:
                logging.error(f"{self.log_id} Error on moving entities : size of 'channels' is not compatible with the number of entities")
        elif channel and channels:
            logging.error(f"{self.log_id} Error on moving entities : Only one of 'channel' or 'channels' should be used.")
        else:
            
            logging.error(f"{self.log_id} Error on moving entities : 'channel' and 'channels' are both None. One has to be set.'")
            
    def __iter__(self):
        yield 'round_idx', self.round_idx
        yield 'match_idx', self.match_idx
        yield 'entities', [dict(e) for e in self._entities]
        
#Class for rounds, with attributs for the matches
class Round:
    
    def __init__(self, tournament, round_idx : int, matches : List[Match] = None):
        self._tournament = tournament
        self._round_idx : int = round_idx
        self._matches : List[Match] = matches
        
    @property
    def round_idx(self) -> int:
        return self._round_idx
    
    @property
    def indexes(self) -> List[int]:
        return [self._round_idx]
    
    @property
    def matches(self) -> List[Match]:
        return self._matches
    
    @property
    def title(self) -> str:
        if self.is_played:
            return f"~~__**ROUND **__{emotes.num[self._round_idx+1]}~~"
        else:
            return f"__**ROUND **__{emotes.num[self._round_idx+1]}"

    @property
    def embed(self) -> disnake.Embed:
        return FastEmbed(
        title = self.title,
        color = color.gold,
        fields = [m.field for m in self._matches]
        )
            
    @property
    def embed_detailled(self) -> disnake.Embed:
        return FastEmbed(
        title = self.title,
        color = color.gold,
        fields = [m.field_detailled for m in self._matches]
        )
            
    @property
    def log_id(self) -> str:
        return f"[ROUND {self._round_idx}]" 
    
    @property
    def is_played(self) -> bool:
        played = True
        for match in self._matches:
            played = played and match.is_played
        return played
    
    def get_match(self, match : Union[Match,int]) -> Optional[Match]:
        if isinstance(match, Match):
            if match in self._matches:
                return match
            else:
                logging.error(f"{self.log_id} Error getting match : match {match.log_id} does not belong to this round.")
        elif isinstance(match, int):
            if match < len(self._matches):
                return self._matches[match]
            else:
                logging.error(f"{self.log_id} Error getting match by index : index {match} is out of the range of this round ({len(self._matches)}).")
        else:
            raise TypeError('Argument "match" should be either an "Match", or a "int".')
            
    def add_score(self, match : Union[Match,int], entity : Entity, value : int = 1, index : int = 0) -> None:
        match = self.get_match(match)
        if match:
            match.add_score(entity, value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during adding score.")
    
    def add_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]):
        match = self.get_match(match)
        if match:
            match.add_scores(entity, values)
        else:
            logging.error(f"{self.log_id} The above error occurred during adding scores.")
    
    def remove_score(self, match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        match = self.get_match(match)
        if match:
            match.remove_score(entity, value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during removing score.")
    
    def remove_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        match = self.get_match(match)
        if match:
            match.remove_scores(entity, values)
        else:
            logging.error(f"{self.log_id} The above error occurred during removing scores.")
                
    def set_score(self, match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        match = self.get_match(match)
        if match:
            match.set_score(entity, value, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during setting score.")
    
    def set_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        match = self.get_match(match)
        if match:
            match.set_scores(entity, values)
        else:
            logging.error(f"{self.log_id} The above error occurred during setting scores.")
    
    def clear_score(self, match : Union[Match,int], entity : Union[Entity,int], index : int = 0) -> None:
        match = self.get_match(match)
        if match:
            match.clear_score(entity, index)
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing score.")
            
    def clear_scores(self, match : Union[Match,int], entity : Union[Entity,int]) -> None:
        match = self.get_match(match)
        if match:
            match.clear_scores(entity)
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing scores.")
            
    async def move_to(self, channel : VocalGuildChannel = None, channels : List[VocalGuildChannel] = None):
        if channel and not channels:
            for match in self._matches:
                await match.move_to(channel)
        elif channels and not channel:
            if len(channels) == len(self._matches):
                for i,match in enumerate(self._matches):
                    await match.move_to(channels[i])
            else:
                logging.error(f"{self.log_id} Error on moving matches : size of 'channels' is not compatible with the number of matches.")
        elif channel and channels:
            logging.error(f"{self.log_id} Error on moving matches : Only one of 'channel' or 'channels' should be used.")
        else:
            
            logging.error(f"{self.log_id} Error on moving matches : 'channel' and 'channels' are both None. One has to be set.'")
            
    def __iter__(self):
        yield 'round_idx', self.round_idx
        yield 'entities', [dict(e) for e in self._matches]
        

class Tournament:
    
    def __init__(self, name : str, members : List[disnake.Member], nb_round : int = None, nb_matches_per_round : int = None, nb_teams_per_match : int = None, nb_players_per_team : int = None, size_of_scores : int = 1, weigths : List[float] = [1]):
        if len(weigths) != size_of_scores:
            raise ValueError('"Size of scores" and "weights" are not compatible.')
        
        self._name : str = name
        self._players : List[Player] = [Player(self, m, size_of_scores=size_of_scores) for m in members]
        for player in self._players:
            player.set_tournament(self)
        self._start_time : datetime = datetime.now()
        self._rounds : List[Round] = None
        self._current_round : Round = None
        self._size_of_scores : int = size_of_scores
        self._weights : List[float] = weigths
        self._nb_rounds : int = nb_round
        self._nb_matches_per_round : int = nb_matches_per_round
        self._nb_teams_per_match : int = nb_teams_per_match
        self._nb_players_per_team : int = nb_players_per_team

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def players(self) -> List[Player]:
        return self._players
    
    @property
    def rounds(self) -> List[Round]:
        return self._rounds
    
    @property
    def start_time(self) -> datetime:
        return self._start_time
    
    @property
    def current_round(self) -> Round:
        return self._current_round
    
    @property
    def size_of_scores(self) -> int:
        return self._size_of_scores
    
    @property
    def weights(self) -> List[int]:
        return self._weights
    
    @property
    def nb_rounds(self) -> int:
        return self._nb_rounds
    
    @property
    def nb_matches_per_round(self) -> int:
        return self._nb_matches_per_round
    
    @property
    def nb_teams_per_match(self) -> int:
        return self._nb_teams_per_match
    
    @property
    def nb_players_per_team(self) -> int:
        return self._nb_players_per_team
    
    @property
    def log_id(self) -> str:
        return f"[TOURNAMENT {self._name}]"
    
    @property
    def classement(self) -> disnake.Embed:
        pass
        
    @property
    def rules(self) -> disnake.Embed:
        pass
    
    def rounds_embeds(self, max : int = None, detailled : bool = False) -> List[disnake.Embed]:
        if max == None:
            max = self.nb_rounds
        embeds : List[disnake.Embed] = []
        if detailled:
            for i in range(max+1):
                embeds.append(self.rounds[i].embed_detailled)
        else:
            for i in range(max+1):
                embeds.append(self.rounds[i].embed)
        return embeds
    
    @abstractmethod
    def generate(self) -> None:
        pass
    
    def getRanking(self) -> List[Player]:
        return sorted(self._players, key=lambda x: (x.points, x.name), reverse=True)
    
    def shuffle_players(self) -> List[Player]:
        random.shuffle(self._players)
        return self._players
    
    def get_round(self, round : Union[Round,int]) -> Optional[Round]:
        if isinstance(round, Round):
            if round in self._rounds:
                return round
            else:
                logging.error(f"{self.log_id} Error getting round : round {round.log_id} does not belong to this tournament.")
        elif isinstance(round, int):
            if round < len(self._rounds):
                return self._rounds[round]
            else:
                logging.error(f"{self.log_id} Error getting round by index : index {round} is out of the range of this tournament ({len(self._rounds)}).")
        else:
            raise TypeError('Argument "round" should be either an "Round", or a "int".')
    
    def add_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        round = self.get_round(round)
        if round:
            round.add_score(match, entity, value, index)   
        else:
            logging.error(f"{self.log_id} The above error occurred during adding score.")
        self.save_state()
        
    def add_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], values : List[int]):
        round = self.get_round(round)
        if round:
            round.add_scores(match, entity, values)   
        else:
            logging.error(f"{self.log_id} The above error occurred during adding scores.")
        self.save_state()
    
    def remove_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        round = self.get_round(round)
        if round:
            round.remove_score(match, entity, value, index)   
        else:
            logging.error(f"{self.log_id} The above error occurred during removing score.")
        self.save_state()
    
    def remove_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        round = self.get_round(round)
        if round:
            round.remove_scores(match, entity, values)   
        else:
            logging.error(f"{self.log_id} The above error occurred during removing scores.")
        self.save_state()
                
    def set_score(self, round : Union[Round,int],  match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        round = self.get_round(round)
        if round:
            round.set_score(match, entity, value, index)   
        else:
            logging.error(f"{self.log_id} The above error occurred during setting score.")
        self.save_state()
    
    def set_scores(self, round : Union[Round,int],  match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        round = self.get_round(round)
        if round:
            round.set_scores(match, entity, values)   
        else:
            logging.error(f"{self.log_id} The above error occurred during setting scores.")
        self.save_state()
    
    def clear_score(self, round : Union[Round,int],  match : Union[Match,int], entity : Union[Entity,int], index : int = 0) -> None:
        round = self.get_round(round)
        if round:
            round.clear_score(match, entity, index)   
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing score.")
        self.save_state()
            
    def clear_scores(self, round : Union[Round,int],  match : Union[Match,int], entity : Union[Entity,int],) -> None:
        round = self.get_round(round)
        if round:
            round.clear_scores(match, entity)   
        else:
            logging.error(f"{self.log_id} The above error occurred during clearing scores.")
        self.save_state()
        
    @property
    def MSE(self) -> int:
        points_diff = []
        for i in range(len(self.players)):
            for j in range(len(self.players) - i -1):
                points_diff.append(pow(self.players[i].points-self.players[j].points,2))
        return sum(points_diff)/len(points_diff)
        
    @property
    def state_file(self) -> str:
        return f"cogs/Tournament/saves/{self._name}_state-{self._start_time}.json" 
    
    def __iter__(self):
        yield 'name', self._name
        yield 'start_time', str(self._start_time)
        yield 'nb_players', len(self._players)
        yield 'nb_rounds', self._nb_rounds
        yield 'nb_matches_per_round', self._nb_matches_per_round
        yield 'nb_teams_per_match', self._nb_teams_per_match
        yield 'nb_players_per_team', self._nb_players_per_team
        yield 'current_round_idx', self._rounds.index(self._current_round)
        yield 'players', [dict(p) for p in self._players]
        yield 'rounds', [dict(r) for r in self._rounds]
    
    def save_state(self) -> None:
        with open(self.state_file, 'w') as fp:
            json.dump(dict(self), fp, indent=1)


seeding = List[List[List[List[int]]]]    

#Class for the tournament, with attributs for the rounds and the players, and a method to get the players sorted by points 
class Tournament2v2Roll(Tournament):
    
    class Score:
        KILLS : int = 0
        TURRETS : int = 1
        CS : int = 2
        
    class Seeding:
        S4 : seeding = [
            [
                [[2, 3],[1, 4]]
            ],[
                [[1, 3],[2, 4]]
            ],[
                [[1, 2],[3, 4]]
            ]
        ]
    
        S5 : seeding = [
            [
                [[4, 5],[2, 3]]
            ],[
                [[1, 3],[2, 4]]
            ],[
                [[1, 5],[3, 4]]
            ],[
                [[2, 5],[1, 4]]
            ],[
                [[1, 2],[3, 5]]
            ]
        ]
        
        S8 : seeding = [
            [
                [[3, 4],[7, 8]],
                [[5, 6],[1, 2]]
            ],[
                [[6, 8],[5, 7]],
                [[1, 3],[2, 4]]
            ],[
                [[1, 4],[5, 8]],
                [[6, 7],[2, 3]]
            ],[
                [[4, 8],[2, 6]],
                [[3, 7],[1, 5]]
            ],[
                [[3, 8],[1, 6]],
                [[2, 5],[4, 7]]
            ],[
                [[2, 8],[3, 5]],
                [[4, 6],[1, 7]]
            ],[
                [[1, 8],[2, 7]],
                [[4, 5],[3, 6]]
            ]
        ]

    def __init__(self, name : str, members : List[disnake.Member], ordered : bool = False):
    
        self._ordered : bool = ordered

        if len(members) == 4:
            self._seeding : seeding = Tournament2v2Roll.Seeding.S4
        elif len(members) == 5:
            self._seeding : seeding = Tournament2v2Roll.Seeding.S5
        elif len(members) == 8:
            self._seeding : seeding = Tournament2v2Roll.Seeding.S8 

        
        super().__init__(name, members,
                         nb_round=len(self._seeding), 
                         nb_matches_per_round=len(self._seeding[0]), 
                         nb_teams_per_match=2,
                         nb_players_per_team=2, 
                         size_of_scores=3, 
                         weigths=[1.01,1,0.99])
        
        logging.info(f"{self.log_id} Initializing tournament {self._name} of {len(self._players)} players.")
        
    def generate(self) -> None:
        if not self._ordered:
            self.shuffle_players()
        self._rounds = []
        for round_idx in range(self._nb_rounds):
            matches = []
            for match_idx in range(self._nb_matches_per_round):
                teams = []
                for team_idx in range(2):
                    teams.append(Team(self,[self._players[self._seeding[round_idx][match_idx][team_idx][0]-1],self._players[self._seeding[round_idx][match_idx][team_idx][1]-1]],round_idx,match_idx,team_idx,3))
                matches.append(Match(self, round_idx, match_idx, teams))
            self._rounds.append(Round(self, round_idx, matches))
        self._current_round = self._rounds[0]
        if self._ordered:
            logging.info(f"{self.log_id} Round generated using the following players order: " + ",".join([str(p.id) for p in self._players]))
        else:
            logging.info(f"{self.log_id} Round generated using random order")
        self.save_state()
             
    @property
    def classement(self) -> disnake.Embed:
        sorted_player = self.getRanking()
        ranks = []
        for i in range(len(sorted_player)):
            if i == 0:
                ranks.append(f"{emotes.rank[i]}")
            elif sorted_player[i].points == sorted_player[i-1].points:
                ranks.append(ranks[-1])
            else:
                ranks.append(f"{emotes.rank[i]}")
        return FastEmbed(
            title = "__**CLASSEMENT**__",
            color = color.gold,
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.display}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}**" for p in sorted_player]),'inline':True}
            ]
        )
   
    @property
    def detailedClassement(self) -> disnake.Embed:
        sorted_player = self.getRanking()
        ranks = []
        for i in range(len(sorted_player)):
            if i == 0:
                ranks.append(f"{emotes.rank[i]}")
            elif sorted_player[i].points == sorted_player[i-1].points:
                ranks.append(ranks[-1])
            else:
                ranks.append(f"{emotes.rank[i]}")
        return FastEmbed(
            title = "__**CLASSEMENT**__",
            color = color.gold,
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.display}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}** *({p.scores[self.Score.KILLS]}-{p.scores[self.Score.TURRETS]}-{p.scores[self.Score.CS]})*" for p in sorted_player]),'inline':True}
            ]
        )
        
    @property
    def rules(self) -> disnake.Embed:
        return FastEmbed(
            title = ":scroll: __**RÈGLES**__ :scroll:",
            color = color.gold,
            fields = [
                {
                    'name':"__**Format du tournoi**__",
                    'value':f"""Le tournoi se joue individuellement mais les matchs se font par __équipe de 2__. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            ✅ __avec__ chaque autres joueurs exactement :one: fois
                            :x: __contre__ chaque autres joueurs exactement :two: fois.
                            Il y aura donc __ {self._nb_rounds} rounds__ avec __{self._nb_matches_per_round} matchs__ en parallèles."""
                },
                {
                    'name':"__**Format d'un match**__",
                    'value':"""Les matchs sont en __BO1__ se jouant en 2v2 selon le format suivant :
                            🌍 __Map__ : Abime hurlante
                            👓 __Mode__ : Blind
                            ❌ __Bans__ : 3 par équipe (à faire via le chat dans le lobby **pré-game**)"""
                },
                {
                    'name':"__**Règles d'un match**__",
                    'value':"""⛔ Interdiction de prendre les healts __extérieurs__ (ceux entre la **T1** et la **T2**).
                            ✅ Le suicide est autorisé et ne compte pas comme un kill.
                            ✅ L'achat d'objet lors d'une mort est autorisé."""
                },
                {
                    'name':"__**Score d'un match**__",
                    'value':"""Le match se finit lorsque l'une des deux équipes a __2 points__. Une équipe gagne :one: point pour :
                            ⚔️  __Chaque kills__
                            🧱 __1e tourelle de la game__
                            💰 __1e **joueur** d'une équipe à 100cs__"""
                },
                {
                    'name':"__**Score personnel**__",
                    'value':f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur (indépendamment de qui a marqué le point).
                            À la fin des {self._nb_rounds} rounds, c'est les points personnels qui détermineront le classement."""
                },
                {
                    'name':"__**Égalité**__",
                    'value':f"""En cas d'égalité, on départage avec __kills > Tourelles > 100cs__.
                            En cas d'égalité parfaite pour la première ou deuxième place, un __1v1__ en BO1 est organisé (même règles, mais _1 point__ suffit pour gagner)."""
                },
                {
                    'name':"__**Phase finale**__",
                    'value':f"""À la fin des {self._nb_rounds} rounds, un BO5 en __1v1__ sera joué entre le 1er et le 2ème du classement pour derterminer le grand vainqueur. Pour chaque deux points d'écart, un match d'avance sera accordé au 1er du classement (jusqu'à un maximum de 2 matchs d'avance).
                    *__Exemple :__
                    **Lỳf** est premier avec __14 points__ mais **Gay Prime** est deuxième avec __11 points__\n⏭️ BO5 commençant à **1-0** en faveur de **Lỳf**.*"""
                }
            ]
        )
        

    def nextRound(self) -> Round:
        self._current_round = self._rounds[self._rounds.index(self._current_round) + 1]
        return self._current_round
    
    def previousRound(self) -> Round:
        self._current_round = self._rounds[self._rounds.index(self._current_round) - 1]
        return self._current_round
    
    
    @staticmethod
    async def load_from_save(inter : disnake.ApplicationCommandInteraction, file : disnake.File) -> Optional[Tournament]:
        try:
            save : dict = json.loads(file.fp.read())
            members : List[disnake.Member] = []
            for member in save.get("players"):
                members.append(await inter.guild.fetch_member(member.get("id")))
            tournament : Tournament2v2Roll = Tournament2v2Roll(save.get("name"), members, ordered = True)
            tournament.generate()
            for round in save.get('rounds'):
                for match in round.get('entities'):
                    for team in match.get("entities"):
                        players : List[dict] = team.get('players')
                        if (players[0].get('id') == tournament.rounds[round.get('round_idx')].matches[match.get('match_idx')].teams[team.get("team_idx")].players[0].id
                        and players[1].get('id') == tournament.rounds[round.get('round_idx')].matches[match.get('match_idx')].teams[team.get("team_idx")].players[1].id):
                            tournament.add_scores(round.get("round_idx"),match.get('match_idx'),team.get("team_idx"),team.get('scores'))
                            
                        else:
                            raise KeyError
                        
            for player in tournament.players:
                for player_dict in save.get('players'):
                    if player.id == player_dict.get('id') and player.scores != player_dict.get('scores'):
                            raise ValueError
            for round in tournament.rounds:
                if not round.is_played:
                    tournament._current_round = round
                    break
            return tournament
        except:
            return None
                
            
            

        
        


    
