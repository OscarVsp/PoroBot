# -*- coding: utf-8 -*-
import logging
from typing import List
from typing import Union

import disnake

from .Assets import *


class Embed(disnake.Embed):
    """Represents a Discord embed.

    .. container:: operations

        .. describe:: len(x)

            Returns the total size of the embed.
            Useful for checking if it's within the 6000 character limit.

        .. describe:: bool(b)

            Returns whether the embed has any data set.

            .. versionadded:: 2.0

    Certain properties return an ``EmbedProxy``, a type
    that acts similar to a regular :class:`dict` except using dotted access,
    e.g. ``embed.author.icon_url``. If the attribute
    is invalid or empty, then a special sentinel value is returned,
    :attr:`Embed.Empty`.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    casted to :class:`str` for you.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialisation.
    type: :class:`str`
        The type of embed. Usually "rich".
        This can be set during initialisation.
        Possible strings for embed types can be found on discord's
        `api docs <https://discord.com/developers/docs/resources/channel#embed-object-embed-types>`_
    description: :class:`str`
        The description of the embed.
        This can be set during initialisation.
    url: :class:`str`
        The URL of the embed.
        This can be set during initialisation.
    timestamp: :class:`datetime.datetime`
        The timestamp of the embed content. This is an aware datetime.
        If a naive datetime is passed, it is converted to an aware
        datetime with the local timezone.
    colour: Union[:class:`Colour`, :class:`int`]
        The colour code of the embed. Aliased to ``color`` as well.
        This can be set during initialisation.
    Empty
        A special sentinel value used by ``EmbedProxy`` and this class
        to denote that the value or attribute is empty.
    """

    def __init__(
        self,
        *,
        title: str = disnake.Embed.Empty,
        description: str = disnake.Embed.Empty,
        color: int = disnake.Embed.Empty,
        url: str = disnake.Embed.Empty,
        fields: Union[List[dict], dict] = None,
        author_name: str = None,
        author_url: str = disnake.Embed.Empty,
        author_icon_url: str = disnake.Embed.Empty,
        thumbnail: Union[str, disnake.File] = disnake.Embed.Empty,
        image: Union[str, disnake.File] = disnake.Embed.Empty,
        footer_text: str = disnake.Embed.Empty,
        footer_icon_url: str = disnake.Embed.Empty,
    ):
        if len(description) > 4096:
            logging.warn("Embed description length is higher than 4096 and will be truncated to avoid error.")
            description = description[:4096]
        super().__init__(title=title, description=description, color=color, url=url)

        if fields != None:

            if type(fields) == list:
                for i, field in enumerate(fields):
                    value = field.get("value", f"Field value")
                    if value == "":
                        value = "Field value"
                    self.add_field(
                        name=field.get("name", f"Field name {i+1}"), value=value, inline=field.get("inline", False)
                    )

            elif type(fields) == dict:
                value = fields.get("value", f"Field value")
                if value == "":
                    value = "Field value"
                self.add_field(name=fields.get("name", f"Field name"), value=value, inline=fields.get("inline", False))

            else:
                raise TypeError(
                    f'Argument "fields" should be type "list" or "dict" but {type(fields)} has been provided.'
                )

        if author_name != None:
            self.set_author(name=author_name, url=author_url, icon_url=author_icon_url)

        if thumbnail != Embed.Empty:
            if type(thumbnail) == str:
                self.set_thumbnail(url=thumbnail)
            elif type(thumbnail) == disnake.File:
                self.set_thumbnail(file=thumbnail)
            else:
                raise TypeError(
                    f'Argument "thumbnail" should be type "str" or "disnake.File" but {type(fields)} has been provided.'
                )

        if image != Embed.Empty:
            if type(image) == str:
                self.set_image(url=image)
            elif type(image) == disnake.File:
                self.set_image(file=image)
            else:
                raise TypeError(
                    f'Argument "thumbnail" should be type "str" or "disnake.File" but {type(fields)} has been provided.'
                )

        self.set_footer(text=footer_text, icon_url=footer_icon_url)

    def __str__(self):
        author = (
            f"Author:\n\tname: '{self.author.name}'\n\turl: '{self.author.url}'\n\ticon_url: '{self.author.icon_url}'"
        )
        base = f"Title:\n\t'{self.title}'\nDescription:\n\t'{self.description}\n'Color:\n\t'{self.color}'"
        fields = "Fields:\n" + "\n".join(
            f"\tField {i}:\n\t\tTitle: '{f.name}'\n\t\tValue: '{f.value}'\n\t\tInline: '{f.inline}'"
            for i, f in enumerate(self.fields)
        )
        thumbnail = f"Thumbnail:\n\t'{self.thumbnail.url}'"
        image = f"Image:\n\t'{self.image.url}'"
        footer = f"Footer:\n\tText: '{self.footer.text}'\n\tUrl: '{self.footer.icon_url}'"
        return f"{author}\n{base}\n{fields}\n{thumbnail}\n{image}\n{footer}"

    def check_limits(self) -> None:
        """
        Checks if this embed fits within the limits dictated by Discord.
        There is also a 6000 character limit across all embeds in a message.
        Returns nothing on success, raises :exc:`ValueError` if an attribute exceeds the limits.
        +--------------------------+------------------------------------+
        |   Field                  |              Limit                 |
        +--------------------------+------------------------------------+
        | title                    |        256 characters              |
        +--------------------------+------------------------------------+
        | description              |        4096 characters             |
        +--------------------------+------------------------------------+
        | fields                   |        Up to 25 field objects      |
        +--------------------------+------------------------------------+
        | field.name               |        256 characters              |
        +--------------------------+------------------------------------+
        | field.value              |        1024 characters             |
        +--------------------------+------------------------------------+
        | footer.text              |        2048 characters             |
        +--------------------------+------------------------------------+
        | author.name              |        256 characters              |
        +--------------------------+------------------------------------+
        .. versionadded:: 2.6
        Raises
        ------
        ValueError
            One or more of the embed attributes are too long.
        """

        if self.title and len(self.title.strip()) > 256:
            raise ValueError("Embed title cannot be longer than 256 characters")

        if self.description and len(self.description.strip()) > 4096:
            raise ValueError("Embed description cannot be longer than 4096 characters")

        if self.footer and self.footer != disnake.Embed.Empty and len(self._footer.get("text", "").strip()) > 2048:
            raise ValueError("Embed footer text cannot be longer than 2048 characters")

        if self.author and self.author != disnake.Embed.Empty and len(self._author.get("name", "").strip()) > 256:
            raise ValueError("Embed author name cannot be longer than 256 characters")

        if self.fields:
            if len(self._fields) > 25:
                raise ValueError("Embeds cannot have more than 25 fields")

            for field_index, field in enumerate(self._fields):
                if field != disnake.Embed.Empty:
                    if len(field["name"].strip()) > 256:
                        raise ValueError(f"Embed field {field_index} name cannot be longer than 256 characters")
                    if len(field["value"].strip()) > 1024:
                        raise ValueError(f"Embed field {field_index} value cannot be longer than 1024 characters")

        if len(self) > 6000:
            raise ValueError("Embed total size cannot be longer than 6000 characters")

    @property
    def remaining_space(self) -> int:
        space = 6000
        if self.title:
            space -= len(self.title.strip())
        if self.description:
            space -= len(self.description.strip())
        if self.footer and self.footer != disnake.Embed.Empty:
            space -= len(self._footer.get("text", "").strip())
        if self.author and self.author != disnake.Embed.Empty:
            space -= len(self._author.get("name", "").strip())

        if self.fields:

            for field in self._fields:
                if field != disnake.Embed.Empty:
                    space -= len(field["name"].strip())
                    space -= len(field["value"].strip())
        return space

    @staticmethod
    def flex(
        title: str = disnake.Embed.Empty,
        description: str = disnake.Embed.Empty,
        color: int = disnake.Embed.Empty,
        url: str = disnake.Embed.Empty,
        fields: Union[List[dict], dict] = None,
        author_name: str = None,
        author_url: str = disnake.Embed.Empty,
        author_icon_url: str = disnake.Embed.Empty,
        thumbnail: Union[str, disnake.File] = disnake.Embed.Empty,
        image: Union[str, disnake.File] = disnake.Embed.Empty,
        footer_text: str = disnake.Embed.Empty,
        footer_icon_url: str = disnake.Embed.Empty,
    ) -> List[disnake.Embed]:
        embeds = [
            Embed(
                title=title,
                description="",
                color=color,
                url=url,
                author_name=author_name,
                author_url=author_url,
                author_icon_url=author_icon_url,
                thumbnail=thumbnail,
            )
        ]
        for line in description.split("\n"):
            if (
                len((line + "\n").strip()) > embeds[-1].remaining_space
                or len((line + "\n").strip()) + len(embeds[-1].description.strip()) > 4000
            ):
                embeds.append(Embed(color=color, description=""))
            embeds[-1].description += line + "\n"

        if isinstance(fields, dict):
            if (
                len(fields.get("name", "field name").strip()) + len(fields.get("value", "field value").strip())
                > embeds[-1].remaining_space
            ):
                embeds.append(Embed(color=""))
            embeds[-1].add_field(
                name=fields.get("name", "field name"),
                value=fields.get("value", "field value"),
                inline=fields.get("inline", False),
            )
        elif isinstance(fields, list):
            for field in fields:
                if (
                    len(field.get("name", "field name").strip()) + len(field.get("value", "field value").strip())
                    > embeds[-1].remaining_space
                ):
                    embeds.append(Embed(color=""))
                embeds[-1].add_field(
                    name=field.get("name", "field name"),
                    value=field.get("value", "field value"),
                    inline=field.get("inline", False),
                )
        if footer_text != disnake.Embed.Empty and len(footer_text.strip()) > embeds[-1].remaining_space:
            embeds.append(Embed(color=color))
        embeds[-1].set_footer(text=footer_text, icon_url=footer_icon_url)
        if isinstance(image, str):
            embeds[-1].set_image(url=image)
        elif isinstance(image, disnake.File):
            embeds[-1].set_image(file=image)
        return embeds


def warning(message: str) -> disnake.Embed:
    return Embed(title="⚠", description=message, color=disnake.Colour.orange(), thumbnail=Images.Poros.SWEAT)


def error(message: str) -> disnake.Embed:
    return Embed(title=":x:", description=message, color=disnake.Colour.orange(), thumbnail=Images.Poros.SHOCKED)
