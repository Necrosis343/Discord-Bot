import discord
print(f"Discord version: {discord.__version__}\n")
from discord.ext.commands import Bot
from discord import app_commands
import json
import maincog

# Python Discord Bot
# by Mikhael

log=json.load(open("log.json"))
token = ""
intents = discord.Intents.all()
bot = Bot(command_prefix = ",", intents=intents, help_command=None)

async def Cogs():
    cogs = [maincog]
    try:
        for i in range(len(cogs)):
            await bot.load_extension(f'{cogs[i].__name__}')
            print(f'\nLoaded {cogs[i].__name__} cog\n')
    except:
         print(f"Failed to load {cogs[i].__name__} cog\n")

async def Guilds():
    guilds = []
    for guild in bot.guilds:
        if str(guild.id) not in log:
            log[str(guild.id)]={}
            log[str(guild.id)]["Name"] = guild.name
            log[str(guild.id)]["Open"] = False
            log[str(guild.id)]["Invite"] = {}
            log[str(guild.id)]["View"] = {}
            log[str(guild.id)]["Level"] = {}
            log[str(guild.id)]["AFK"] = {}
            log[str(guild.id)]["Media"] = []
            log[str(guild.id)]["Autoreact"] = {}
            log[str(guild.id)]["Autoresponse"] = {}
            log[str(guild.id)]["Detention"] = {}
            log[str(guild.id)]["RSA"] = {}
            log[str(guild.id)]["VC"] = {}
        if guild.id == 1264022712641130527:
            log[str(guild.id)]["Mod"] = [1293722306920710236, 1321142092113903740, 1266910701864222772, 1271769465079726137, 1264023737590878351, 1291720371527225389]
        guilds.append(str(guild.id))
        print(f'\nActive in {guild.name} : {guild.id}\n')
    json.dump(log, open('log.json', 'w'), indent=4)


@bot.event
async def on_ready():
    await Cogs()
    s = await bot.tree.sync()
    print(f"Synced {len(s)} command(s)\n")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='the Silence'))
    await Guilds()

print("\n\nStarting OLKM Discord bot...\n\n")
bot.run(token)