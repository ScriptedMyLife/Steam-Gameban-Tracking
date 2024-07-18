import discord, json, os, steam, asyncio, time
from dotenv import load_dotenv, dotenv_values
from termcolor import colored
from discord.ext import commands, tasks
import custom_embeds as ce

# Enviorment Variables
load_dotenv()
discord_token = os.getenv("DISCORD_API_KEY")
steam_api_key = os.getenv("STEAM_API_KEY")
logger_channel_id = int(os.getenv("LOG_CHANNEL"))
gameban_channel_id = int(os.getenv("BAN_CHANNEL"))
name_change_channel_id = int(os.getenv("NAME_CHANGE_CHANNEL"))
other_bans_channel_id = int(os.getenv("OTHER_BANS_CHANNEL"))

class BanTracker(commands.Bot):
    async def on_ready(self):
        print(colored(f"Logged on as {self.user}.", "green"))
        load_ids()
        activity = discord.Game(type=discord.ActivityType.watching, name="Rust")
        await bot.change_presence(activity=activity)
        await self.tree.sync(guild=discord.Object(id=1195907162556354731))
        print(colored("Changed bot status, and synced command tree", "green"))

# Discord bot permissions
intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = BanTracker(command_prefix="/", intents=intents)

# Accessing json location
cur_dir = os.path.dirname(os.path.abspath(__file__))
STEAM_ID_FILE = os.path.join(cur_dir, '..','data','steam_ids.json')

# Dict's containing steam information
steam_ids = {}
steam_ids_cache = {}

# Boolean for enabling and disabling ban loop
ban_loop_active = False

def save_ids():
    """Saves steamids to a json file"""
    with open(STEAM_ID_FILE, 'w') as f:
        json.dump(steam_ids, f, indent=4)

def load_ids():
    """Loads steamids from a json file"""
    global steam_ids
    if not os.path.exists(STEAM_ID_FILE):
        print(colored("Steam ID json file does not exist, creating a new one", "yellow"))
        with open(STEAM_ID_FILE, 'w') as f:
            json.dump(steam_ids, f, indent=4)
        print(colored("Created a new Steam ID json file", "green"))
    if os.path.getsize(STEAM_ID_FILE) == 0:
        print(colored("Steam ID json file is empty", "yellow"))
        return
    
    try:
        with open(STEAM_ID_FILE, 'r') as f:
            steam_ids = json.load(f)
            print(colored("Steam ID's loaded from file", "green"))
    except json.JSONDecodeError as e:
        print(colored(f"Error decoding JSON: {e}", "red"))

def compare_users(old_user, new_user):
    """Checks for changes in a user, returns a list of changes"""
    results = []
    if old_user['name'] != new_user['name']:
        results.append("name_change")
    if old_user['CommunityBanned'] != new_user['CommunityBanned']:
        results.append("community_ban")
        if old_user['CommunityBanned'] == False:
            results.append("community_ban_issued")
        else:
            results.append("community_ban_revoked")
    if old_user['VACBanned'] != new_user['VACBanned']:
        results.append("vac_ban")
        if old_user['VACBanned'] == False:
            results.append("vac_ban_issued")
        else:
            results.append("vac_ban_revoked")
    if old_user['NumberOfVACBans'] != new_user['NumberOfVACBans']:
        results.append("vac_ban_num")
    if old_user['NumberOfGameBans'] != new_user['NumberOfGameBans']:
        results.append("game_ban")
        if old_user['NumberOfGameBans'] < new_user['NumberOfGameBans']:
            results.append("game_ban_issued")
        else:
            results.append("game_ban_revoked")
    return results

#TODO implement more effiecent discord embed logging
async def add_log_message(channel_id, embed):
    return

@bot.hybrid_command(name="add_user", with_app_command=True, description="Add's a SteamID to the tracking loop")
async def add_user(ctx: commands.Context, steam_id: str):
    print(colored(f"{ctx.message.author.name} called add_user command with steamid: {steam_id}", "blue"))
    async with ctx.typing(): # For demanding tasks let the user know something is happening
        # Check if the steam ID is 17 characters
        if len(steam_id) != 17:
            await ctx.send(f"Invalid SteamID")
            print(colored(f"{steam_id} is not the right length", "yellow"))
            return

        # Check if the steam ID is already in the database
        if steam_id in steam_ids:
            await ctx.send(f"SteamID: __{steam_id}__ is already being watched.")
            print(colored(f"SteamID: {steam_id} is already being watched", "yellow"))
            return
        
        # Check if the steam ID is already in the queue
        if steam_id in steam_ids_cache:
            await ctx.send(f"SteamID: __{steam_id}__ is already in the queue.")
            print(colored(f"SteamID: {steam_id} is already in the queue", "yellow"))
            return
        
        try:
            user_data_task = steam.get_player_summaries(steam_ids=[steam_id], steam_api_key=steam_api_key)
            ban_data_task = steam.get_ban_data(steam_ids=[steam_id], steam_api_key=steam_api_key)

            user_data, ban_data = await asyncio.gather(user_data_task, ban_data_task)

            if user_data == None:
                await ctx.send(f"Could not fetch player data from steam. (steam API may be down)")
                print(colored("get_player_summaries returned none", "red"))
                return
            
            if ban_data == None:
                await ctx.send(f"Could not fetch ban data from steam. (steam API may be down)")
                print(colored(f"get_ban_data returnd none", "red"))

            user_data = user_data['response']['players'][0]
            ban_data = ban_data['players'][0]

            if ban_loop_active == True:
                steam_ids_cache[steam_id] = {
                    "name": user_data['personaname'],
                    "avatar": user_data['avatarfull'],
                    "aliases": [user_data['personaname']],
                    "CommunityBanned": ban_data['CommunityBanned'],
                    "VACBanned": ban_data['VACBanned'],
                    "NumberOfVACBans": ban_data['NumberOfVACBans'],
                    "NumberOfGameBans": ban_data['NumberOfGameBans']
                }
                await ctx.send(f"SteamID: __{steam_id}__ was added to the queue.")
                print(colored(f"SteamID: {steam_id} was added to the queue", "green"))
            elif ban_loop_active == False:
                steam_ids[steam_id] = {
                    "name": user_data['personaname'],
                    "avatar": user_data['avatarfull'],
                    "aliases": [user_data['personaname']],
                    "CommunityBanned": ban_data['CommunityBanned'],
                    "VACBanned": ban_data['VACBanned'],
                    "NumberOfVACBans": ban_data['NumberOfVACBans'],
                    "NumberOfGameBans": ban_data['NumberOfGameBans']
                }
                await ctx.send(f"SteamID: __{steam_id}__ was added to the database.")
                print(colored(f"SteamID: {steam_id} was added to the database", "green"))
                save_ids()
            log_channel = bot.get_channel(logger_channel_id)
            await log_channel.send(embed=ce.add_user_embed_log(steam_id, user_data['avatarfull'], ctx.message.author.global_name))
        except KeyError as e:
            print(colored("KeyError: {e}", "red"))
            return
        except Exception as e:
            print(colored(f"An unexpected error occured: {e}", "red"))
            return
    return

@bot.hybrid_command(name="loop", with_app_command=True, description='Takes "start" and "stop" as params')
async def loop(ctx: commands.Context, state: str):
    async with ctx.typing():
        state = state.lower()
        print(colored(f"{ctx.message.author.name} called loop with state: {state}","blue"))
        global ban_loop_active

        # Handle states, and turn loop on and off
        if state == "start":
            if check_for_bans.is_running():
                await ctx.send("Ban Checking loop is alreay running")
                return
            else:
                await ctx.send("Starting tracking loop")
                print(colored("Starting Tracking Loop", "blue"))
                ban_loop_active = True
                check_for_bans.start()
                return
        elif state == "stop":
            if check_for_bans.is_running():
                await ctx.send("Stopping tracking loop")
                print(colored("Stopping Tracking Loop (after next iteration)", "blue"))
                check_for_bans.stop()
                ban_loop_active = False
            else:
                await ctx.send("Tracking Loop is not running")
        else:
            await ctx.send("Invalid state error, state must be: __start__ or __stop__")    
        log_channel = bot.get_channel(logger_channel_id)
        log_channel.send(embed=ce.loop_command_log(state, ctx.message.author.name))
        return

@bot.hybrid_command(name="count", with_app_command=True, description='Lists all the users in the database')
async def count(ctx: commands.Context):
    async with ctx.typing():
        ids = steam_ids.keys()
        embed = discord.Embed()
        embed.title = f"{len(ids)} accounts in the database"
        await ctx.send(embed=embed)

@bot.hybrid_command(name="test_api", with_app_command=True, description="Tests api calls")
async def test_api(ctx: commands.Context):
    result = await steam.get_ban_data(["76561199626760903"], steam_api_key)
    await ctx.send(result)

@tasks.loop(minutes=10)
async def check_for_bans():
    global steam_ids_cache
    global steam_ids
    global ban_loop_active
    ban_loop_active = True

    # If a user is added during the loop (very very rare)
    if steam_ids_cache:
        for steam_id in steam_ids_cache.keys():
            steam_ids[steam_id] = steam_ids_cache[steam_id]
        steam_ids_cache = {}
        save_ids()
    id_list = list(steam_ids.keys())
    
    # Get new info
    new_info = await steam.process_ids(id_list, steam_api_key=steam_api_key)

    # Compare info
    for steamid in new_info.keys():
        old_user = steam_ids[steamid]
        new_user = new_info[steamid]

        previous_name = old_user['name']
        cur_name = new_user['name']
        avatar_url = old_user['avatar']
        orig_name = old_user['aliases'][0]

        # Check for changes (if gamebans increased, name changed, etc)
        changes = compare_users(old_user, new_user)

        # Logic for a name change event
        if "name_change" in changes:
            old_user['aliases'].append(old_user['name'])
            old_user['name'] = new_user['name']
            name_change_channel = bot.get_channel(name_change_channel_id)
            if name_change_channel:
                embed = ce.name_change_embed(previous_name, cur_name, avatar_url)
                await name_change_channel.send(embed=embed)
            else:
                print(colored("Could not send message to log channel", "red"))
                print(colored("User changed their name", "blue"))
            
        # Logic for a game ban event
        if "game_ban" in changes:
            gameban_channel = bot.get_channel(gameban_channel_id)
            if gameban_channel:
                state = "game_ban_issued" if "game_ban_issued" in changes else "game_ban_revoked"
                embed = ce.game_ban_embed(orig_name, cur_name, old_user['NumberOfGameBans'], new_user['NumberOfGameBans'], avatar_url, state)
                old_user['NumberOfGameBans'] = new_user['NumberOfGameBans']
                await gameban_channel.send(embed=embed)
            else:
                print(colored("Could not send message to gameban channel", "red"))
                print(colored(f"Gameban detected, state={state}", "blue"))

        # Logic for a vac ban event
        if "vac_ban" in changes:
            other_bans_channel = bot.get_channel(other_bans_channel_id)
            if other_bans_channel:
                state = "vac_ban_issued" if "vac_ban_issued" in changes else "vac_ban_revoked"
                prev_vac_bans = old_user['NumberOfVACBans']
                cur_vac_bans = new_user['NumberOfVACBans']
                embed = ce.vac_ban_embed(orig_name, cur_name, prev_vac_bans, cur_vac_bans, avatar_url, state)
                await other_bans_channel.send(embed=embed)
            else:
                print(colored("Could not send message to vac_ban channel", "red"))
                print(colored(f"VAC ban detected, state={state}", "blue"))

        # Logic for a community ban event
        if "community_ban" in changes:
            other_bans_channel = bot.get_channel(other_bans_channel_id)
            if other_bans_channel:
                state = "community_ban_issued" if "community_ban_issued" in changes else "community_ban_revoked"
                embed = ce.community_ban_embed(orig_name, cur_name, avatar_url, state)
                await other_bans_channel.send(embed=embed)
            else:
                print(colored("Could not send message to community_ban channel", "red"))
                print(colored(f"Community ban detected, state={state}", "blue"))  
    save_ids()
    ban_loop_active = False
    return

bot.run(token=discord_token)