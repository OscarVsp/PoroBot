from enum import Enum
import random
import disnake
import modules.FastSnake as FS
from modules.FastSnake.ShadowMember import ShadowMember, VocalGuildChannel, Components
import logging
from typing import List, Union, Optional, Sequence, overload

class State(Enum):
    
    INIT = 0
    SET = 1
    STARTED = 2
    ENDED = 3
    
    def __gt__(self, other):
        try:
            return self.value > other.value
        except:
            pass
        try:
            if isinstance(other, int):
                return self.value > other
        except:
            pass
        return NotImplemented

    def __lt__(self, other):
        try:
            return self.value < other.value
        except:
            pass
        try:
            if isinstance(other, int):
                return self.value < other
        except:
            pass
        return NotImplemented

    def __ge__(self, other):
        try:
            return self.value >= other.value
        except:
            pass
        try:
            if isinstance(other, int):
                return self.value >= other
            if isinstance(other, str):
                return self.name == other
        except:
            pass
        return NotImplemented

    def __le__(self, other):
        try:
            return self.value <= other.value
        except:
            pass
        try:
            if isinstance(other, int):
                return self.value <= other
            if isinstance(other, str):
                return self.name == other
        except:
            pass
        return NotImplemented

    def __eq__(self, other):
        try:
            return self.value == other.value
        except:
            pass
        try:
            if isinstance(other, int):
                return self.value == other
            if isinstance(other, str):
                return self.name == other
        except:
            pass
        return NotImplemented

class SaveLoadError(Exception):
    pass

class PlayersNotSetError(Exception):
    def __init__(self):
        self.message = "Players are not set"
        super().__init__()
        
class UnknownRoundError(Exception):
    def __init__(self):
        self.message = "This round does not belong to this phase"
        super().__init__()
        
class UnknownMatchError(Exception):
    def __init__(self):
        self.message = "This match does not belong to this phase"
        super().__init__()
        
class UnknownEntityError(Exception):
    def __init__(self):
        self.message = "This entity does not belong to this phase"
        super().__init__()
        
class ScoreIndexOutOfRange(Exception):
    def __init__(self):
        self.message = "The index of the score is out of range"
        super().__init__()
        
class ScoreSizeNotMatching(Exception):
    def __init__(self):
        self.message = "The size of the score don't match"
        super().__init__()
        
class Player(ShadowMember):
    
    def __init__(self, member : disnake.Member, size_of_scores : int = 1, weights : List[float] = [1]):
        super().__init__(member)
        self._scores : List[int] = [0 for _ in range(size_of_scores)]
        self._weights : List[float] = weights
        
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
        return sum([self._scores[i]*self._weights[i] for i in range(len(self._scores))])

    
    @property
    def log_id(self) -> str:
        return f"[PLAYER {self.name}:{self.id}]"
        
    def add_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] += value
        else:
            raise ScoreIndexOutOfRange
            
    def add_scores(self, values : List[int]):
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self._scores[i] += value
        else:
            raise ScoreSizeNotMatching
            
    def remove_score(self, value : int = 1, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] -= value
        else:
            raise ScoreIndexOutOfRange
    
    def remove_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            for i,value in enumerate(values):
                self._scores[i] -= value
        else:
            raise ScoreSizeNotMatching       
    
    def set_score(self, value : int, index : int) -> None:
        if len(self._scores) > index:
            self._scores[index] = value
        else:
            raise ScoreIndexOutOfRange
            
    def set_scores(self, values : List[int]) -> None:
        if len(self._scores) == len(values):
            self._scores = values
        else:
            raise ScoreSizeNotMatching
      
    def clear_score(self, index : int = 0) -> None:
        if len(self._scores) > index:
            self._scores[index] = 0
        else:
            raise ScoreIndexOutOfRange
    
    def clear_scores(self) -> None:
        self._scores = [0 for _ in range(len(self._scores))]
    
    def __iter__(self):
        yield 'display_name', self.display_name
        yield 'name', self.name
        yield 'id', self.id
        yield 'scores', self._scores
        
class Team:
    
    def __init__(self, phase, players : List[Player], round_idx : int, match_idx : int, team_idx : int, size_of_scores : int = 1):
        self._phase : Phase = phase
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
    def scores_description(self) -> str:
        descriptor = self._phase._scores_descriptor
        if descriptor:      
            text = ""
            for i in range(len(self._scores)):
                if self._scores[i]:
                    text += f"{self._scores[i]} {descriptor[i]}, "
            if text == "":
                return "Nothing"
            return text[:len(text)-2]
        return str(self._scores)
    
    @property
    def points(self) -> int:
        return sum([self._scores[i]*self.phase.weights[i] for i in range(len(self._scores))])
    
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
            
    async def move_to(self, channel : VocalGuildChannel):
        for player in self._players:
            try:
                await player.move_to(channel)
            except disnake.errors.HTTPException:
                pass
    
            
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
        msg = None
        for player in self._players:
            msg = await player.send(
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
        return msg
        
    def __iter__(self):
        yield 'round_idx', self.round_idx
        yield 'match_idx', self.match_idx
        yield 'team_idx', self.team_idx
        yield 'players', [dict(p) for p in self._players]
        yield 'scores', self._scores
                       
Entity = Union[Player,Team]
    
    
class Container:    
        
    @property
    def state(self) -> State:
        pass
    
#Class for a match between two teams, with attributs for the teams and the winner, and method to add points to a team
class Match(Container):
    def __init__(self, phase, round_idx : int, match_idx : int, entities : List[Entity] = None):
        self._phase : Phase = phase
        self._round_idx : int = round_idx
        self._match_idx : int = match_idx
        self._entities : List[Entity] = entities

    @property
    def state(self) -> State:
        if self._entities:
            started = False
            for entity in self._entities:
                if round(entity.points) >= self._phase.nb_point_to_win_match:
                    return State.ENDED
                if entity.points > 0:
                    started = True
            if started:
                return State.STARTED
            else: 
                return State.SET
        else:
            return State.INIT

            
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
        return self._phase.nb_point_to_win_match
    
    @property
    def title(self) -> str:
        return f"__MATCH __{FS.Emotes.Alpha[self._match_idx]}"

    @property
    def field(self) -> dict:
        if self.state == State.ENDED:
            indicators = ['❌' for _ in range(len(self._entities))]
        else:
            indicators = ['⬛' for _ in range(len(self._entities))]
        for i,entity in enumerate(self._entities):
            if round(entity.points) >= self._phase.nb_point_to_win_match:
                indicators[i] = '✅'
        return {'name':self.title,'value':"\n".join([f"{indicators[i]}{FS.Emotes.Num(round(e.points))} {e.display}" for i,e in enumerate(self._entities)]),'inline':True}
      
    @property
    def field_detailled(self) -> dict:
        if self.state == State.ENDED:
            indicators = ['❌' for _ in range(len(self._entities))]
        else:
            indicators = ['⬛' for _ in range(len(self._entities))]
        for i,entity in enumerate(self._entities):
            if round(entity.points) >= self._phase.nb_point_to_win_match:
                indicators[i] = '✅'
        return {'name':self.title,'value':"\n".join([f"{indicators[i]}{''.join([FS.Emotes.Num(round(score)) for score in e.scores])} {e.display}" for i,e in enumerate(self._entities)]),'inline':True}
      
        
    @property
    def log_id(self) -> str:
        return f"[MATCH {self._round_idx}:{self._match_idx}]" 
    
    def get_entity(self, entity : Union[Entity,int]) -> Optional[Entity]:
        if isinstance(entity, Player) or isinstance(entity, Team):
            if entity in self._entities:
                return entity
            else:
                raise UnknownEntityError
        elif isinstance(entity, int):
            return self._entities[entity]
        else:
            raise TypeError('Argument "entity" should be either an "Entity", or a "int".')
            
    def add_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        self.get_entity(entity).add_score(value, index)
     
    def add_scores(self,entity : Entity, values : List[int]):
        self.get_entity(entity).add_scores(values)
       
    def remove_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        self.get_entity(entity).remove_score(value, index)
       
    def remove_scores(self, entity : Entity, values : List[int]) -> None:
        self.get_entity(entity).remove_scores(values)
            
    def set_score(self, entity : Entity, value : int = 1, index : int = 0) -> None:
        self.get_entity(entity).set_score(value, index)
       
    def set_scores(self, entity : Entity, values : List[int]) -> None:
        self.get_entity(entity).set_scores(values)
        
    def clear_score(self, entity : Entity, index : int = 0) -> None:
        self.get_entity(entity).clear_score(index)
            
    def clear_scores(self, entity : Entity) -> None:
        self.get_entity(entity).clear_scores()
            
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
class Round(Container):
    
    def __init__(self, phase, round_idx : int, matches : List[Match] = None):
        super().__init__()
        self._phase : Phase = phase
        self._round_idx : int = round_idx
        self._matches : List[Match] = matches
        
    @property
    def state(self) -> State:
        if self._matches:
            seted = True
            started = False
            ended = True
            
            for match in self._matches:
                seted = seted and (match.state >= State.SET)
                started = started or (match.state >= State.STARTED)
                ended = ended and (match.state == State.ENDED)
                
            if ended:
                return State.ENDED
            elif started:
                return State.STARTED
            elif seted:
                return State.SET
        
        return State.INIT
        
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
        return f"⚔️ __**ROUND **__{FS.Emotes.Num(self._round_idx+1)}"

    @property
    def embed(self) -> disnake.Embed:
        return FS.Embed(
        title = self.title,
        color = self.embed_color,
        fields = [m.field for m in self._matches]
        )
            
    @property
    def embed_detailled(self) -> disnake.Embed:
        return FS.Embed(
        title = self.title,
        color = self.embed_color,
        fields = [m.field_detailled for m in self._matches]
        )
        
    @property
    def embed_color(self) -> disnake.Color:
        if self.state == State.ENDED:
            return disnake.Colour.lighter_grey()
        elif self.round_idx == 0 or self._phase.rounds[self._phase.rounds.index(self)-1].state == State.ENDED:
            return disnake.Colour.green()
        return disnake.Embed.Empty
        
            
    @property
    def log_id(self) -> str:
        return f"[ROUND {self._round_idx}]" 
    
    def get_match(self, match : Union[Match,int]) -> Optional[Match]:
        if isinstance(match, Match):
            if match in self._matches:
                return match
            else:
                raise UnknownMatchError
        elif isinstance(match, int):
            return self._matches[match]
        else:
            raise TypeError('Argument "match" should be either an "Match", or a "int".')
            
    def add_score(self, match : Union[Match,int], entity : Entity, value : int = 1, index : int = 0) -> None:
        self.get_match(match).add_score(entity, value, index)
    
    def add_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]):
        self.get_match(match).add_scores(entity, values)

    def remove_score(self, match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        self.get_match(match).remove_score(entity, value, index)
        
    def remove_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        self.get_match(match).remove_scores(entity, values)
                
    def set_score(self, match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        self.get_match(match).set_score(entity, value, index)
        
    def set_scores(self, match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        self.get_match(match).set_scores(entity, values)
    
    def clear_score(self, match : Union[Match,int], entity : Union[Entity,int], index : int = 0) -> None:
        self.get_match(match).clear_score(entity, index)
            
    def clear_scores(self, match : Union[Match,int], entity : Union[Entity,int]) -> None:
        self.get_match(match).clear_scores(entity)
            
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
        

class Phase(Container):
    
    def __init__(self, stage_idx : int, phase_idx : int, name : str, size : int, nb_round : int = None, nb_matches_per_round : int = None, nb_teams_per_match : int = None, nb_players_per_team : int = None, size_of_scores : int = 1, weigths : List[float] = [1], scores_descriptor : List[str] = None, score_emoji : List[str] =None,  nb_point_to_win_match : int = 2):
        super().__init__()
        if len(weigths) != size_of_scores:
            raise ValueError('"Size of scores" and "weights" are not compatible.')
        self._stage_idx : int = stage_idx
        self._phase_idx : int = phase_idx
        self._name : str = name
        self._size : int = size
        self._players : List[Player] = None
        self._role : disnake.Role = None
        self._rounds : List[Round] = None
        self._size_of_scores : int = size_of_scores
        self._scores_descriptor : List[str] = scores_descriptor if scores_descriptor else ['point']
        self._score_emoji : List[str] = score_emoji if score_emoji else ["💎" for _ in range(size_of_scores)]
        self._weigths : List[float] = weigths
        self._nb_rounds : int = nb_round
        self._nb_matches_per_round : int = nb_matches_per_round
        self._nb_teams_per_match : int = nb_teams_per_match
        self._nb_players_per_team : int = nb_players_per_team
        self._nb_point_to_win_match : int = nb_point_to_win_match
        self._last_state : dict = None
        self.view : disnake.ui.View = None
        self.start_flag : bool = False
        
    async def set_role(self, role : disnake.Role) -> None:
        self._role : disnake.Role = role
        self._players : List[Player] = [Player(member, size_of_scores=self._size_of_scores, weights=self._weigths) for member in role.members]
        self.generate()
        await self.view.generate()
        
    async def start(self) -> None:
        self.start_flag = True
        await self.view.update()
        
    async def delete(self) -> None:
        await self.view.delete_cat()
        
        
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def emotes(self) -> str:
        return f"{FS.Assets.Emotes.Num(self.stage_idx+1)}{FS.Assets.Emotes.Alpha[self.phase_idx]}"
    
    @property
    def role(self) -> disnake.Role:
        return self._role
    
    @property
    def stage_idx(self) -> int:
        return self._stage_idx
    
    @property
    def phase_idx(self) -> int:
        return self._phase_idx
    
    @property
    def title(self) -> str:
        return f"{self.stage_idx+1}{chr(ord('A') + self.phase_idx)} - {self.name}"
    
    @property
    def title_emote(self) -> str:
        return f"{self.emotes} {self.name}"
    
    @property
    def score_desriptor(self) -> List[str]:
        return self._scores_descriptor
    
    @property
    def score_emoji(self) -> List[str]:
        return self._score_emoji
    
    @property
    def nb_point_to_win_match(self) -> int:
        return self._nb_point_to_win_match
    
    @staticmethod
    def rank_emotes(sorted_players : List[Player]) -> List[str]:
        ranks = []
        for i in range(len(sorted_players)):
            if i == 0:
                ranks.append(f"{FS.Emotes.Rank(i)}")
            elif sorted_players[i].points == sorted_players[i-1].points:
                ranks.append(ranks[-1])
            else:
                ranks.append(f"{FS.Emotes.Rank(i)}")
        return ranks

    @property
    def state(self) -> State:
        if self._players and self._rounds and self.start_flag:
            seted = True
            started = False
            ended = True
            
            for round in self._rounds:
                seted = seted and (round.state >= State.SET)
                started = started or (round.state >= State.STARTED)
                ended = ended and (round.state == State.ENDED)
                
            if ended:
                return State.ENDED
            elif started:
                return State.STARTED
            elif seted:
                return State.SET
        
        return State.INIT

    @property
    def size(self) -> int:
        return self._size

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
    def current_round(self) -> Optional[Round]:
        for round in self._rounds:
            if round.state == State.STARTED:
                return round
        return None
    
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
        return f"[PHASE {self._name}]"
    
    @property
    def last_state(self) -> dict:
        return self._last_state
    
    @property
    def classement_embed(self) -> disnake.Embed:
        if self.state == State.INIT:
            return FS.Embed(
                title="🏆 __**CLASSEMENT**__ 🏆",
                color = disnake.Colour.gold(),
                description="*Le classement sera affiché ici lorsque les participants auront été sélectionnés.*"
            )
        else:
            return None
       
    @property
    def rounds_embeds(self) -> List[disnake.Embed]:
        if self.state <= State.SET:
            return FS.Embed(
                title="📅 __**ROUNDS**__",
                color = disnake.Colour.lighter_grey(),
                description="*Les rounds seront affichés ici une fois que la phase aura commencée.*"
            )
        else:
            return None
    
    @property
    def rules_embed(self) -> disnake.Embed:
        return None  
    
    @property
    def admin_embeds(self) -> List[disnake.Embed]:
        if self.state == State.INIT:
            return FS.Embed(
                title="__**ADMIN DASHBOARD**__",
                color = disnake.Colour.lighter_grey(),
                description="*Utilise le dashboard du tournoi pour sélectionner les participants du tournoi et commencer la phase.*"  #TODO link
            )
        else:
            return None
    
    def generate(self) -> None:
        pass
    
    def getRanking(self) -> List[Player]:
        return sorted(self._players, key=lambda x: (x.points, x.name), reverse=True)
    
    def shuffle_players(self) -> List[Player]:
        random.shuffle(self._players)
        return self._players
    
    def get_round(self, round : Union[Round,int]) -> Optional[Round]:
        if self.players:
            if isinstance(round, Round):
                if round in self._rounds:
                    return round
                else:
                    raise UnknownRoundError
            elif isinstance(round, int):
                return self._rounds[round]
            else:
                raise TypeError('Argument "round" should be either an "Round", or a "int".')
        else:
            raise PlayersNotSetError
    
    def add_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        self.get_round(round).add_score(match, entity, value, index)   
        
    def add_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], values : List[int]):
        self.get_round(round).add_scores(match, entity, values)   
    
    def remove_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        self.get_round(round).remove_score(match, entity, value, index)   
    
    def remove_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        self.get_round(round).remove_scores(match, entity, values)   
      
    def set_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], value : int = 1, index : int = 0) -> None:
        self.get_round(round).set_score(match, entity, value, index)   
   
    def set_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], values : List[int]) -> None:
        self.get_round(round).set_scores(match, entity, values)   
      
    def clear_score(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int], index : int = 0) -> None:
        self.get_round(round).clear_score(match, entity, index)   

    def clear_scores(self, round : Union[Round,int], match : Union[Match,int], entity : Union[Entity,int],) -> None:
        self.get_round(round).clear_scores(match, entity)   
        
    @property
    def MSE(self) -> int:
        points_diff = []
        for i in range(len(self.players)):
            for j in range(len(self.players) - i -1):
                points_diff.append(pow(self.players[i].points-self.players[j].points,2))
        return sum(points_diff)/len(points_diff)
            
    def __iter__(self):
        yield 'name', self._name
        yield 'guild_id', self._players[0].guild.id
        yield 'nb_players', len(self._players)
        yield 'nb_rounds', self._nb_rounds
        yield 'nb_matches_per_round', self._nb_matches_per_round
        yield 'nb_teams_per_match', self._nb_teams_per_match
        yield 'nb_players_per_team', self._nb_players_per_team
        yield 'players', [dict(p) for p in self._players]
        yield 'rounds', [dict(r) for r in self._rounds]
    
    def save_state(self) -> None:
        self._last_state : dict = dict(self)
  
    def restore_from_last_state(self) -> None:
        for round in self.last_state.get('rounds'):
            for match in round.get('entities'):
                for team in match.get("entities"):
                    players : List[dict] = team.get('players')
                    if (players[0].get('id') == self.rounds[round.get('round_idx')].matches[match.get('match_idx')].teams[team.get("team_idx")].players[0].id
                    and players[1].get('id') == self.rounds[round.get('round_idx')].matches[match.get('match_idx')].teams[team.get("team_idx")].players[1].id):
                        self.set_scores(round.get("round_idx"),match.get('match_idx'),team.get("team_idx"),team.get('scores'))   
  
class Phase2v2Roll(Phase):
 
    class Score:
        KILLS : int = 0
        TURRETS : int = 1
        CS : int = 2
        
    class Seeding:
        S4 : List[List[List[List[int]]]] = [
            [
                [[2, 3],[1, 4]]
            ],[
                [[1, 3],[2, 4]]
            ],[
                [[1, 2],[3, 4]]
            ]
        ]
    
        S5 : List[List[List[List[int]]]] = [
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
        
        S8 : List[List[List[List[int]]]] = [
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

    def __init__(self, stage_idx : int, phase_idx : int, size):

        if size == 4:
            self._seeding : List[List[List[List[int]]]] = Phase2v2Roll.Seeding.S4
        elif size == 5:
            self._seeding : List[List[List[List[int]]]] = Phase2v2Roll.Seeding.S5
        elif size == 8:
            self._seeding : List[List[List[List[int]]]] = Phase2v2Roll.Seeding.S8 

        
        super().__init__(
            stage_idx,
            phase_idx,
            "2v2 Roll",
            size,
            nb_round=len(self._seeding), 
            nb_matches_per_round=len(self._seeding[0]), 
            nb_teams_per_match=len(self._seeding[0][0]),
            nb_players_per_team=len(self._seeding[0][0][0]), 
            size_of_scores=3, 
            weigths=[1.001,1,0.989],
            scores_descriptor=["kill(s)","turret(s)","cs"],
            score_emoji=["⚔️","🧱","🧙‍♂️"],
            nb_point_to_win_match=2
        )
           
    def generate(self) -> None:
        if self.players == None:
            raise PlayersNotSetError
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
        self.save_state()
        
    @property
    def classement_embed(self) -> disnake.Embed:
        embed = super().classement_embed
        if embed:
            return embed
        sorted_players : List[Player] = self.getRanking()
        ranks = self.rank_emotes(sorted_players)
        return FS.Embed(
            title = "🏆 __**CLASSEMENT**__ 🏆",
            color = disnake.Colour.gold(),
            fields=[
                {
                    'name':"🎖️➖__*Joueurs*__",
                    'value':"\n".join([f"{ranks[i]}➖**{p.display}**" for i,p in enumerate(sorted_players)]),
                    'inline':True
                },
                {
                    'name':"💎",
                    'value':"\n".join([f" **{round(p.points)}**" for p in self.getRanking()]),
                    'inline':True
                },
                {
                    'name':"➖➖➖➖➖➖➖➖➖➖➖➖➖",
                    'value':"""> **Calcul des points**
                    > 💎 Points **=** ⚔️ Kill  **+**  🧱 Tour  **+**  🧙‍♂️ 100cs
                    > **En cas d'égalité**
                    > ⚔️ Kill  **>**  🧱 Tour  **>**  🧙‍♂️ 100cs
                    """,
                    'inline':False
                }
            ]
        )
   
    @property
    def rounds_embeds(self) -> List[disnake.Embed]:
        embed = super().rounds_embeds
        if embed:
            return [embed]
        return [round.embed for round in self.rounds]
       
    @property
    def rules_embed(self) -> disnake.Embed:
        return FS.Embed(
            title = ":scroll: __**RÈGLES**__ :scroll:",
            color = disnake.Colour.purple(),
            fields = [
                {
                    'name':"__**Format du tournoi**__",
                    'value':f"""Le tournoi se joue individuellement mais les matchs se font par **équipe de 2**. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            > ✅ __avec__ chaque autres joueurs exactement :one: fois
                            > :x: __contre__ chaque autres joueurs exactement :two: fois.
                            Il y aura donc **{self._nb_rounds} rounds**"""+(f"avec **{self._nb_matches_per_round} matchs** en parallèles." if self._nb_matches_per_round>1 else ".")
                },
                {
                    'name':"__**Format d'un match**__",
                    'value':"""Les matchs sont en **BO1** se jouant en 2v2 selon le format suivant :
                            > 🌍 __Map__ : Abime hurlante
                            > 👓 __Mode__ : Blind
                            > ❌ __Bans__ : 3 par équipe *(à faire via le chat dans le lobby **pré-game**)*"""
                },
                {
                    'name':"__**Règles d'un match**__",
                    'value':"""> ⛔ __Interdiction__ de prendre les healts **extérieurs** *(ceux entre la **T1** et la **T2**)*.
                            > ✅ __Le suicide__ est autorisé et ne compte pas comme un kill.
                            > ✅ __L'achat d'objet__ lors d'une mort est autorisé."""
                },
                {
                    'name':"__**Score d'un match**__",
                    'value':"""Le match se finit lorsque l'une des deux équipes a **2 points**. Une équipe gagne **1 point** pour :
                            > ⚔️  __Chaque kills__
                            > 🧱 __1e tourelle de la game__
                            > 🧙‍♂️ __1e joueur d'une équipe à 100cs__"""
                },
                {
                    'name':"__**Score personnel**__",
                    'value':f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur *(indépendamment de qui a marqué le point)*.
                            À la fin des {self._nb_rounds} rounds, c'est les points personnels qui détermineront le classement."""
                },
                {
                    'name':"__**Égalité**__",
                    'value':f"""En cas d'égalité, on départage avec ⚔️ **kills** > 🧱 **Tourelles** > 🧙‍♂️ **100cs**.
                            En cas d'égalité parfaite pour la 2ième place, un **1v1** en BO1 est organisé *(même règles, mais **1 point** suffit pour gagner)*."""
                },
                {
                    'name':"__**Phase finale**__",
                    'value':f"""À la fin des {self._nb_rounds} rounds, un BO5 en **1v1** sera joué entre le **1er** et le **2ième** du classement pour derterminer le grand vainqueur. Pour chaque **{round((self._nb_rounds*2)/5)} point(s)** d'écart, un match d'avance sera accordé au **1er** *(jusqu'à un maximum de 2 matchs d'avance)*.
                    > __*Exemple :*__
                    > **Lỳf** est 1er avec **{self._nb_rounds*2} points** mais **Gay Prime** est 2ième avec **{self._nb_rounds*2-round((self._nb_rounds*2)/5)} points**
                    > ⏭️ **BO5** commençant à **1-0** en faveur de **Lỳf**."""
                }
            ]
        )
         
    @property
    def admin_embeds(self) -> List[disnake.Embed]:
        embed = super().admin_embeds
        if embed:
            return [embed]
        embeds = [round.embed_detailled for round in self.rounds]
        sorted_players : List[Player] = self.getRanking()
        ranks = self.rank_emotes(sorted_players)
        embeds.append(FS.Embed(
            title = "🏆 __**CLASSEMENT**__🏆 ",
            color = disnake.Colour.gold(),
            fields=[
                {
                    'name':"🎖️➖__*Joueurs*__",
                    'value':"\n".join([f"{ranks[i]}➖**{p.display}**" for i,p in enumerate(sorted_players)]),
                    'inline':True
                },
                {
                    'name':"💎 __**Points**__",
                    'value':"\n".join([f"**{round(p.points)}** *({p.scores[self.Score.KILLS]}  {p.scores[self.Score.TURRETS]}  {p.scores[self.Score.CS]})*" for p in self.getRanking()]),
                    'inline':True
                },
                {
                    'name':"➖➖➖➖➖➖➖➖➖➖➖➖➖",
                    'value':f"> MSE = {self.MSE}",
                    'inline':False
                }
            ]
        ))
        return embeds
    
                  
  
class Stage(Container):
    
    def __init__(self):
        self._phases : List[Phase] = []       
        
    @property
    def state(self) -> State:
        if self._phases:
            seted = True
            started = False
            ended = True
            
            for phase in self._phases:
                seted = seted and (phase.state >= State.SET)
                started = started or (phase.state >= State.STARTED)
                ended = ended and (phase.state == State.ENDED)
                
            if ended:
                return State.ENDED
            elif started:
                return State.STARTED
            elif seted:
                return State.SET
        
        return State.INIT
        
    @property
    def phases(self) -> List[Phase]:
        return self._phases
    
    def add_phase(self, phase : Phase) -> None:
        self._phases.append(phase)
  
                
class Tournament:
    
    def __init__(self, name : str, role : disnake.Role):
        self._name : str = name
        self._role: disnake.Role = role
        self._stages : List[Stage] = []
        
    def add_phase(self, phase : Phase, stage_index : int = None):
        if stage_index == None:
            stage_index = len(self._stages)

        if stage_index < len(self._stages):
            self._stages[stage_index].add_phase(phase)
        elif stage_index == len(self._stages):
            new_stage : Stage = Stage()
            new_stage.add_phase(phase)
            self._stages.append(new_stage)
        else:
            raise IndexError("Index cannot be higher that the current size of phase")
        
    async def remove_phase(self, phase_to_remove : Phase):
        for stage in self._stages:
            for phase in stage._phases:
                if phase == phase_to_remove:
                    stage._phases.remove(phase)
                    await phase.delete()
                    if len(stage._phases) == 0:
                        self._stages.remove(stage)
                    return
        
    
                
    @property
    def stages(self) -> List[Stage]:
        return self._stages
        
    @property
    def phases(self) -> List[Phase]:
        phases : list[Phase] = []
        for stage in self._stages:
            for phase in stage.phases:
                phases.append(phase)
        return phases

    @property
    def role(self) -> disnake.Role:
        return self._role
    
    @property
    def name(self) -> str:
        return self._name


    @property
    def embed(self) -> disnake.Embed:
        fields = []
        
        for stage in self._stages:
            phases = stage.phases
            if len(phases) > 1:
                fields.append({'name':f"__**Phase **__{FS.Assets.Emotes.Num(self._stages.index(stage)+1)}", 'value':'➖'})
                for phase in phases:
                    fields.append({'name':f"{phase.emotes} __**{phase.name}**__", 'value':("\n> ".join([f'{p.display_name}' for p in phase.players]) if phase.players else "*À déterminer...*"), 'inline':True})
            else:
                fields.append({'name':f"__**Phase **__{phases[0].emotes} : __**{phases[0].name}**__", 'value':("\n> ".join([f'{p.display_name}' for p in phases[0].players]) if phases[0].players else "*À déterminer...*"), 'inline':False})
        
        return FS.Embed(
            title = f"🏆 __**{self._name.upper()}**__ 🏆",
            description="__**Joueurs :**__\n"+"\n".join([f'> {member.mention}' for member in self._role.members]),
            fields = fields
        )
            
            
    def next_phase_ready(self) -> bool:
        for stage in self._stages:
            if stage.state == State.SET:
                return True
            elif stage.state == State.INIT or stage.state == State.STARTED:
                return False
        return False
            
            
    def next_phases(self) -> List[Phase]:
        for stage in self._stages:
            if stage.state == State.SET:
                return stage.phases
            elif stage.state == State.INIT or stage.state == State.STARTED:
                return None
        return None
    
    def current_phases(self) -> Optional[List[Phase]]:
        current_stage : Stage = None
        for stage in self._stages:
            if stage.state == State.SET or stage.state == State.STARTED:
                current_stage = stage
                break
            elif stage.state == State.ENDED:
                current_stage = stage
            elif stage.state == State.INIT:
                return None
        return current_stage.phases if current_stage else None
            

        
        


    
