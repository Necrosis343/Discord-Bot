# Python Discord Bot

from datetime import datetime as dt
import time
import json
import discord
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
intents.invites = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command('help')

@bot.event                                                                      
async def on_ready():                                                           
	print(f'----------------------------------------')                      
	print("\nOLKM is online.\n")
	try:                                                                    
		synced = await bot.tree.sync()                                  
		print(f"Synced {len(synced)} commands")                         
	except Exception as e:                                                  
		print(e)                                         
	for guild in bot.guilds:                                                
		print(f'\nActive in {guild.name} : {guild.id}\n')               
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Economics'))
	print(f'----------------------------------------')
	
@bot.event                                                                      
async def on_member_join(member):                                               
	t=dt.utcnow()                                            
	t=t.strftime("%Y-%m-%d, %H:%M:%S UTC")                                  
	guild=member.guild
	name=member.display_name
	pfp=member.display_avatar
	print(f'----------------------------------------')                      
	print(f"\n{name} has joined {guild}.\n{t}\n")          
	print(f'----------------------------------------')
	i = 0                                                                   
	if guild.id==957547487021920286:
		abt=bot.get_channel(1236609739677241435) 
		mc=bot.get_channel(1250597586205933680)                               
		welc=bot.get_channel(1119832965967515739)
		intro=bot.get_channel(1124666133384003624)                               
		main=bot.get_channel(1230463798868185139)
		dm=await member.create_dm()
		civil=discord.utils.get(guild.roles, id=1114312387105923214)
		embed=discord.Embed(title=f"**Welcome, {name}!**")
		embed.set_image(url="https://cdn.dribbble.com/users/76761/screenshots/827372/time-and-money.gif")
		# Ghost ping
		g=await abt.send(f"{member.mention}")
		await g.delete()
		# Member Count
		for m in guild.members:
			i+=1
		await mc.edit(name=f"Total Members: {i}")
		# Welcome message
		await welc.send(f"<a:welcome1:1070410706761023658><a:welcome2:1070410773681156218>, {member.mention} <:02love:1071351144590356542>\nYou've joined **{guild}**; You are member **{i}**. \nMake an introduction in {intro.mention} to speak in {main.mention}.", embed=embed)
		try:
			await dm.send(f"Thank you, for joining {guild.name}! \nFinish the onboarding process, and make an introduction in {intro.mention}, for full-access to the server.")
#			await dm.send(f"First impressions matter, so send an introduction; {intro.mention}.\nMessage <@602358651788853268>, if you have any question comments or concerns!")
		except:
			print("DM failed.")

bot.run('')
