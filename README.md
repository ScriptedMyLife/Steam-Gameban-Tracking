
<h2 style="margin-bottom:10px">Steam Gameban Tracking Discord Bot</h2>
<h3 style="margin-top:0px">Purpose</h3>

<p style="padding-left:25px">
A discord bot designed for tracking suspected cheating steam accounts. This bot continuously monitors the specified steam accounts for any changes to usernames and imposition of game, vac or community bans. Upon detecting a ban, the discord bot ouputs background information including the name they had when you added them, and all aliases they had leading up to their ban. This functionally is essential because when reporting a player in rust the game only provides their current username, which can change frequently, making it difficult to track and identify cheaters accurately.
</p>

<h3>Bot Commands</h3>
<ul>
    <li>/add_user [steam id] [note]
        <ul>
            <li>Adds a user to the data base</li>
            <li>steam id: users steam id</li>
            <li>note: extra information about the user (server you were playing on, their discord, etc.)</li>
        </ul>
    </li>
    <li>/loop [state]
        <ul>
            <li>Starts the tracking loop (checks steam api every 10 minutes for changes)</li>
            <li>state: takes one of the two options <b>start</b> and <b>stop</b> as a param</li>
        </ul>
    </li>
    <li>/count
        <ul>
            <li>Displays how many steam ids are in the database</li>
        </ul>
    </li>
</ul>
<h3>Enviorment Variables</h3>
<ul>
    <li><b>STEAM_API_KEY</b> - Your steam web api key</li>
    <li><b>DISCORD_API_KEY</b> - Your discord bot api key</li>
    <li><b>LOG_CHANNEL</b> - Discord channel ID for logging actions</li>
    <li><b>BAN_CHANNEL</b> - Discord channel ID for sending ban notifications</li>
    <li><b>NAME_CHANGE_CHANNEL<b> - Discord Channel ID for logging name changes</li>
    <li><b>OTHER_BANS_CHANNEL<b> - Discord Channel ID for logging vac and community bans</li>
</ul>
<h3> Resources </h3>
<ul>
    <li><b><a href=https://steamcommunity.com/dev>Steam API Help<a></b> </li>
    <li><b><a href=https://discordpy.readthedocs.io/en/stable/discord.html>Discord API Help<a></b> </li>
    <li><b><a href=https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID>Discord Channel ID's<a></b> </li>
</ul>
