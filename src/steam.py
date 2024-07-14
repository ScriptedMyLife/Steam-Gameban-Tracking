import aiohttp, asyncio

async def process_ids(steam_ids, steam_api_key):

    #TODO add implementation to support over 100 steam ids
    if len(steam_ids) > 100:
        return

    # Create ban tasks
    new_ban_task = get_ban_data(steam_ids, steam_api_key)
    new_user_task = get_player_summaries(steam_ids, steam_api_key)

    # Rust tasks async
    new_ban_data, new_user_data = await asyncio.gather(new_ban_task, new_user_task)

    # Create dict keys
    new_info = {steam_id: {} for steam_id in steam_ids}

    ban_data = new_ban_data['players']
    for user in ban_data:
        new_info_user = new_info[user['SteamId']]

        new_info_user['CommunityBanned'] = user['CommunityBanned']
        new_info_user['VACBanned'] = user['VACBanned']
        new_info_user['NumberOfVACBans'] = user['NumberOfVACBans']
        new_info_user['NumberOfGameBans'] = user['NumberOfGameBans']

    user_data = new_user_data['response']['players']
    for user in user_data:
        new_info_user = new_info[user['steamid']]

        new_info_user['name'] = user['personaname']

    return new_info

async def get_player_summaries(steam_ids, steam_api_key):
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_api_key}&steamids={steam_ids}"

    # Check if the steam_ids list is longer than the limit
    if len(steam_ids) > 100:
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print("Error")

async def get_ban_data(steam_ids, steam_api_key):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={steam_api_key}&steamids={steam_ids}"

    # Check if the steam_ids list is longer than the limit
    if len(steam_ids) > 100:
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print("Error")

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