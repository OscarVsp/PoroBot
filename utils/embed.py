import disnake

def new_embed(title = None, description = None, color = disnake.Embed.Empty, user : disnake.Member = None, fields : dict = None, thumbnail = None, image : str = None, footer : str = None):
    """

    """

    #use *arhs and **kwargs !!
    if title != None:
        if description != None:
            if color != disnake.Embed.Empty:
                embed = disnake.Embed(title=title, description=description, color=color)
            else:
                embed = disnake.Embed(title=title, description=description)
        else:
            if color != None:
                embed = disnake.Embed(title=title, color=color)
            else:
                embed = disnake.Embed(title=title)
    else:
        if description != None:
            if color != None:
                embed = disnake.Embed(description=description, color=color)
            else:
                embed = disnake.Embed(description=description)
        else:
            if color != None:
                embed = disnake.Embed(color=color)
            else:
                embed = disnake.Embed()

    if fields != None:
        for field in fields:
            if 'inline' in field.keys():
                embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
            else:
                embed.add_field(name=field['name'], value=field['value'], inline=False)

    if user != None:
        embed.set_thumbnail(url=user.display_avatar.url)

    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)

    if image != None:
        embed.set_image(url=image)

    if footer != None:
        embed.set_footer(text=footer)
    
    return embed