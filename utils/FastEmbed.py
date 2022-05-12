from disnake import Embed, File
from typing import List, Union

class FastEmbed(Embed):
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
    
    
    def __init__(self,
        *,
        title               : str                       = Embed.Empty,
        description         : str                       = Embed.Empty,
        color               : int                       = Embed.Empty,
        url                 : str                       = Embed.Empty,
        
        fields              : Union[List[dict],dict]    = None,
        
        author_name         : str                       = None,
        author_url          : str                       = Embed.Empty,
        author_icon_url     : str                       = Embed.Empty,
        
        thumbnail           : Union[str,File]           = Embed.Empty,
        
        image               : Union[str,File]           = Embed.Empty,
          
        footer_text         : str                       = Embed.Empty,
        footer_icon_url     : str                       = Embed.Empty
        ):
        
        super().__init__(
            title = title,
            description = description,
            color = color,
            url = url)
           
        if fields != None:
            
            if type(fields) == list:
                for i, field in enumerate(fields):
                    self.add_field(
                        name=field.get('name',f"Field name {i+1}"),
                        value=field.get('value',f"Field value {i+1}"),
                        inline=field.get('inline',False)
                    )
                    
            elif type(fields) == dict:
                self.add_field(
                    name=fields.get('name',f"Field name"),
                    value=fields.get('value',f"Field value"),
                    inline=fields.get('inline',False)
                )
                
            else:
                raise TypeError(f'Argument "fields" should be type "list" or "dict" but {type(fields)} has been provided.')
            
        if author_name != None:
            self.set_author(
                name = author_name,
                url = author_url,
                icon_url = author_icon_url
            )
            
        if thumbnail != Embed.Empty:
            if type(thumbnail) == str:
                self.set_thumbnail(url = thumbnail)
            elif type(thumbnail) == File:
                self.set_thumbnail(file = thumbnail)
            else:
                raise TypeError(f'Argument "thumbnail" should be type "str" or "disnake.File" but {type(fields)} has been provided.')
            

        if image != Embed.Empty:
            if type(image) == str:
                self.set_image(url = image)
            elif type(image) == File:
                self.set_image(file = image)
            else:
                raise TypeError(f'Argument "thumbnail" should be type "str" or "disnake.File" but {type(fields)} has been provided.')

        self.set_footer(
            text = footer_text,
            icon_url = footer_icon_url
        )
        
    
        
    def __str__(self):
        author = f"Author:\n\tname: '{self.author.name}'\n\turl: '{self.author.url}'\n\ticon_url: '{self.author.icon_url}'"
        base = f"Title:\n\t'{self.title}'\nDescription:\n\t'{self.description}\n'Color:\n\t'{self.color}'"
        fields = "Fields:\n" + "\n".join(f"\tField {i}:\n\t\tTitle: '{f.name}'\n\t\tValue: '{f.value}'\n\t\tInline: '{f.inline}'" for i,f in enumerate(self.fields))
        thumbnail = f"Thumbnail:\n\t'{self.thumbnail.url}'"
        image = f"Image:\n\t'{self.image.url}'"
        footer = f"Footer:\n\tText: '{self.footer.text}'\n\tUrl: '{self.footer.icon_url}'"
        return f"{author}\n{base}\n{fields}\n{thumbnail}\n{image}\n{footer}"


        
