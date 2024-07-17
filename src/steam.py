import aiohttp, asyncio, time
import custom_exceptions as ce
from termcolor import colored

async def process_ids(all_steam_ids, steam_api_key):

    # Start time for measuring execution time
    start_time = time.time()

    # divides the steam ids into chunks to avoid the steam web api limit
    chunk_size = 100
    steam_ids_packs = [all_steam_ids[i:i + chunk_size] for i in range(0,len(all_steam_ids), chunk_size)]

    # A list of coro's to be executed at the same time
    api_tasks = []

    # Create dict keys of all steam ids
    new_info = {steam_id: {} for steam_id in all_steam_ids}

    # Creates multiple coro calls to the steam api
    for steam_ids in steam_ids_packs:
        # Create ban tasks
        ban_info_coro = get_ban_data(steam_ids, steam_api_key)
        user_info_coro = get_player_summaries(steam_ids, steam_api_key)

        api_tasks.extend([ban_info_coro, user_info_coro])

    # Get results using coro's
    results = await asyncio.gather(*api_tasks)
    
    # Filter the coro results
    ban_data_raw = [results[i] for i in range(len(results)) if i % 2 == 0]
    user_data_raw = [results[i] for i in range(len(results)) if i % 2 != 0]

    # sections are the divided api requests (for ban info), user is the data within each request
    for section in ban_data_raw:
        for user in section['players']:
            new_user = (new_info[(user['SteamId'])])
            new_user['CommunityBanned'] = user['CommunityBanned']
            new_user['VACBanned'] = user['VACBanned']
            new_user['NumberOfVACBans'] = user['NumberOfVACBans']
            new_user['NumberOfGameBans'] = user['NumberOfGameBans']

    # sections are for the steam user data
    for section in user_data_raw:
        for user in section['response']['players']:
            new_user = (new_info[(user['steamid'])])
            new_user['name'] = user['personaname']

    end_time = time.time()
    print(colored(f"Execution time: {round((end_time-start_time)*1000)}ms", "blue"))
    return new_info

async def get_player_summaries(steam_ids, steam_api_key):
    start_time = time.time()
    # Request url
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_api_key}&steamids={steam_ids}"

    # Check if the steam_ids list is longer than the limit
    if len(steam_ids) > 100:
        return ce.InvalidRequestListError

    # Make request using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                end_time = time.time()
                print(colored(f"API call time: {round((end_time-start_time)*1000)}ms", "blue"))
                return data
            else:
                print("Error")

async def get_ban_data(steam_ids, steam_api_key):
    start_time = time.time()
    # Request URL
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={steam_api_key}&steamids={steam_ids}"

    # Check if the steam_ids list is longer than the limit
    if len(steam_ids) > 100:
        return ce.InvalidRequestListError
    
    # Make request using aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                end_time = time.time()
                print(colored(f"API call time: {round((end_time-start_time)*1000)}ms", "blue"))
                return data
            else:
                print(colored(f"Error -> {response.status}", "red"))

async def get_steam_profile_picture(steam_id, steam_api_key):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_api_key}&steamids={steam_id}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'response' in data and 'players' in data['response'] and len(data['response']['players']) > 0:
                    player = data['response']['players'][0]
                    avatar_url = player['avatarfull']
                    return avatar_url
                else:
                    return None
            else:
                print(f"Failed to fetch data: {response.status}")
                return None