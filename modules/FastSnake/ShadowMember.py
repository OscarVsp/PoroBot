# -*- coding: utf-8 -*-
import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import overload
from typing import Sequence
from typing import Tuple
from typing import TypeVar
from typing import Union

import disnake
from disnake.abc import Snowflake
from disnake.context_managers import Typing
from disnake.ui.item import WrappedComponent

# __all__ = ("ActionRow",)

SnowflakeTime = Union["Snowflake", datetime.datetime]
VocalGuildChannel = Union[disnake.VoiceChannel, disnake.StageChannel]

ActionRowT = TypeVar("ActionRowT", bound="disnake.ActionRow")
Components = Union[
    ActionRowT,
    WrappedComponent,
    Sequence[Union[ActionRowT, WrappedComponent, Sequence[WrappedComponent]]],
]


class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return "..."


MISSING: Any = _MissingSentinel()


class ShadowMember:
    def __init__(self, member: disnake.Member):
        self.member = member

    ####### PROPERTIES #######

    @property
    def accent_color(self) -> Optional[disnake.Colour]:
        """Optional[:class:`Colour`]: Returns the user's accent color, if applicable.

        There is an alias for this named :attr:`accent_colour`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        return self.member.accent_colour

    @property
    def accent_colour(self) -> Optional[disnake.Colour]:
        """Optional[:class:`Colour`]: Returns the user's accent colour, if applicable.

        There is an alias for this named :attr:`accent_color`.

        .. versionadded:: 2.0

        .. note::

            This information is only available via :meth:`Client.fetch_user`.
        """
        return self.member.accent_colour

    @property
    def activity(self) -> Optional[disnake.activity.ActivityTypes]:
        """Optional[Union[:class:`BaseActivity`, :class:`Spotify`]]: Returns the primary
        activity the user is currently doing. Could be ``None`` if no activity is being done.

        .. note::

            Due to a Discord API limitation, this may be ``None`` if
            the user is listening to a song on Spotify with a title longer
            than 128 characters. See :issue-dpy:`1738` for more information.

        .. note::

            A user may have multiple activities, these can be accessed under :attr:`activities`.
        """
        return self.member.activity

    @property
    def activities(self) -> Tuple[Union[disnake.BaseActivity, disnake.Spotify]]:
        """The activities that the user is currently doing."""
        return self.member.activities

    @property
    def avatar(self) -> disnake.Asset:
        return self.member.avatar

    @property
    def banner(self) -> Optional[disnake.Asset]:
        """Optional[:class:`Asset`]: Returns the user's banner asset, if available.

        .. versionadded:: 2.0

        .. note::
            This information is only available via :meth:`Client.fetch_user`.
        """
        return self.member.banner

    @property
    def bot(self) -> bool:
        return self.member.bot

    @property
    def color(self) -> disnake.Colour:
        """:class:`Colour`: A property that returns a color denoting the rendered color for
        the member. If the default color is the one rendered then an instance of :meth:`Colour.default`
        is returned.

        There is an alias for this named :attr:`colour`.
        """
        return self.member.colour

    @property
    def colour(self) -> disnake.Colour:
        """:class:`Colour`: A property that returns a colour denoting the rendered colour
        for the member. If the default colour is the one rendered then an instance
        of :meth:`Colour.default` is returned.

        There is an alias for this named :attr:`color`.
        """
        return self.member.colour

    @property
    def created_at(self) -> datetime.datetime:
        return self.member.created_at

    @property
    def current_timeout(self) -> Optional[datetime.datetime]:
        """Optional[:class:`datetime.datetime`]: Returns the datetime when the timeout expires, if any.

        .. versionadded:: 2.3
        """
        return self.member.current_timeout

    @property
    def default_avatar(self) -> disnake.Asset:
        """:class:`Asset`: Returns the default avatar for a given user. This is calculated by the user's discriminator."""
        return self.member.default_avatar

    @property
    def desktop_status(self) -> disnake.Status:
        """:class:`Status`: The member's status on the desktop client, if applicable."""
        return self.member.desktop_status

    @property
    def display_avatar(self) -> disnake.Asset:
        """:class:`Asset`: Returns the member's display avatar.

        For regular members this is just their avatar, but
        if they have a guild specific avatar then that
        is returned instead.

        .. versionadded:: 2.0
        """
        return self.member.display_avatar

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name.

        For regular users this is just their username, but
        if they have a guild specific nickname then that
        is returned instead.
        """
        return self.member.display_name

    @property
    def dm_channel(self) -> Optional[disnake.DMChannel]:
        """Optional[:class:`DMChannel`]: Returns the channel associated with this user if it exists.

        If this returns ``None``, you can create a DM channel by calling the
        :meth:`create_dm` coroutine function.
        """
        return self.member.dm_channel

    @property
    def guild(self) -> disnake.Guild:
        return self.member.guild

    @property
    def guild_avatar(self) -> Optional[disnake.Asset]:
        """Optional[:class:`Asset`]: Returns an :class:`Asset` for the guild avatar
        the member has. If unavailable, ``None`` is returned.

        .. versionadded:: 2.0
        """
        return self.member.guild_avatar

    @property
    def guild_permissions(self) -> disnake.Permissions:
        """:class:`Permissions`: Returns the member's guild permissions.

        This only takes into consideration the guild permissions
        and not most of the implied permissions or any of the
        channel permission overwrites. For 100% accurate permission
        calculation, please use :meth:`abc.GuildChannel.permissions_for`.

        This does take into consideration guild ownership and the
        administrator implication.
        """
        return self.member.guild_permissions

    @property
    def id(self) -> int:
        return self.member.id

    @property
    def joined_at(self) -> datetime.datetime:
        return self.member.joined_at

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the member."""
        return self.member.mention

    @property
    def mobile_status(self) -> disnake.Status:
        """:class:`Status`: The member's status on a mobile device, if applicable."""
        return self.member.mobile_status

    @property
    def mutual_guilds(self) -> List[disnake.Guild]:
        """List[:class:`Guild`]: The guilds that the user shares with the client.

        .. note::

            This will only return mutual guilds within the client's internal cache.

        .. versionadded:: 1.7
        """
        return self.member.mutual_guilds

    @property
    def name(self) -> str:
        return self.member.name

    @property
    def nick(self) -> str:
        return self.member.nick

    @property
    def pending(self) -> bool:
        return self.member.pending

    @property
    def premiun_since(self) -> datetime.datetime:
        return self.member.premium_since

    @property
    def public_flags(self) -> disnake.PublicUserFlags:
        """:class:`PublicUserFlags`: The publicly available flags the user has."""
        return self.member.public_flags

    @property
    def raw_status(self) -> str:
        """:class:`str`: The member's overall status as a string value.

        .. versionadded:: 1.5
        """
        return self.member.raw_status

    @property
    def role_icon(self) -> Optional[Union[disnake.Asset, disnake.PartialEmoji]]:
        """Optional[Union[:class:`Asset`, :class:`PartialEmoji`]]: Returns the member's displayed role icon, if any.

        .. versionadded:: 2.5
        """
        return self.member.role_icon

    @property
    def roles(self) -> List[disnake.Role]:
        """List[:class:`Role`]: A :class:`list` of :class:`Role` that the member belongs to. Note
        that the first element of this list is always the default '@everyone'
        role.

        These roles are sorted by their position in the role hierarchy.
        """
        return self.member.roles

    @property
    def status(self) -> disnake.Status:
        """:class:`Status`: The member's overall status. If the value is unknown, then it will be a :class:`str` instead."""
        return self.member.status

    @property
    def system(self) -> bool:
        return self.member.system

    @property
    def top_role(self) -> disnake.Role:
        """:class:`Role`: Returns the member's highest role.

        This is useful for figuring where a member stands in the role
        hierarchy chain.
        """
        return self.member.top_role

    @property
    def voice(self) -> Optional[disnake.VoiceState]:
        """Optional[:class:`VoiceState`]: Returns the member's current voice state."""
        return self.member.voice

    @property
    def web_status(self) -> disnake.Status:
        """:class:`Status`: The member's status on the web client, if applicable."""
        return self.member.web_status

    ###### METHODS ######

    async def add_roles(self, *roles: Snowflake, reason: Optional[str] = None, atomic: bool = True) -> None:
        """
        |coro|

        Gives the member a number of :class:`Role`\\s.

        You must have :attr:`~Permissions.manage_roles` permission to
        use this, and the added :class:`Role`\\s must appear lower in the list
        of roles than the highest role of the member.

        Parameters
        ----------
        *roles: :class:`abc.Snowflake`
            An argument list of :class:`abc.Snowflake` representing a :class:`Role`
            to give to the member.
        reason: Optional[:class:`str`]
            The reason for adding these roles. Shows up on the audit log.
        atomic: :class:`bool`
            Whether to atomically add roles. This will ensure that multiple
            operations will always be applied regardless of the current
            state of the cache.

        Raises
        ------
        Forbidden
            You do not have permissions to add these roles.
        HTTPException
            Adding roles failed.
        """
        return await self.member.add_roles(*roles, reason=reason, atomic=atomic)

    async def ban(self, *, delete_message_days=1, reason=None) -> None:
        """|coro|

        Bans this member. Equivalent to :meth:`Guild.ban`.
        """
        await self.member.ban(delete_message_days=delete_message_days, reason=reason)

    async def create_dm(self) -> disnake.DMChannel:
        """|coro|

        Creates a :class:`DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        return self.member.create_dm()

    async def edit(
        self,
        *,
        nick: Optional[str] = MISSING,
        mute: bool = MISSING,
        deafen: bool = MISSING,
        suppress: bool = MISSING,
        roles: Sequence[disnake.abc.Snowflake] = MISSING,
        voice_channel: Optional[VocalGuildChannel] = MISSING,
        timeout: Optional[Union[float, datetime.timedelta, datetime.datetime]] = MISSING,
        reason: Optional[str] = None,
    ) -> Optional[disnake.Member]:
        """|coro|

        Edits the member's data.

        Depending on the parameter passed, this requires different permissions listed below:

        +------------------------------+-------------------------------------+
        |   Parameter                  |              Permission             |
        +------------------------------+-------------------------------------+
        | nick                         | :attr:`Permissions.manage_nicknames`|
        +------------------------------+-------------------------------------+
        | mute                         | :attr:`Permissions.mute_members`    |
        +------------------------------+-------------------------------------+
        | deafen                       | :attr:`Permissions.deafen_members`  |
        +------------------------------+-------------------------------------+
        | roles                        | :attr:`Permissions.manage_roles`    |
        +------------------------------+-------------------------------------+
        | voice_channel                | :attr:`Permissions.move_members`    |
        +------------------------------+-------------------------------------+
        | timeout                      | :attr:`Permissions.moderate_members`|
        +------------------------------+-------------------------------------+

        All parameters are optional.

        .. versionchanged:: 1.1
            Can now pass ``None`` to ``voice_channel`` to kick a member from voice.

        .. versionchanged:: 2.0
            The newly member is now optionally returned, if applicable.

        Parameters
        ----------
        nick: Optional[:class:`str`]
            The member's new nickname. Use ``None`` to remove the nickname.
        mute: :class:`bool`
            Whether the member should be guild muted or un-muted.
        deafen: :class:`bool`
            Whether the member should be guild deafened or un-deafened.
        suppress: :class:`bool`
            Whether the member should be suppressed in stage channels.

            .. versionadded:: 1.7

        roles: Sequence[:class:`Role`]
            The member's new list of roles. This *replaces* the roles.
        voice_channel: Optional[:class:`VoiceChannel`]
            The voice channel to move the member to.
            Pass ``None`` to kick them from voice.
        timeout: Optional[Union[:class:`float`, :class:`datetime.timedelta`, :class:`datetime.datetime`]]
            The duration (seconds or timedelta) or the expiry (datetime) of the timeout;
            until then, the member will not be able to interact with the guild.
            Set to ``None`` to remove the timeout. Supports up to 28 days in the future.

            .. versionadded:: 2.3

        reason: Optional[:class:`str`]
            The reason for editing this member. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have the proper permissions to the action requested.
        HTTPException
            The operation failed.

        Returns
        -------
        Optional[:class:`.Member`]
            The newly updated member, if applicable. This is only returned
            when certain fields are updated.
        """
        await self.member.edit(
            nick=nick,
            mute=mute,
            deafen=deafen,
            suppress=suppress,
            roles=roles,
            voice_channel=voice_channel,
            timeout=timeout,
            reason=reason,
        )

    async def fetch_message(self, id: int) -> disnake.Message:
        """|coro|

        Retrieves a single :class:`.Message` from the destination.

        Parameters
        ----------
        id: :class:`int`
            The message ID to look for.

        Raises
        ------
        NotFound
            The specified message was not found.
        Forbidden
            You do not have the permissions required to get a message.
        HTTPException
            Retrieving the message failed.

        Returns
        -------
        :class:`.Message`
            The message asked for.
        """
        return await self.member.fetch_message(id)

    def get_role(self, role_id: int) -> Optional[disnake.Role]:
        """Returns a role with the given ID from roles which the member has.

        .. versionadded:: 2.0

        Parameters
        ----------
        role_id: :class:`int`
            The role ID to search for.

        Returns
        -------
        Optional[:class:`Role`]
            The role or ``None`` if not found in the member's roles.
        """
        return self.member.get_role(role_id)

    def history(
        self,
        *,
        limit: Optional[int] = 100,
        before: Optional[SnowflakeTime] = None,
        after: Optional[SnowflakeTime] = None,
        around: Optional[SnowflakeTime] = None,
        oldest_first: Optional[bool] = None,
    ):
        """Returns an :class:`.AsyncIterator` that enables receiving the destination's message history.

        You must have :attr:`.Permissions.read_message_history` permission to use this.

        Examples
        --------

        Usage ::

            counter = 0
            async for message in channel.history(limit=200):
                if message.author == client.user:
                    counter += 1

        Flattening into a list: ::

            messages = await channel.history(limit=123).flatten()
            # messages is now a list of Message...

        All parameters are optional.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of messages to retrieve.
            If ``None``, retrieves every message in the channel. Note, however,
            that this would make it a slow operation.
        before: Optional[Union[:class:`.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages before this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: Optional[Union[:class:`.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages after this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        around: Optional[Union[:class:`.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages around this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
            When using this argument, the maximum limit is 101. Note that if the limit is an
            even number then this will return at most limit + 1 messages.
        oldest_first: Optional[:class:`bool`]
            If set to ``True``, return messages in oldest->newest order. Defaults to ``True`` if
            ``after`` is specified, otherwise ``False``.

        Raises
        ------
        Forbidden
            You do not have permissions to get channel message history.
        HTTPException
            The request to get message history failed.

        Yields
        -------
        :class:`.Message`
            The message with the message data parsed.
        """
        return self.member.history(limit=limit, before=before, after=after, around=around, oldest_first=oldest_first)

    def is_on_mobile(self) -> bool:
        """Whether the member is active on a mobile device.

        :return type: :class:`bool`
        """
        return self.member.is_on_mobile()

    async def kick(self, *, reason=None) -> None:
        """|coro|

        Kicks this member. Equivalent to :meth:`Guild.kick`.
        """
        await self.member.kick(reason=reason)

    def mentioned_in(self, message: disnake.Message) -> bool:
        """Whether the member is mentioned in the specified message.

        Parameters
        ----------
        message: :class:`Message`
            The message to check.

        Returns
        -------
        :class:`bool`
            Indicates if the member is mentioned in the message.
        """
        return self.member.mentioned_in(message=message)

    async def move_to(self, channel: VocalGuildChannel, *, reason: Optional[str] = None) -> None:
        """|coro|

        Moves a member to a new voice channel (they must be connected first).

        You must have :attr:`~Permissions.move_members` permission to
        use this.

        This raises the same exceptions as :meth:`edit`.

        .. versionchanged:: 1.1
            Can now pass ``None`` to kick a member from voice.

        Parameters
        ----------
        channel: Optional[:class:`VoiceChannel`]
            The new voice channel to move the member to.
            Pass ``None`` to kick them from voice.
        reason: Optional[:class:`str`]
            The reason for doing this action. Shows up on the audit log.
        """
        await self.member.move_to(channel, reason=reason)

    async def pins(self) -> List[disnake.Message]:
        """|coro|

        Retrieves all messages that are currently pinned in the channel.

        .. note::

            Due to a limitation with the Discord API, the :class:`.Message`
            objects returned by this method do not contain complete
            :attr:`.Message.reactions` data.

        Raises
        ------
        HTTPException
            Retrieving the pinned messages failed.

        Returns
        -------
        List[:class:`.Message`]
            The messages that are currently pinned.
        """
        return await self.member.pins()

    async def remove_roles(self, *roles: Snowflake, reason: Optional[str] = None, atomic: bool = True) -> None:
        """
        |coro|

        Removes :class:`Role`\\s from this member.

        You must have :attr:`~Permissions.manage_roles` permission to
        use this, and the removed :class:`Role`\\s must appear lower in the list
        of roles than the highest role of the member.

        Parameters
        ----------
        *roles: :class:`abc.Snowflake`
            An argument list of :class:`abc.Snowflake` representing a :class:`Role`
            to remove from the member.
        reason: Optional[:class:`str`]
            The reason for removing these roles. Shows up on the audit log.
        atomic: :class:`bool`
            Whether to atomically remove roles. This will ensure that multiple
            operations will always be applied regardless of the current
            state of the cache.

        Raises
        ------
        Forbidden
            You do not have permissions to remove these roles.
        HTTPException
            Removing the roles failed.
        """
        await self.member.remove_roles(roles=roles, reason=reason, atomic=atomic)

    async def request_to_speak(self) -> None:
        """|coro|

        Requests to speak in the connected channel.

        Only applies to stage channels.

        .. note::

            Requesting members that are not the client is equivalent
            to :attr:`.edit` providing ``suppress`` as ``False``.

        .. versionadded:: 1.7

        Raises
        ------
        Forbidden
            You do not have the proper permissions to the action requested.
        HTTPException
            The operation failed.
        """
        await self.member.request_to_speak()

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
        await self.member.send(
            content=content,
            tts=tts,
            embed=embed,
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
            components=components,
        )

    @overload
    async def timeout(
        self,
        *,
        duration: Optional[Union[float, datetime.timedelta]],
        reason: Optional[str] = None,
    ) -> disnake.Member:
        ...

    @overload
    async def timeout(
        self,
        *,
        until: Optional[datetime.datetime],
        reason: Optional[str] = None,
    ) -> disnake.Member:
        ...

    async def timeout(
        self,
        *,
        duration: Optional[Union[float, datetime.timedelta]] = MISSING,
        until: Optional[datetime.datetime] = MISSING,
        reason: Optional[str] = None,
    ) -> disnake.Member:
        """|coro|

        Times out the member from the guild; until then, the member will not be able to interact with the guild.

        Exactly one of ``duration`` or ``until`` must be provided. To remove a timeout, set one of the parameters to ``None``.

        You must have the :attr:`Permissions.moderate_members` permission to do this.

        .. versionadded:: 2.3

        Parameters
        ----------
        duration: Optional[Union[:class:`float`, :class:`datetime.timedelta`]]
            The duration (seconds or timedelta) of the member's timeout. Set to ``None`` to remove the timeout.
            Supports up to 28 days in the future.
            May not be used in combination with the ``until`` parameter.
        until: Optional[:class:`datetime.datetime`]
            The expiry date/time of the member's timeout. Set to ``None`` to remove the timeout.
            Supports up to 28 days in the future.
            May not be used in combination with the ``duration`` parameter.
        reason: Optional[:class:`str`]
            The reason for this timeout. Appears on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to timeout this member.
        HTTPException
            Timing out the member failed.

        Returns
        -------
        :class:`Member`
            The newly updated member.
        """
        return await self.member.timeout(duration=duration, until=until, reason=reason)

    async def trigger_typing(self) -> None:
        """|coro|

        Triggers a *typing* indicator to the destination.

        *Typing* indicator will go away after 10 seconds, or after a message is sent.
        """
        await self.member.trigger_typing()

    def typing(self) -> Typing:
        """Returns a context manager that allows you to type for an indefinite period of time.

        This is useful for denoting long computations in your bot.

        .. note::

            This is both a regular context manager and an async context manager.
            This means that both ``with`` and ``async with`` work with this.

        Example Usage: ::

            async with channel.typing():
                # simulate something heavy
                await asyncio.sleep(10)

            await channel.send('done!')

        """
        return self.member.typing()

    async def unban(self, *, reason=None) -> None:
        """|coro|

        Unbans this member. Equivalent to :meth:`Guild.unban`.
        """
        await self.member.unban(reason=reason)

    ### DUNDER ###

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ShadowMember):
            return __o.member == self.member
        return self.member == __o
