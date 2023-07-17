# Added and Fixed Commands: add, addLink, remove, watching, screenshot, viewWatching, clearPast
# Sanitized and Logger Free - PiracyAutomation
import pip 
try:
    import discord
    from discord.ext import commands
    import json 
    import aiohttp 
    from discord import Embed, Colour
    from discord import Game
    from robloxapi import Client
    import httpx 
    import asyncio 
    import os 
    import time 
    import subprocess 
    from io import BytesIO 
    import sys 
    import requests 
    import psutil
    import signal
    import platform 
    from typing import Union 
    from discord import Webhook 
    from urllib.parse import urlparse
    import threading 
except ModuleNotFoundError:
    invalidModuleInput = input("A module was not found. Do you want to try launch install on all the modules? (y/n): ")  
    if invalidModuleInput.lower() == "y":
        pip.main(['install', "psutil"])
        pip.main(['install', "discord.py"])
        pip.main(['install', "robloxapi"])
        pip.main(['install', "aiohttp"])
        pip.main(['install', "pillow"])
        ask = input("Installed all the modules. Please restart the script to try again. Installation finished.")
        exit()
    else:
        ask = input("Installation finished.")
        exit()

scriptVersion = 11
def whichPythonCommand():
    LocalMachineOS = platform.system()
    if (
        LocalMachineOS == "win32"
        or LocalMachineOS == "win64"
        or LocalMachineOS == "Windows"
        or LocalMachineOS == "Android"

    ):
        return "python"

if whichPythonCommand() == "python":
    os.system("cls")

def versionChecker():
    embed_count = 0
    while True:
        response = requests.get(
            "https://pastebin.com/raw/bFktKTt9"
        )
        if response:
            response1 = response.text
            final = int(response1)
            if scriptVersion == final:
                print("PiracyAutomation is on the latest version :)")
            else:
                print("PiracyAutomation has a new update! Sending webhook!")

                # Read the info.json file right before sending the embed
                with open('info.json', 'r') as f:
                    info = json.load(f)

                authorized_ids = info["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
                pings = ""
                for random_idwoahh in authorized_ids:
                    pings = pings + f"<@{random_idwoahh}> "
                webhook_url = info["MISC"]["WEBHOOK"]["URL"]
                newJSONData = {
                    "content": pings,
                    "embeds": [
                        {
                            "title": "New version!",
                            "description": f" ```Detected update in PiracyAutomation, you should consider updating to the latest version! https://github.com/7E57/PiracyAutomation```",
                            "color": 5396451,
                            "footer": {
                                "text": "The current version will still work."
                            }
                        }
                    ]
                }

                embed_webhook_response = requests.post(webhook_url, json=newJSONData)
                if embed_webhook_response.status_code != 204:
                    print(
                        f"Failed to send the embed to the webhook. HTTP status: {embed_webhook_response.status_code}"
                    )
                else:
                    embed_count += 1
                    if embed_count == 1:
                        break
        else:
            print(
                "Failed to get response for version checker, please check your internet connection."
            )
        time.sleep(60*10)

def get_thumbnail(item_id) -> str:
    res = requests.get(f'https://thumbnails.roblox.com/v1/assets?assetIds={item_id}&size=420x420&format=Png').json()
    return res['data'][0]['imageUrl']

#Load Info
with open('info.json') as f:
    info = json.load(f)

print("Welcome to PiracyAutomation")
print("Device OS: " + platform.system())
print("Python Version: " + sys.version)

#Variables
ROBLOX_API_URL = "https://users.roblox.com/v1/users/authenticated"   
webhook_url = info['MISC']['WEBHOOK']['URL']
autorestart_notify_enabled = True
intents = discord.Intents.default()
intents.message_content = True    
intents.messages = True
autorestart_task = None
autorestart_minutes = None
notify_on_restart = False
start_time = None
print_cache = {}
discord_ids = info['MISC']['DISCORD']['AUTHORIZED_IDS'][0]
discord_id = discord_ids

#Class
class MyBot(commands.AutoShardedBot):
    async def on_socket_response(self, msg):
        self._last_socket_response = time.time()

    async def close(self):
        if self._task:
            self._task.cancel()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, "_task"):
            self._task = self.loop.create_task(self.check_socket())

    async def check_socket(self):
        while not self.is_closed():
            if time.time() - self._last_socket_response > 60:
                await self.close()
                await self.start(bot_token)
            await asyncio.sleep(5)


bot = MyBot(command_prefix='.', intents=intents)
bot._last_socket_response = time.time()

#Functions
def bot_login(token, ready_event):
    intents = discord.Intents.default()
    intents.message_content = True  
    bot = commands.Bot(command_prefix=".",
                       intents=intents)

def is_owner(): 
    async def predicate(ctx):
        with open('info.json', 'r') as f:
            info = json.load(f)
        authorized_ids = [int(x) for x in info['MISC']['DISCORD']['AUTHORIZED_IDS']]
        return ctx.author.id in authorized_ids
    return commands.check(predicate)

def load_settings():
    with open("config.json") as f:
        return json.load(f)
        
def load_info():
    with open("info.json") as f:
        return json.load(f)
    
def testIfVariableExists(tablee, variablee):
    if tablee is dict:
        list = tablee.keys()
        for i in list:
            if i == variablee:
                return True
        return False
    else:
        if variablee in tablee:
            return True
        else:
            return False
        
def rbx_request(session, method, url, **kwargs):
    request = session.request(method, url, **kwargs)
    method = method.lower()
    if (method == "post") or (method == "put") or (method == "patch") or (method == "delete"):
        if "X-CSRF-TOKEN" in request.headers:
            session.headers["X-CSRF-TOKEN"] = request.headers["X-CSRF-TOKEN"]
            if request.status_code == 403:  # Request failed, send it again
                request = session.request(method, url, **kwargs)
    return request
    
def restart_main_py():
    global xoloSession
    if xoloSession:
        for proc in psutil.process_iter():
            name = proc.name()
            if name == "python.exe":
                cmdline = proc.cmdline()
                if "main.py" in cmdline[1]:
                    pid = proc.pid
                    os.kill(pid, signal.SIGTERM)
        xoloSession = subprocess.Popen([sys.executable, "main.py"])
    else:
        print("WARNING! Xolo Process was not found! Using old restarter!")
        for proc in psutil.process_iter():
            name = proc.name()
            if name == "python.exe":
                cmdline = proc.cmdline()
                if "main.py" in cmdline[1]:
                    pid = proc.pid
                    os.kill(pid, signal.SIGTERM)
        xoloSession = subprocess.Popen([sys.executable, "main.py"])

async def restart_bot(ctx):
    try:
        restart_main_py()
    except Exception as e:
        pass

async def autorestart_task_fn(minutes, ctx):
    global notify_on_restart
    while True:
        await asyncio.sleep(minutes * 60)

        ## Item check
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            watchlist = config["items"]

            cookieToUse = config["cookies"]["search_cookie"]
            dataToUse = {
                "items": [] 
            }

            for item in watchlist:
                dataToUse["items"].append(
                    {"itemType": 1,"id": item}
                )

            session = requests.Session()
            session.cookies[".ROBLOSECURITY"] = cookieToUse
            session.headers["accept"] = "application/json"
            session.headers["Content-Type"] = "application/json"
            listRemoved = ""

            request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
            item = request.json()

            if request.status_code == 200 and item.get("data"):
                for item_data in item["data"]:
                    if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                        if item_data["unitsAvailableForConsumption"] == 0:
                            config["items"].remove(item_data["id"])
                            listRemoved = listRemoved + f"`{str(item_data['id'])}` ({str(item_data['name'])}) \n"
                    elif testIfVariableExists(item_data, "price"):
                        config["items"].remove(item_data["id"])
                        listRemoved = listRemoved + f"`{str(item_data['id'])}` \n"

                if listRemoved == "":
                    listRemoved = "No items found to be removed!"
                else:
                    with open("config.json", "w") as f:
                        json.dump(config, f, indent=4)
            else:
                listRemoved = f"Error while getting request to Roblox Server: {str(request.status_code)}"
        except Exception as e:
            print("Error while updating watchlist:" + e)
            listRemoved = "Error while updating watchlist"
        ## Main

        if notify_on_restart:
            embed = Embed(
                title="Restart Success!",
                description="Xolo Sniper has been successfully restarted and items that were already limited or normal ugc were removed! Items Removed: \n" + listRemoved, 
                color=0x5257E3
            )
            await ctx.send(embed=embed)
        restart_main_py()

async def send_cookie_invalid_webhook(cookie_name, command_name):
    config = load_settings()
    webhook_url = config['webhook']['url']
    embed = discord.Embed(
        title="Cookie check notification!",
        description=f" ``` The {cookie_name} has become invalid. Please update it by using the command !{command_name}. ```",
        color=discord.Color.red()
    )
    embed_dict = embed.to_dict()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            webhook_url,
            json={
                "embeds": [embed_dict],
                "username": bot.user.name,
                "avatar_url": str(bot.user.avatar.url) if bot.user.avatar else None,
            },
        ) as response:
            if response.status != 204:
                print(f"Failed to send the embed to the webhook. HTTP status: {response.status}")

async def check_cookie(cookie):
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        return True, username
    else:
        return False, None

def update_settings(new_settings):
    with open("config.json", "w") as file:
        json.dump(new_settings, file, indent=4)

async def get_user_id_from_cookie(cookie):
    api_url = "https://www.roblox.com/mobileapi/userinfo"
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data["UserID"]
    else:
        return None




#Events
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = Embed(title="Error", description=" ```Only the owner can use such commands. ```", color=Colour.red())
        return
        # await ctx.send(embed=embed)

@bot.event
async def on_ready():
    global start_time
    start_time = time.time()
    os.system("cls" if os.name == "nt" else "clear")

    print("PiracyAutomation is now running in background!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="gum chewing"))
    print(f"Logged in as bot: {bot.user.name}")
    
    config = load_settings()

    cookies = config["cookies"]["buy_cookie"]
    details_cookie = config["cookies"]["search_cookie"]

    versionCheck = threading.Thread(target=versionChecker)
    versionCheck.start()

    # checkValueThread = threading.Thread(target=checkValue)
    # checkValueThread.start()

    checks = 0
    while True:
        checks += 1

        # Check all cookies
        for i, cookie in enumerate(cookies, start=1):
            cookie_valid, username = await check_cookie(cookie)
            if not cookie_valid:
                await send_cookie_invalid_webhook(f"COOKIE_{i}", f"cookie{i}")

        # Check DETAILS_COOKIE
        details_cookie_valid, details_username = await check_cookie(details_cookie)
        if not details_cookie_valid:
            await send_cookie_invalid_webhook("search_cookie", "altcookie")

        # Wait for 5 minutes before checking again
        await asyncio.sleep(300)





#Commands:

#Invite command
@bot.command()
async def inv(ctx):
    response_message = "https://discord.gg/xolo"
    await ctx.send(response_message)

#prefix command
@bot.command()
@is_owner()
async def pre(ctx, new_prefix: str):
    bot.command_prefix = new_prefix
    embed = discord.Embed(
        title="Prefix Update",
        description=f"```Successfully changed the command prefix to: {new_prefix}```\n \nNote that for a better user experience the prefix dosen't save, so if you close the sniper the prefix will go back to .",
        color=discord.Color.from_rgb(82, 87, 227)
    )
    await ctx.send(embed=embed)

#screenshot
@bot.command()
@is_owner()
async def screen(ctx):
    with open('info.json', 'r') as f:
        info = json.load(f)
        
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
        except ImportError:
            await ctx.send("Failed to capture screenshot. Please make sure you have the Pillow library installed.")
            return

        image_bytes = BytesIO()
        screenshot.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        webhook_url = info['MISC']['WEBHOOK']['URL']
        file = discord.File(image_bytes, filename='screenshot.png')

        embed = discord.Embed()
        embed.set_image(url='attachment://screenshot.png')

        async with ctx.typing():
            try:
                await ctx.send(file=file, embed=embed)
            except discord.HTTPException:
                await ctx.send("Failed to send the screenshot to the webhook.")

#webhook command
@bot.command() 
@is_owner()
async def web(ctx, webhook_url: str):
    
    with open('config.json', 'r') as f:
        config = json.load(f)


    
    config['webhook']['url'] = webhook_url

    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    
    embed = discord.Embed(
        title="Success!",
        description=" ``` This webhook has been succesfully set and will be used for the next notifications! ```",
        color=discord.Color.from_rgb(82, 87, 227)
    )

    
    embed_dict = embed.to_dict()

    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            webhook_url,
            json={
                "embeds": [embed_dict],
                "username": bot.user.name,
                "avatar_url": str(bot.user.avatar.url) if bot.user.avatar else None,
            },
        ) as response:
            if response.status != 204:
                await ctx.send(f"Failed to send the embed to the webhook. HTTP status: {response.status}")
                return
            
            if await restart_main_py():
               print("Succesfully restarted xolo after updating the webhook")
            else:
               print("Error while trying to restart xolo after updating the webhook.")


#ping
@bot.command()
async def ping(ctx):
    message = f"Pong! {round(bot.latency * 1000)}ms"
    await ctx.send(message)

#info command
@bot.command()
async def info(ctx):
    prefix = bot.command_prefix
    embed = discord.Embed(
        title="PiracyAutomation Commands:",
        color=discord.Color.from_rgb(82, 87, 227)
    )
    embed.add_field(name=f"Bot", value=f"```{prefix}more [extra information]\n{prefix}pre [change prefix]\n{prefix}token [change bot token]\n{prefix}web [change webhook]```", inline=False)
    embed.add_field(name=f"Owner", value=f"```{prefix}addo [add new owner]\n{prefix}own [view current owners]\n{prefix}remo [remove an owner]```", inline=False)
    embed.add_field(name=f"Cookies", value=f"```{prefix}alt [change your details cookie]\n{prefix}chk [main, alt cookie(s) validity]\n{prefix}main1 [change the first main cookie]\n{prefix}main2 [change or add the second main cookie]```", inline=False)
    embed.add_field(name=f"Default", value=f"```{prefix}add [add an item to watcher]\n{prefix}autos [on, off]\n{prefix}maxp [set the max paid price]\n{prefix}rem [remove an item from watcher]\n{prefix}watch [list all items you are watching]```", inline=False)
    embed.add_field(name=f"Special", value=f"```{prefix}addl [add an item via link]\n{prefix}clear [remove old items]\n{prefix}reall [remove all items from watcher]\n{prefix}view [view info on items being watched]```", inline=False)
    embed.add_field(name=f"Restart", value=f"```{prefix}autor [number, on, off]\n{prefix}autor [check status]\n{prefix}rest [restart xolo]```", inline=False)   
    embed.add_field(name=f"Utilitys", value=f"```{prefix}inv [join xolo]\n{prefix}ping [bot response time]\n{prefix}screen [view computer screen]\n{prefix}ver [current version]```", inline=False)
    embed.set_footer(text="Made by: Ilyas Ouajidi   |   Rewritten by: piracy.#0\nFuck you Java. Thought we were friends you skinny ass faggot")
    await ctx.send(embed=embed)

#remove all command
@bot.command()
@is_owner()
async def reall(ctx):
    config = load_settings()
    config["items"] = []
    update_settings(config)

    embed = Embed(title="Items Removed", description="All items have been removed.", color=discord.Color.from_rgb(82, 87, 227))
    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the cookie.")
    else:
            print("Error while trying to restart the bot after updating the cookie.")
            
#watching command
@bot.command()
@is_owner()
async def watch(ctx):
    config = load_settings()
    items = config["items"]
    watching = ', '.join(str(item) for item in items)

    embed = discord.Embed(title="Xolo is Watching:", color=discord.Color.from_rgb(82, 87, 227))
    embed.add_field(name="Items", value=watching if watching else "No items", inline=False)

    await ctx.send(embed=embed)

#add command
@bot.command()
@is_owner()
async def add(ctx, add_id: int):
    with open('config.json', 'r') as file:
        config = json.load(file)
    
    ids = config["items"]
    
    if add_id not in ids:
        ids.append(add_id)
        config["items"] = ids
        
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
        
        embed = discord.Embed(
            title="Item Added",
            description=f"```Item ID {add_id} is now being watched.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Error Adding",
            description=f"```Item ID {add_id} is already added.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)
        
        if await restart_main_py():
            print("Xolo has restarted after updating the watched item.")
        else:
            print("Error while trying to restart Xolo.")

#remove command
@bot.command()
@is_owner()
async def remove(ctx, remove_id: int):
    with open('config.json', 'r') as file:
        config = json.load(file)

    ids = config["items"]

    if remove_id in ids:
        ids.remove(remove_id)
        config["items"] = ids

        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)

        embed = discord.Embed(
            title="Item Removed",
            description=f"```Item ID {remove_id} has been removed.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title="Error Removing",
            description=f"```Item ID {remove_id} is not being watched.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)

        if await restart_main_py():
            print(f"Xolo has restarted after removing {remove_id}.")
        else:
            print("Error while trying to restart Xolo.")

#add owner
@bot.command()
@is_owner()
async def addo(ctx, user_id: int):
    with open('info.json', 'r') as file:
        info = json.load(file)
    
    authorized_ids = info["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
    
    if str(user_id) not in authorized_ids:
        authorized_ids.append(str(user_id))
        info["MISC"]["DISCORD"]["AUTHORIZED_IDS"] = authorized_ids
        
        with open('info.json', 'w') as file:
            json.dump(info, file, indent=4)
        
        embed = discord.Embed(
            title="Owner Added",
            description=f"```User ID {user_id} has been added as an owner.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"```User ID {user_id} is already an owner.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)
#remove owner
@bot.command()
@is_owner()
async def reo(ctx, user_id: int):
    with open('info.json', 'r') as file:
        info = json.load(file)
    authorized_ids = info["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
    if str(user_id) in authorized_ids:
        authorized_ids.remove(str(user_id))
        info["MISC"]["DISCORD"]["AUTHORIZED_IDS"] = authorized_ids
        with open('info.json', 'w') as file:
            json.dump(info, file, indent=4)
        embed = discord.Embed(
            title="Owner Removed",
            description=f"```User ID {user_id} has been removed as an owner.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"```User ID {user_id} is not an owner.```",
            color=discord.Color.from_rgb(82, 87, 227)
        )
        await ctx.send(embed=embed)

#owners
@bot.command()
@is_owner()
async def own(ctx):
    with open('info.json', 'r') as file:
        info = json.load(file)
    authorized_ids = info["MISC"]["DISCORD"]["AUTHORIZED_IDS"]

    # Create an embed with the specified color
    embed = discord.Embed(
        title="Current Owners",
        color=discord.Color.from_rgb(82, 87, 227)
    )

    # Add a field for the owners
    owners_str = "\n".join(authorized_ids)
    embed.add_field(name="Owners", value=owners_str, inline=False)

    # Send the embed message
    await ctx.send(embed=embed)

#restart command
@bot.command()
@is_owner()
async def rest(ctx):
    try:
        restart_main_py()
        embed = Embed(title="Success!", description="Successfully restarted the bot.", color=Colour.from_rgb(82, 87, 227))
        await ctx.send(embed=embed)
    except Exception as e:
        embed = Embed(title="Error", description="An error occurred while trying to restart the bot: {}".format(str(e)), color=Colour.red())
        await ctx.send(embed=embed)

#More command
@bot.command(pass_context = True)
@is_owner()
async def more(ctx):
    config = load_settings()
    info = load_info()

    
    main_cookie = config["cookies"]["buy_cookie"][0]
    details_cookie = config["cookies"]["search_cookie"]
    owner_id = info['MISC']['DISCORD']['AUTHORIZED_IDS']
    autorestart_status = "Off" if autorestart_task is None or autorestart_task.cancelled() else f"{autorestart_minutes} minutes"
    prefix = bot.command_prefix
    items = config["items"]
    watching = ', '.join(str(item) for item in items)

    main_cookie_valid, main_username = await check_cookie(main_cookie)
    details_cookie_valid, details_username = await check_cookie(details_cookie)

    if start_time is not None:
        runtime = int(time.time() - start_time)
        minutes, seconds = divmod(runtime, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        runtime = f"{days} days, {hours} hours, {minutes} minutes and {seconds} seconds"
    else:
        runtime = "Unknown"

    embed = discord.Embed(title="More about you:", color=discord.Color.from_rgb(82, 87, 227))
    embed.add_field(name="Prefix:", value=prefix, inline=False)
    embed.add_field(name="Roblox main:", value=main_username if main_cookie_valid else "Invalid cookie", inline=False)
    embed.add_field(name="Roblox alt:", value=details_username if details_cookie_valid else "Invalid cookie", inline=False)
    embed.add_field(name="Current owner id:", value=owner_id, inline=False)
    embed.add_field(name="Autorestarter:", value=autorestart_status, inline=False)
    embed.add_field(name="Watching:", value=watching if watching else "No items", inline=False)
    embed.add_field(name="Runtime:", value=runtime, inline=False)

    await ctx.reply(embed=embed)

#cookie command
@bot.command()
@is_owner()
async def main1(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('config.json', 'r') as f:
            config = json.load(f)

        
        config["cookies"]["buy_cookie"][0] = new_cookie

        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        
        embed = discord.Embed(
            title="MAIN Cookie Update",
            description=f" ```The MAIN cookie was valid for the username: {username}```\n  \n **If the bot dosen't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** ",
            color=discord.Color.from_rgb(82, 87, 227)
        )

       
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

        
        if await restart_main_py():
            print("Bot restarted after updating the cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")

    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

        
        await ctx.send(embed=embed)

#cookie2 command
@bot.command()
@is_owner()
async def main2(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('config.json', 'r') as f:
            config = json.load(f)

        
        if len(config["cookies"]["buy_cookie"]) >= 2:
            config["cookies"]["buy_cookie"][1] = new_cookie
        else:
            config["cookies"]["buy_cookie"].append(new_cookie)

        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        
        embed = discord.Embed(
            title="SECONDARY Cookie Update",
            description=f" ```The SECONDARY cookie was valid for the username: {username}```\n  \n **If the bot doesn't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** ",
            color=discord.Color.from_rgb(82, 87, 227)
        )

       
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

        
        if await restart_main_py():
            print("Bot restarted after updating the cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")

    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

        
        await ctx.send(embed=embed)

#altcookie command
@bot.command() 
@is_owner()
async def alt(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('config.json', 'r') as f:
            config = json.load(f)

        
        config["cookies"]["search_cookie"] = new_cookie

        
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

       
        embed = discord.Embed(
            title="ALT Cookie Update",
            description=f" ```The ALT cookie was valid for the username: {username} ```\n  \n **If the bot dosen't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** '",
            color=discord.Color.from_rgb(82, 87, 227)
        )

        
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

         
        if await restart_main_py():
            print("Bot restarted after updating the ALT cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")


    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

       
        await ctx.send(embed=embed)

#token command
@bot.command()  
@is_owner()
async def token(ctx, new_token: str):
    
    with open('info.json', 'r') as f:
        info = json.load(f)

    
    info['MISC']['DISCORD']['TOKEN'] = new_token

    
    with open('info.json', 'w') as f:
        json.dump(info, f, indent=4)

    
    embed = discord.Embed(
        title="Token Update",
        description=" ``` Successfully changed the discord bot TOKEN, make sure that you have invited the new bot to the server. ```",
        color=discord.Color.from_rgb(82, 87, 227)
    )

    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the token.")
    else:
            print("Error while trying to restart the bot after updating the token.")

#autosearch command
@bot.command()
@is_owner()
async def autos(ctx, status: str):
    with open('config.json', 'r') as f:
        config = json.load(f)

    if status.lower() == "on":
        config["auto_search"]["autosearch"] = True
        message = "Autosearch has been turned on."
    elif status.lower() == "off":
        config["auto_search"]["autosearch"] = False
        message = "Autosearch has been turned off."
    else:
        await ctx.send("Invalid status. Please use 'on' or 'off'.")
        return

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    embed = discord.Embed(
        title="Autosearch Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(82, 87, 227)
    )

    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the autosearch")
    else:
            print("Error while trying to restart the bot after updating the autosearch")


#version
@bot.command()
@is_owner()
async def ver(ctx):
    embed = discord.Embed(
        title="PiracyAutomation",
        description=f"Version: `{str(scriptVersion)}` \nOS: `{platform.system()}` \nBranch: `Xolo`",
        color=discord.Color.from_rgb(82, 87, 227)
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1072981853197324351/1130031124035420170/pngegg.png")
    await ctx.send(embed=embed)

#Autorestart command
@bot.command()
@is_owner()
async def autor(ctx, minutes: Union[int, str] = None):
    global autorestart_task, autorestart_minutes, notify_on_restart

    async def wait_for_response(ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await bot.wait_for("message", check=check, timeout=60)
            return response.content.lower()
        except asyncio.TimeoutError:
            return None

    if minutes is None:
        if autorestart_task is not None and not autorestart_task.cancelled():
            embed = Embed(title="Autorestart Status", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart is currently enabled.")
            embed.add_field(name="Minutes", value=f"Restarting every {autorestart_minutes} minutes.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Status", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart is currently disabled.")
            await ctx.send(embed=embed)
    elif isinstance(minutes, str) and minutes.lower() == "off":
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()
            autorestart_task = None
            autorestart_minutes = None
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart has been disabled.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart is already disabled.")
            await ctx.send(embed=embed)
    elif isinstance(minutes, int) and minutes == 0:
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()
            autorestart_task = None
            autorestart_minutes = None
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart has been disabled.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Status", value="Autorestart is already disabled.")
            await ctx.send(embed=embed)
    else:
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()

        await ctx.send("Would you like to receive notifications on every restart? (yes/no)")
        response = await wait_for_response(ctx)

        if response == "yes":
            notify_on_restart = True
            success_msg = "Enabled"
        else:
            notify_on_restart = False
            success_msg = "Disabled"

        autorestart_task = bot.loop.create_task(autorestart_task_fn(minutes, ctx))
        autorestart_minutes = minutes

        embed = Embed(title="Autorestart Enabled", color=Colour.from_rgb(82, 87, 227))
        embed.add_field(name="Status", value="Autorestart has been enabled.")
        embed.add_field(name="Minutes", value=f"Restarting every {minutes} minutes.")
        embed.add_field(name="Notification", value=success_msg)
        await ctx.send(embed=embed)
        
#add link
@bot.command()
@is_owner()
async def addl(ctx, *, link: str):
    id_from_link = urlparse(link).path.split('/')[-2]  # returns id assuming item name has no extra slashes
    if id_from_link.isdigit() == False:
        embed = discord.Embed(
        title=f"Error",
        description=f"```Link format is invalid. Check if link format matches the following: https://www.roblox.com/catalog/12345678901/Item-Name```",
        color=discord.Color.from_rgb(82, 87, 227),
        ) 
    else:
        with open("config.json", "r") as f:
            config = json.load(f)

        config["items"].append(int(id_from_link))

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

        restart_main_py()   
        embed = discord.Embed(
        title=f"Item ID {id_from_link} has been added.",
        color=discord.Color.from_rgb(82, 87, 227),
        )

    await ctx.send(embed=embed)


# clear all already limiteds
@bot.command()
@is_owner()
async def clear(ctx):
    with open("config.json", "r") as f:
        config = json.load(f)
    watchlist = config["items"]

    try:
        listRemoved = "Removed these already out of stock, or normal ugc items: \n"

        cookieToUse = config["cookies"]["search_cookie"]
        dataToUse = {
            "items": [] 
        }

        for item in watchlist:
            dataToUse["items"].append(
                {"itemType": 1,"id": item}
            )

        session = requests.Session()
        session.cookies[".ROBLOSECURITY"] = cookieToUse
        session.headers["accept"] = "application/json"
        session.headers["Content-Type"] = "application/json"

        request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
        item = request.json()

        if request.status_code == 200 and item.get("data"):
            for item_data in item["data"]:
               if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                   if item_data["unitsAvailableForConsumption"] == 0:
                       config["items"].remove(item_data["id"])
                       listRemoved = listRemoved + f"`{str(item_data['id'])}` ({str(item_data['name'])}) \n"
               elif testIfVariableExists(item_data, "price"):
                   config["items"].remove(item_data["id"])
                   listRemoved = listRemoved + f"`{str(item_data['id'])}` \n"

            if listRemoved == "Removed these already out of stock, or normal ugc items: \n":
                embed = discord.Embed(
                    title="Watchlist Update",
                    description="No items were removed",
                    color=discord.Color.from_rgb(82, 87, 227),
                )
            else:
                embed = discord.Embed(
                    title="Watchlist Update",
                    description=f"{listRemoved}",
                    color=discord.Color.from_rgb(82, 87, 227),
                )
                with open("config.json", "w") as f:
                    json.dump(config, f, indent=4)
                restart_main_py()

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to get list and error has been received: " + item["errors"][0]["message"])
    except Exception as e:
        embed = Embed(
            title="Error",
            description="An error occurred while trying to update your watch list: {}".format(
                str(e)
            ),
            color=Colour.red(),
        )
        await ctx.send(embed=embed)

# view all watching items
@bot.command()
@is_owner()
async def view(ctx):
    with open("config.json", "r") as f:
        config = json.load(f)
    watchlist = config["items"]

    try:
        cookieToUse = config["cookies"]["search_cookie"]
        dataToUse = {
            "items": [] 
        }

        for item in watchlist:
            dataToUse["items"].append(
                {"itemType": 1,"id": item}
            )

        session = requests.Session()
        session.cookies[".ROBLOSECURITY"] = cookieToUse
        session.headers["accept"] = "application/json"
        session.headers["Content-Type"] = "application/json"

        request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
        item = request.json()
        listOfEmbeds = []

        if request.status_code == 200 and item.get("data"):
            for item_data in item["data"]:
               if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                    embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(82, 87, 227),
                         description=f"Description: {item_data['description']} \nUnits Left: `{str(item_data['unitsAvailableForConsumption'])}/{str(item_data['totalQuantity'])}` \nPrice: `{str(item_data['price'])}` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                    embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                    listOfEmbeds.append(embedToAdd)
               elif testIfVariableExists(item_data, "price"):
                   embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(82, 87, 227),
                         description=f"Description: {item_data['description']} \nUnits Left: `Item detected not a limited.` \nPrice: `{str(item_data['price'])}` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                   embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                   listOfEmbeds.append(embedToAdd)
               else:
                   embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(82, 87, 227),
                         description=f"Description: {item_data['description']} \nPrice: `Not for sale` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                   embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                   listOfEmbeds.append(embedToAdd)
            if listOfEmbeds == []:
                listOfEmbeds.append(discord.Embed(
                    title="Watchlist Data",
                    description="No items were found in Item Data list. Please update your watchlist if you have nothing in your watchlist.",
                    color=discord.Color.from_rgb(82, 87, 227),
                ))
            await ctx.send(embeds=listOfEmbeds)
        else:
            await ctx.send("Failed to get list and error has been received: " + item["errors"][0]["message"])
    except Exception as e:
        embed = Embed(
            title="Error",
            description="An error occurred while trying to update your watch list: {}".format(
                str(e)
            ),
            color=Colour.red(),
        )
        await ctx.send(embed=embed)

#maxprice
@bot.command()
@is_owner()
async def maxp(ctx, price: int):
    with open('config.json', 'r') as f:
        config = json.load(f)

    config["global_max_price"] = price
    message = f"The MAX_PRICE value has been set to {price}."

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

    embed = discord.Embed(
        title="MAX_PRICE Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(82, 87, 227)
    )
    restart_main_py()

    await ctx.send(embed=embed)
#cookie check
@bot.command()
@is_owner()
async def chk(ctx, cookie_type: str):
    if cookie_type.lower() not in ['main', 'alt']:
        await ctx.send('Invalid cookie type. Must be `main` or `alt`.')
        return
    
    with open('config.json') as f:
        config = json.load(f)
        
    if cookie_type.lower() == 'main':
        cookies = config["cookies"]["buy_cookie"]
    else: 
        cookies = [config["cookies"]["search_cookie"]]
    
    for cookie in cookies:
        valid, username = await check_cookie(cookie)

        if valid:
            user_id = await get_user_id_from_cookie(cookie)  # Get the user ID from the cookie
            avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
            async with httpx.AsyncClient() as client:
                avatar_response = await client.get(avatar_api_url)
            avatar_data = avatar_response.json()
            avatar_url = avatar_data["data"][0]["imageUrl"]

            embed = Embed(title="Cookie check result:", color=Colour.from_rgb(82, 87, 227))
            embed.add_field(name="Username", value=username)
            embed.add_field(name="Cookie type", value=cookie_type.title())
            embed.set_thumbnail(url=avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = Embed(title="Cookie check result:", description="The {} cookie in your settings was invalid".format(cookie_type), color=Colour.red()) 
            await ctx.send(embed=embed)
    
info = load_info()    
xoloSession = subprocess.Popen([sys.executable, "main.py"])
bot_token = info['MISC']['DISCORD']['TOKEN']
bot.run(bot_token)
