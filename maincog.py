# Dependecies

from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
import discord
from discord import Member
import json
import time
import discord.voice_state
log=json.load(open("log.json"))
# Library

async def update_data(guild, user):
	if not user.bot:
		if str(user.id) in log[str(guild.id)]["Level"]:
			if user.display_name != log[str(guild.id)]["Level"][str(user.id)][0]:
				log[str(guild.id)]["Level"][str(user.id)][0]=user.display_name
				json.dump(log, open('log.json', 'w'), indent=4)

		else:
			log[str(guild.id)]["Level"][str(user.id)]= []
			log[str(guild.id)]["Level"][str(user.id)].append(user.display_name)
			log[str(guild.id)]["Level"][str(user.id)].append(0)
			log[str(guild.id)]["Level"][str(user.id)].append(0)
			json.dump(log, open('log.json', 'w'), indent=4)
			print(f"\nData updated ({guild.name} : {user.display_name}).\n")

async def add_exp(guild, user, exp):
	if not user.bot:
		log[str(guild.id)]["Level"][str(user.id)][1] += exp
		json.dump(log, open('log.json', 'w'), indent=4)
		print(f"\n{user} got +{exp} exp in {guild}.\n")

async def lvl_up(guild, user):
	logChannel = discord.utils.get(guild.channels, id=1358940063672565891)
	if not user.bot:
		exp = log[str(guild.id)]["Level"][str(user.id)][1]
		lvl = log[str(guild.id)]["Level"][str(user.id)][2]
		lvl_end = int(exp ** (1/4))
		if lvl < lvl_end:
			log[str(guild.id)]["Level"][str(user.id)][2]=int(lvl_end)
			json.dump(log, open('log.json', 'w'), indent=4)
			print(f"\n{user.name} is level {lvl_end}.\n")
			if guild.id == 1264022712641130527:
				await logChannel.send(f"{user.name} is level {lvl_end}")

class KickConfirm(discord.ui.View):
	def __init__(self, m):
		super().__init__(timeout=None)
		self.m = m

	@discord.ui.button(label="Confirm", custom_id="kick_confirm_button", style=discord.ButtonStyle.red)
	async def confirm(self, i:discord.Interaction, b:discord.Button):
		emb = discord.Embed(description=f'The user {self.m} has been kicked.')
		await self.m.kick()
		print(f"\nKicked {self.m}.\n")
		await i.response.send_message(embed=emb)

class BanConfirm(discord.ui.View):
	def __init__(self, m):
		super().__init__(timeout=None)
		self.m = m

	@discord.ui.button(label="Confirm", custom_id="ban_confirm_button", style=discord.ButtonStyle.red)
	async def confirm(self, i:discord.Interaction, b:discord.Button):
		emb = discord.Embed(description=f'The user {self.m} has been banned.')
		await self.m.ban()
		print(f"\nBanned {self.m}.\n")
		await i.response.send_message(embed=emb)

class DeleteConfirm(discord.ui.View):
	def __init__(self, guild, embed):
		super().__init__(timeout=None)
		self.guild = guild
		self.embed = embed

	@discord.ui.button(label="Confirm", custom_id="confirm_button", style=discord.ButtonStyle.red)
	async def Confirm(self, i:discord.Interaction, b:discord.Button):
		two = discord.Embed(title="Deleted", description="Deleted ticket queue.")
		del log[str(self.guild.id)]["View"][str(i.message.id)]
		json.dump(log, open('log.json', "w"), indent=4)
		await self.embed.delete()
		await i.response.send_message(embed=two)

class ArchiveConfirm(discord.ui.View):
	def __init__(self, guild, embed):
		super().__init__(timeout=None)
		self.guild = guild
		self.embed = embed

	@discord.ui.button(label="Confirm", custom_id="confirm_button", style=discord.ButtonStyle.red)
	async def Confirm(self, i:discord.Interaction, b:discord.Button):
		cat = discord.utils.get(i.guild.categories, id=1273541794742669342)
		one = discord.Embed(title="Archived", description=f"Moved ticket to archive.")
		o = {   
			i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
			i.user: discord.PermissionOverwrite(view_channel=False, send_messages=False)}
	
		await i.channel.edit(category=cat, overwrites=o)
		await i.response.send_message(embed=one, ephemeral=True)

	@discord.ui.button(label="Cancel", custom_id="cancel_button", style=discord.ButtonStyle.grey)
	async def Cancel(self, i:discord.Interaction, b:discord.Button):
		await self.embed.delete()

class cwr(discord.ui.Modal, title='Close with reason'):
	reason = discord.ui.TextInput(
		label='reason for closing',
		required=True,
		placeholder='Enter your reason for closing.',
		max_length=250)
		
	async def on_submit(self, i: discord.Interaction):
		cat = discord.utils.get(i.guild.categories, id=1273541794742669342)
		log = discord.utils.get(i.guild.channels, id=1272365731522150403)
		emb = discord.Embed(title="Archived", description=f"Moved ticket to archive.")
		overwrites = {   
			i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
			i.user: discord.PermissionOverwrite(view_channel=False, send_messages=False)}
		await i.channel.edit(category=cat, topic=f'CRW: {self.reason.value}', overwrites=overwrites)
		await log.send(f'{i.channel.mention}, closed with reason: {self.reason.value}')
		await i.response.send_message(embed=emb, ephemeral=True)

class ClaimedTicket(discord.ui.View):
	def __init__(self, guild, embed):
		super().__init__(timeout=None)
		self.guild = guild
		self.embed = embed

	@discord.ui.button(label="Close", custom_id="close_button", style=discord.ButtonStyle.red)
	async def Close(self, i:discord.Interaction, b:discord.Button):
		conf = discord.Embed(title="Close Confirmation", description="Please confirm that you want to close the ticket.")
		conf.set_author(name=i.user.name, icon_url=i.user.avatar)
		e = i.response.send_message(embed=conf)
		await e.edit(view=ArchiveConfirm(self.guild, e))

	@discord.ui.button(label="Close with reason", custom_id="cwr_button", style=discord.ButtonStyle.red)
	async def cwr(self, i:discord.Interaction, b:discord.Button):
		await i.response.send_modal(cwr())

class UnclaimedTicket(discord.ui.View):
	def __init__(self, guild, embed):
		super().__init__(timeout=None)
		self.guild = guild
		self.embed = embed

	@discord.ui.button(label="Close", custom_id="close_button", style=discord.ButtonStyle.red)
	async def close(self, i:discord.Interaction, b:discord.Button):
		conf = discord.Embed(title="Close Confirmation", description="Please confirm that you want to close the ticket.")
		conf.set_author(name=i.user.name, icon_url=i.user.avatar)
		e = await i.response.send_message(embed=conf)
		e.edit(view=ArchiveConfirm(self.guild, e))

	@discord.ui.button(label="Close with reason", custom_id="cwr_button", style=discord.ButtonStyle.red)
	async def cwr(self, i:discord.Interaction, b:discord.Button):
		await i.response.send_modal(cwr())

	@discord.ui.button(label="Claim", custom_id="claim_button", style=discord.ButtonStyle.green)
	async def claim(self, i:discord.Interaction, b:discord.Button):
		HR = discord.utils.get(i.guild.roles, id=1264023737590878351)
		if HR in i.user.roles:
			claimEmb = discord.Embed(title="Your ticket has been claimed ✅", description=f'{i.user.mention} has claimed this ticket.')
			msg = await i.response.send_message(embed=claimEmb)
			await self.embed.edit(view=None)
			await msg.edit(view=ClaimedTicket(i.guild, msg))
		else:
			claimEmb = discord.Embed(description="Must be a HR to claim a ticket.")
			await i.response.send_message(embed=claimEmb, ephemeral=True)

class Queue(discord.ui.View):
	def __init__(self, bot, guild, channel, embed):
		super().__init__(timeout=None)
		self.bot:commands.Bot = bot
		self.guild:discord.Guild = guild
		self.channel = channel
		self.embed:discord.Embed = embed
		self.gm = discord.utils.get(guild.roles, id=1266910701864222772)
		self.manager = discord.utils.get(guild.roles, id=1271769465079726137)

	@discord.ui.button(label="🛎️ Open", custom_id="ticket_button", style=discord.ButtonStyle.green)
	async def Open(self, i:discord.Interaction, b:discord.ui.Button):
		if log[str(i.guild.id)]["Open"]:
			cat = discord.utils.get(i.guild.categories, id=1273541204193054801)
			logChannel = discord.utils.get(i.guild.channels, id=1264022712641130531)
			overwrites = {
				i.guild.default_role: discord.PermissionOverwrite(view_channel=False),
				i.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
			c =  await i.guild.create_text_channel(name=f"{i.user.name}'s-ticket", overwrites=overwrites, reason=f"{i.user.name} created a ticket", category=cat)
			emb = discord.Embed(title="Your Ticket 🎟️", description=c.mention)
			emb2 = discord.Embed(description="Please state your reason for opening a ticket, and wait for staff.")
			await logChannel.send(f"\n{i.user.mention} created a ticket; {c.mention}.\n")
			e = await c.send(f"{i.user.mention}", embed=emb2)
			await e.edit(view=UnclaimedTicket(i.guild, e))
			await i.response.send_message(embed=emb, ephemeral=True)
		else:
			if self.manager in i.user.roles:
				log[str(i.guild.id)]["Open"]=True
				json.dump(log, open('log.json', 'w'))
				print("Ticket Queue Opened\n")
			else:
				emb=discord.Embed(title="Closed ⛔")
				b.disabled=True
				await i.response.send_message(embed=emb, ephemeral=True)

	@discord.ui.button(label="⌛ Close", custom_id="close_button", style=discord.ButtonStyle.gray)
	async def Close(self, i:discord.Interaction, b:discord.ui.Button):
		if log[str(i.guild.id)]["Open"]:
			if self.manager in i.user.roles:
				log[str(i.guild.id)]["Open"]=False
				json.dump(log, open('log.json', "w"), indent=4)
				print("Ticket Queue Closed\n")
		else:
			b.disabled=True

	@discord.ui.button(label="❌ Delete", custom_id="delete_button", style=discord.ButtonStyle.red)
	async def Delete(self, i:discord.Interaction, b:discord.ui.Button):
		if self.gm in i.user.roles:
			conf = discord.Embed(title="Delete Confirmation", description="Please confirm that you want to delete the queue.")
			e = await i.response.send_message(embed=conf)
			self.bot.add_view(DeleteConfirm(self.guild, e), message_id=e.id)
			print("Ticket Queue Deleted\n")
		else:
			b.disabled=True

class MainCog(commands.Cog):
	def __init__(self, bot):
		self.bot:commands.Bot = bot

	@commands.command(aliases=['a'])
	async def attention(self, ctx, r:discord.Role=None):
		role = r
		async with ctx.typing():
			mod=False
			if role == None:
				e = discord.Embed(description="No role inputed.")
				await ctx.reply(embed=e)
				return
			for r in ctx.author.roles:
				if r.id in log[str(ctx.guild.id)]["Mod"]:
					mod=True
			if mod:
				print(ctx.message)
				if role.position < ctx.author.top_role.position:
					for m in role.members:
						await ctx.reply(m.mention)
				else:
					e = discord.Embed(description="Must have a higher role.")
					await ctx.reply(embed=e)
			else:
				e = discord.Embed(description="Must be mod to use this command.")
				await ctx.reply(embed=e)

	@commands.command(aliases=['i'])
	async def invites(self, ctx):
		l = {}
		async with ctx.typing():
			for i in await ctx.guild.invites():
				if str(i.inviter) not in l:
					l[str(i.inviter)]=i.uses
				else:
					l[str(i.inviter)]=l[str(i.inviter)]+i.uses
			print(l)
			print(dir(ctx.guild.members[0]))

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def ticket(self, ctx):
		# add remove enable disable
		# React, response, imgonly, welcome, boost, jail, embed
		emb = discord.Embed(title="Open a support ticket.", description="Click the open button below to contact staff.")
		e = await ctx.send(embed=emb)
		await e.edit(view=Queue(self.bot, ctx.guild, ctx.channel, e))
		log[str(ctx.guild.id)]["View"][str(self.embed.id)]=["queue", int(self.channel.id), False]
		json.dump(log, open('log.json', "w"), indent=4)
		print("Ticket Queue Created\n")

	@ticket.error
	async def kick_error(self, ctx, error):
		if isinstance(error, MissingPermissions):
			text = f"{ctx.message.author}, you're missing {MissingPermissions} to do that."
			await ctx.send_message(text)

	@commands.command()
	async def vc(self, ctx, cmd, *, name:str=""):
		config=json.load(open("config.json"))
		if cmd.lower() == "rename":
			# Rename VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						if len(name) > 100:
							emb = discord.Embed(description="Name needs to be less than 100 characters. (WTF is wrong w you?)")
							await ctx.reply(embed=emb)
							return
						emb = discord.Embed(description=f"Renamed VC to **{name}**.")
						await ctx.author.voice.channel.edit(name=name)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't rename this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == "hide":
			# Hides VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						emb = discord.Embed(description="Your VC has been hidden.")
						overwrites = {
							ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
							ctx.author: discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True)}
						await ctx.author.voice.channel.set_permissions(overwrites=overwrites)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't rename this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == 'lock':
			# Lock VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						emb = discord.Embed(description="Your VC has been locked.")
						overwrites = {
							ctx.guild.default_role: discord.PermissionOverwrite(connect=False),
							ctx.author: discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True)}
						await ctx.author.voice.channel.edit(overwrites=overwrites)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't rename this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == 'unlock':
			# Unlock VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						emb = discord.Embed(description="Your VC has been unlocked.")
						overwrites = {
							ctx.guild.default_role: discord.PermissionOverwrite(connect=True),
							ctx.author: discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True)}
						await ctx.author.voice.channel.edit(overwrites=overwrites)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't rename this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == "unhide":
			# Unhides VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						emb = discord.Embed(description="Your VC has been unhidden.")
						overwrites = {
							ctx.guild.default_role: discord.PermissionOverwrite(view_channel=True),
							ctx.author: discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True)}
						await ctx.author.voice.channel.edit(overwrites=overwrites)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't rename this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == 'transfer':
			# Transfer VC ownership to user
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						u=await commands.MemberConverter().convert(ctx, name)
						if u == ctx.author:
							emb =discord.Embed(description="You're already the VC's owner.")
							await ctx.reply(embed=emb)
						if u.voice.channel != ctx.author.voice.channel:
							emb = discord.Embed(description="Member must be in the same VC for ownership to be transfered.")
							await ctx.reply(embed=emb)
							return
						emb = discord.Embed(description=f"{u} is now this VC's owner.")
						config[str(ctx.guild.id)]["vc"][str(ctx.author.voice.channel.id)]['owner']=u.id
						json.dump(config, open('config.json', 'w'))
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't transfer ownership of this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == 'block':
			# Block user from VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						u=await commands.MemberConverter().convert(ctx, name)
						emb = discord.Embed(description=f"{u} is now blocked from joining VC.")
						ow = discord.PermissionOverwrite(view_channel=False, connect=False, send_messages=False)
						await ctx.author.voice.channel.set_permissions(u, overwrite=ow)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't block members from this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == "allow":
			# Allow user into VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if ctx.author.id == config[str(ctx.guild.id)]['vc'][str(ctx.author.voice.channel.id)]['owner']:
						u=await commands.MemberConverter().convert(ctx, name)
						emb = discord.Embed(description=f"{u} is now allowed to join VC.")
						ow = discord.PermissionOverwrite(view_channel=True, connect=True, send_messages=True)
						await ctx.author.voice.channel.edit(overwrites=overwrites)
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="You're not the owner of this VC")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="Everyone is already allowed in this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

		if cmd.lower() == "claim":
			# Claim ownership of VC
			if ctx.author.voice:
				if str(ctx.author.voice.channel.id) in config[str(ctx.guild.id)]['vc']:
					if config[str(ctx.guild.id)]["vc"][str(ctx.author.voice.channel.id)]['owner'] == ctx.author.id:
						emb = discord.Embed(description="You're the owner of the VC.")
						await ctx.reply(embed=emb)
						return
					mids = []
					for m in ctx.author.voice.channel.members:
						mids.append(m.id)
					if config[str(ctx.guild.id)]["vc"][str(ctx.author.voice.channel.id)]['owner'] not in mids:
						emb = discord.Embed(description=f"You claimed {ctx.author.voice.channel}")
						config[str(ctx.guild.id)]["vc"][str(ctx.author.voice.channel.id)]['owner']=ctx.author.id
						json.dump(config, open('config.json', 'w'))
						await ctx.reply(embed=emb)
					else:
						emb = discord.Embed(description="The owner is still in VC.")
						await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description="You can't claim this VC.")
					await ctx.reply(embed=emb)
			else:
				emb = discord.Embed(description="You're not in a VC.")
				await ctx.reply(embed=emb)

	@commands.command()
	async def banner(self, ctx, m:discord.Member=None):
		pass

	@commands.command()
	async def afk(self, ctx, *, msg = None):
		async with ctx.typing():
			if msg==None:
				emb = discord.Embed(description=f"{ctx.author.mention}, your AFK status has been set.")
			else:
				emb = discord.Embed(description=f"{ctx.author.mention}, your AFK status has been set: {msg}")
			log[str(ctx.guild.id)]["AFK"][str(ctx.author.id)]=[ctx.author.nick, str(msg)]
			try:
				await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
			except:
				pass
		json.dump(log, open('log.json', 'w'), indent=4)
		print(f"{ctx.author} went afk: {msg}\n")
		await ctx.reply(embed=emb)

	@commands.command()
	async def role(self, ctx, m:discord.Member=None, r:discord.Role=None):
		async with ctx.typing():
			return
			if r>=ctx.author.top_role:
				emb = discord.Embed(description=f"Cannot give this role.")
				await ctx.reply(embed=emb)
				return
			elif r == None and m == None:
				emb = discord.Embed(description="Please select a role and a member.")
				await ctx.reply(embed=emb)
			elif r == None:
				emb = discord.Embed(description="Please select a role.")
				await ctx.reply(embed=emb)
			else:
				if r not in m.roles:
					emb = discord.Embed(description=f'{m} has been given {r}.')
					await m.add_roles(r)
					await ctx.reply(embed=emb)
				else:
					emb = discord.Embed(description=f'{r} has been taken {m}.')
					await m.remove_roles(r)
					await ctx.reply(embed=emb)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, m:discord.Member=None):
		async with ctx.typing():
			if m == None:
				emb = discord.Embed(description="Please select a member you would like to ban.")
				await ctx.reply(embed=emb)
			elif ctx.author.top_role <= m.top_role:
				emb = discord.Embed(description="Cannot ban someone with a higher role than you.")
				await ctx.reply(embed=emb)
				return
			else:
				emb = discord.Embed(description=f"Are you sure you want to ban {m}.")
				await ctx.reply(embed=emb, view=BanConfirm(m))

	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, m:discord.Member=None):
		async with ctx.typing():
			if m == None:
				emb = discord.Embed(description="Please select a member you would like to kick.")
				await ctx.reply(embed=emb)
			elif ctx.author.top_role <= m.top_role:
				emb = discord.Embed(description="Cannot kick someone with a higher role than you.")
				await ctx.reply(embed=emb)
				return
			else:
				emb = discord.Embed(description=f"Are you sure you want to kick {m}.")
				await ctx.reply(embed=emb, view=KickConfirm(m))

	@commands.command()
	async def ping(self, ctx):
		async with ctx.typing():
			config=json.load(open("config.json"))
			e = discord.Embed(description=f'Pong! {round(self.bot.latency * 1000)}ms.')
			await ctx.reply(embed=e)

	@commands.command()
	async def si(self, ctx, g: discord.Guild=None):
		if g==None:
			g=ctx.guild
		
		print(dir(g.members))
		# description
		# emojis
		# icon
		# members
		# owner
		# text_channels
		# voice_channels

	@commands.command()
	async def level(self, ctx, m: discord.Member=None):
		async with ctx.typing():
			if m == None:
				m = ctx.author
				config=json.load(open("config.json"))
				lvl = config[str(ctx.guild.id)]['level'][str(m.id)]['lvl']
				await ctx.reply(f"You're level {lvl}.")
			else:
				config=json.load(open("config.json"))
				lvl = config[str(ctx.guild.id)]['level'][str(m.id)]['lvl']
				await ctx.reply(f"{m} is level {lvl}.")

	@commands.command()
	async def banner(self, ctx, m: discord.Member=None):
		return
		async with ctx.typing():
			if m==None:
				m = ctx.author
			await ctx.send(m.banner)
			#bannURL=m.banner.url
			#await ctx.send(bannURL)
	
	@commands.command()
	async def detain(self, ctx, m: discord.Member=None, *, msg=None):
		async with ctx.typing():
			l = []
			roles=[]
			i=[]
			j=[]
			b = False
			mod = False
			detainee = discord.utils.get(ctx.guild.roles, id=log[str(ctx.guild.id)]["Detention"]["roleid"])

			for r in log[str(ctx.guild.id)]["Detention"]["Mod"]:
			# Mod role list
				knight = discord.utils.get(ctx.guild.roles, id=r)
				l.append(knight)
			
			for r in l:
				if r in ctx.author.roles:
					mod = True
			if mod:
			# Cross examination check for authorized roles
				if m == None:
				# No member mentioned
					e = discord.Embed(description="Please mention the member you would like to jail.")
					await ctx.reply(embed=e)
					return
				elif m.top_role >= ctx.author.top_role:
					e=discord.Embed(description=f"Can't jail someone with a higher role than yours.")
					await ctx.reply(embed=e)
					return
				else:
					for r in m.roles:
					# Detainee role list
						if r.name!='@everyone':
							if r.id != log[str(ctx.guild.id)]["Detention"]['roleid']:
								roles.append(r)
					for r in roles:
						try:
							await m.remove_roles(r)
							i.append(r.id)
						except:
							b=True
							print(f"Couldn't remove {r}")
							j.append(r)
					await m.add_roles(detainee)
					if b == False:
						e = discord.Embed(title=f"{m.name} has been detained.")
					else:
						e = discord.Embed(title="Detaining Error:")
						for r in j:
							e.add_field(name=f"{r.mention} role unremoveable.", value='', inline=False)
					for r in i:
						role = discord.utils.get(ctx.guild.roles, id=r)
						e.add_field(name=f"{role.name}", value='', inline=False)
					if str(m.id) in log[str(ctx.guild.id)]["Detention"]:
						log[str(ctx.guild.id)]["Detention"][str(m.id)]=[i]
					else:
						log[str(ctx.guild.id)]["Detention"][str(m.id)]=[i]
						#log[str(ctx.guild.id)]["Detention"][str(m.id)].append(i)
					await ctx.reply(embed=e)
					json.dump(log, open('log.json', 'w'), indent=4)
			else:
				e = discord.Embed(description=f"No unauthorized use")
				await ctx.reply(embed=e)

	@commands.command()
	async def detained(self, ctx):
		async with ctx.typing():
			e = discord.Embed(title="Detained:")
			for m in log[str(ctx.guild.id)]['Detention']:
				if m != "roleid":
					user = discord.utils.get(self.bot.get_all_members(), id=int(m))
					if user:
						e.add_field(name=f"{user} : {m}", value='', inline=False)
			await ctx.send(embed=e)

	@commands.command()
	async def release(self, ctx, m: discord.Member=None):
		async with ctx.typing():
			l = []
			mod = False
			detainee = discord.utils.get(ctx.guild.roles, id=log[str(ctx.guild.id)]["Detention"]["roleid"])

			for r in log[str(ctx.guild.id)]["Detention"]["Mod"]:
			# Mod role list
				knight = discord.utils.get(ctx.guild.roles, id=r)
				l.append(knight)
			
			for r in l:
				if r in ctx.author.roles:
					mod = True
			if mod:
				if m==None:
					e=discord.Embed(description="Please mention the member you would like to unjail.") 
				else:
					if str(m.id) in log[str(ctx.guild.id)]['Detention']:
						await m.remove_roles(discord.utils.get(ctx.guild.roles, id=log[str(ctx.guild.id)]['Detention']['roleid']))
						for role in log[str(ctx.guild.id)]['Detention'][str(m.id)][0]:
							r = discord.utils.get(ctx.guild.roles, id=role)
							await m.add_roles(r)
						e = discord.Embed(title=f"{m.name} has been unjailed.") 
						e.add_field(name="**added roles:**", value='', inline=False)
						for r in log[str(ctx.guild.id)]['Detention'][str(m.id)][0]:
							role = discord.utils.get(ctx.guild.roles, id=r)
							e.add_field(name=f"{role.name}", value='', inline=False)
						del log[str(ctx.guild.id)]['Detention'][str(m.id)]
						json.dump(log, open('log.json', 'w'))
						await ctx.reply(embed=e)
					else:
						e = discord.Embed(description=f"Member is not logged.")
						await ctx.reply(embed=e)
			else:
				e = discord.Embed(description=f"Only moderators can use this command")
				await ctx.reply(embed=e)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def purge(self, ctx, limit=0):
		if limit <= 0:
			m = await ctx.send("Enter the number of messages you want deleted.")
			time.sleep(5)
			await m.delete()
			return
		await ctx.channel.purge(limit=limit)
		m = await ctx.send(f'Cleared {limit} messages, {ctx.author.mention}.')
		time.sleep(5)
		await m.delete()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		guild = member.guild
		log = discord.utils.get(guild.channels, id=1272365731522150403)
		i=0
		c=0

		for memb in guild.members:
			if not memb.bot:
				i = i+1

		for p in log[str(guild.id)]["Welcome"]["pop"]:
			if i == log[str(guild.id)]["Welcome"]["pop"][p][0]:
				e=discord.Embed(title="Population Milestone", description=log[str(guild.id)]["Welcome"]["pop"][p][1])
				await log.send(embed=e)

		# Check detained
		if str(member.id) in log[str(member.guild.id)]["Detention"]:
			j = discord.utils.get(member.guild.roles, id=log[str(member.guild.id)]["Detention"]['roleid'])
			await member.add_roles(j)
			await log.send(f"""_ _
_ _ 
_ _               **{member.mention} member {i} has been detained!** <a:skull:1266173174345760778>
_ _                       
_ _""")
			return
		
		elif member.bot:
			b = discord.utils.get(member.guild.roles, id=1271767274830827540)
			await member.add_roles(b)
			return
		else:
			await log.send(f"""_ _
_ _ 
_ _                      **Welcome, {member.mention}!** <a:skull:1266173174345760778> *You are member {i}*
_ _                       
_ _""")
			return

	@commands.Cog.listener()
	async def on_member_remove(self, ctx):
		#config=json.load(open("config.json"))
		log = discord.utils.get(ctx.guild.channels, id=1272365731522150403)
		await log.send(f'<@{ctx.id}> left the server.')

	@commands.Cog.listener()
	async def on_voice_state_update(self, m: discord.Member, before: discord.voice_state, after: discord.voice_state):
		config=json.load(open("config.json"))
		j2c = discord.utils.get(m.guild.voice_channels, id=1281427995424329779)
		#log = discord.utils.get(m.guild.channels, id=1272365731522150403)
		if not before.channel:
			if m.bot:
				return
			print(f"{m} joined VC; {after.channel}.")
		if before.channel and after.channel:
			if before.channel.id != after.channel.id:
				if len(before.channel.members) == 0:
					if str(before.channel.id) in config[str(m.guild.id)]["vc"]:
						print(f"{m} left VC.")
						del config[str(m.guild.id)]["vc"][str(before.channel.id)]
						json.dump(config, open('config.json', 'w'))
						await before.channel.delete()
						print(f'Deleted {before.channel}.')
				if m.bot:
					return
				print(f'{m} moved from {before.channel} to {after.channel}.')
		if before.channel and not after.channel:
			if len(before.channel.members) == 0:
				if str(before.channel.id) in config[str(m.guild.id)]["vc"]:
					print(f"{m} left VC.")
					del config[str(m.guild.id)]["vc"][str(before.channel.id)]
					json.dump(config, open('config.json', 'w'))
					await before.channel.delete()
					print(f'Deleted {before.channel}.')
			if m.bot:
				return
		if after.channel == j2c:
			if m.bot:
				return
			cat = discord.utils.get(m.guild.categories, id=1264022712641130530)
			vc = await m.guild.create_voice_channel(name=f"{m}'s VC", category=cat)
			config[str(m.guild.id)]["vc"][str(vc.id)]={"owner":m.id}
			json.dump(config, open('config.json', 'w'))
			print(f'{m} created a VC.')
			await m.move_to(vc)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		#boost = discord.utils.get(before.guild.roles, id=log[str(before.guild.id)][])
		detained = discord.utils.get(before.guild.roles, id=log[str(before.guild.id)]["Detention"]["roleid"])
		try:
			if detained in before.roles:
				for r in after.roles:
					if r not in before.roles:
						await before.remove_roles(r)
						print("Removed role from detainee.")
			#elif str(before.guild.id) in log['boost']:
				return
				bank = discord.utils.get(before.guild.channels, id=log['boost'][str(before.guild.id)]['info']['cid'])
				if boost in after.roles:
					if not boost in before.roles:
						print(f"\n{before.guild.name} boosted by {before.name}\n")
						e = discord.Embed(description=f"**Thank you for boosting**\n*+1 level* <a:779062751346819083:1263582193796780185>\n.\t.\t.\n[click here to claim your perks](https://discord.com/channels/1264022712641130527/1321126755766894664)")
						await bank.send(f"{before.mention}", embed=e)
		except:
			print("Boost exception")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, ctx):
		config=json.load(open("config.json"))
		if str(ctx.member.id) in config[str(ctx.member.guild.id)]['jail']['jailed']:
			return
		if ctx.message_id == 1321244285017919542:
			v = discord.utils.get(ctx.member.guild.roles, id=1272242814520000646)
			await ctx.member.add_roles(v)
			print(f'{ctx.member} has been verified.')

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, ctx):
		if ctx.message_id == 1321244285017919542:
			g =  self.bot.get_guild(ctx.guild_id)
			v = discord.utils.get(g.roles, id=1272242814520000646)
			m = g.get_member(ctx.user_id)
			await m.remove_roles(v)
			print(f'{m} has been unverified.')

	@commands.Cog.listener()
	async def on_message(self, ctx):
		if ctx.author==self.bot.user:
			return
		
		u = ctx.author
		m = ctx.content
		c = ctx.channel
		g = ctx.guild

		print(f"\n{g} : {c} : {u} : {m}\n")

		# Level system
#		await update_data(g, u)
#		await add_exp(g, u, 5)
#		await lvl_up(g, u)
		
		# AFK system
		if str(u.id) in log[str(ctx.guild.id)]["AFK"]:
			if ",afk" in m.lower():
				return
			else:
				emb = discord.Embed(title="Welcome Back!", description="Your AFK status has been removed.")
				try:
					await ctx.author.edit(nick=log[str(ctx.guild.id)]["AFK"][str(u.id)][0])
				except:
					pass
				del log[str(ctx.guild.id)]["AFK"][str(u.id)]
				json.dump(log, open('log.json', 'w'), indent=4)
				await ctx.reply(embed=emb)

		for key, value in log[str(ctx.guild.id)]["AFK"].items():
			try:
				if f"<@{int(key)}>" in m:
					emb = discord.Embed(title='AFK Message', description=f' <@{int(key)}>: {log[str(ctx.guild.id)]["AFK"][key][1]}')
					await ctx.reply(embed=emb)
			except:
				pass

		# Auto image reaction & Image only 
		if c.id in log[str(ctx.guild.id)]["Media"]:
			if not ctx.attachments:
				await ctx.delete()
			else:
				# React & send message
				# await ctx.add_reaction(r)
				pass

		# Auto text react
		try:
			for msg in log[str(ctx.guild.id)]["Autoreact"]:
				if msg in m.lower():
					for r in log[str(ctx.guild.id)]["Autoreact"][msg]:
						await ctx.add_reaction(r)
		except:
			print("Text reaction exception")			

		# Auto text response
		try:
			for msg in log[str(ctx.guild.id)]["Autoresponse"]:
				if msg in m.lower():
					await ctx.channel.send(log[str(ctx.guild.id)]["Autoresponse"][str(msg)])
		except:
			print("Text response exception")	

async def setup(bot):
	await bot.add_cog(MainCog(bot))
	
