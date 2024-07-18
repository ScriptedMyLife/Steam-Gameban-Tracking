import discord, time

def gen_timestamp():
    """Creates a discord timestamp for logging"""
    return f"<t:{round(time.time())}:F>"

def name_change_embed(prev_name, cur_name, avatar_url):
    """Creates a discord embed for a name change event"""
    embed = discord.Embed()
    embed.color = discord.Colour.blue()
    embed.add_field(name="Previous Username", value=prev_name, inline=True)
    embed.add_field(name="Updated Username", value=cur_name, inline=True)
    embed.add_field(name="Sent at", value=gen_timestamp(), inline=False)
    embed.set_thumbnail(url=avatar_url)
    return embed

def game_ban_embed(orig_name, cur_name, prev_gamebans, cur_gamebans, avatar_url, state):
    """Creates a discord embed for a game ban event"""
    embed = discord.Embed()
    embed.color = discord.Colour.red()
    if state == "game_ban_issued":
        embed.title = "Game Ban Issued!"
    else:
        embed.title = "Game Ban Revoked!"
    embed.add_field(name="Username when reported", value=orig_name)
    embed.add_field(name="Current username", value=cur_name)
    embed.add_field(name="Game ban count", value=f"{prev_gamebans} -> {cur_gamebans}")
    embed.add_field(name="Sent at", value=gen_timestamp())
    embed.set_thumbnail(url=avatar_url)
    return embed

def vac_ban_embed(orig_name, cur_name, prev_vac_bans, cur_vac_bans, avatar_url, state):
    embed = discord.Embed()
    embed.color = discord.Colour.dark_blue()
    if state == "vac_ban_issued":
        embed.title = "VAC Ban Issued!"
    else:
        embed.title = "VAC Ban Revoked!"
    embed.add_field(name="Username when reported", value=orig_name)
    embed.add_field(name="Current username", value=cur_name)
    embed.add_field(name="Game ban count", value=f"{prev_vac_bans} -> {cur_vac_bans}")
    embed.add_field(name="Sent at", value=gen_timestamp())
    embed.set_thumbnail(url=avatar_url)
    return embed

def community_ban_embed(orig_name, cur_name, avatar_url, state):
    embed = discord.Embed()
    embed.color = discord.Colour.dark_blue()
    if state == "community_ban_issued":
        embed.title = "Community Ban Issued!"
    else:
        embed.title = "Community Ban Revoked!"
    embed.add_field(name="Username when reported", value=orig_name)
    embed.add_field(name="Current username", value=cur_name)
    embed.add_field(name="Sent at", value=gen_timestamp())
    embed.set_thumbnail(url=avatar_url)
    return embed

def add_user_embed_log(steam_id, username, avatar_url, author):
    """Creates a discord embed for logging user add command"""
    embed = log_command_template("/add_user")
    embed.add_field(name="Steam ID added", value=f"{username} - [{steam_id}](https://steamcommunity.com/profiles/{steam_id})", inline=True)
    embed.add_field(name="Sent at", value=gen_timestamp(), inline=False)
    embed.set_thumbnail(url=avatar_url)
    embed.set_footer(text=f"Requested by: {author}")
    return embed

def loop_command_log(state, author):
    """Creates a discord embed for logging loop command"""
    embed = log_command_template("/loop")
    embed.add_field(name="Command State", value=state)
    embed.add_field(name="Sent at", value=gen_timestamp())
    embed.set_footer(text=f"Author: {author}")
    return embed

def log_command_template(cmd_name):
    """A template for creating other embeds"""
    embed = discord.Embed()
    embed.color = discord.Colour.blue()
    embed.title = "Command Executed"
    embed.add_field(name="Command Name", value=f"{cmd_name}", inline=True)
    return embed
