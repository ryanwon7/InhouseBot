import os
import discord
import time
import random
import unicodedata
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import ChannelType

# TO DOs 
# - add check to only let author/op use the !inhouse command after starting it (done)
# - add rematch feature (done)
# - add team create feature
# - add exit from current command feature (done)
intents = discord.Intents(messages=True, reactions=True, members=True)

if 'DYNO' in os.environ:
	TOKEN = os.environ['DISCORD_TOKEN']
	DATABASE = os.environ['MONGO_CONN_URL']
else:
	load_dotenv()
	TOKEN = os.getenv('DISCORD_TOKEN')
	DATABASE = os.getenv('MONGO_CONN_URL')


cluster = MongoClient(DATABASE)

timeout = 2400 #seconds
db = cluster["channel-usage"]
channel_usage = db["channel-usage"]
past_teams = db["past-teams"]

bot = commands.Bot(command_prefix='!')

def check_exist(server_id):
	idquery = {"_id": server_id}
	if channel_usage.find(idquery).count():
		return True
	else:
		return False


def channels_exist(ctx, vc_list):
	for i in range(0,3):
		for channel in ctx.guild.voice_channels:
			if vc_list[i] == channel.name:
				vc_list[i] = None
				continue
	if vc_list[0] == None and vc_list[1] == None and vc_list[2] == None:
		return 1
	else:
		return 0

def swap_list(member_list):
	l = len(member_list)&~1
	member_list[1:l:2],member_list[:l:2] = member_list[:l:2],member_list[1:l:2]

def randomizer(mem_names):
	random.shuffle(mem_names)
	mem_str1 = "\n**Team 1:** "
	mem_str2 = "\n**Team 2:** "
	count = 1
	for member in mem_names:
		if count % 2 == 0:
			if count == 2:
				mem_str1 += member
			else:
				mem_str1 += ", " + member
		else:
			if count == 1:
				mem_str2 += member
			else:
				mem_str2 += ", " + member
		count+=1
	response = 'Here are randomized teams. To accept, react with :ok:. To re randomize, react with :arrows_counterclockwise:. To exit, react with :x:.\n'
	return (response + mem_str1 + mem_str2)


def remove_players_str(ctx, members, mem_add):
	count = 1
	mem_str = ""
	for member in members:
		if member.nick != None:
			mem_str += str(count) + "  " + member.nick + '\t '
		else:
			mem_str += str(count) + "  " + member.name + '\t '
		count+=1
	for member in mem_add:
		mem_str += str(count) + "  " + member + '\t '
		count+=1

	response = 'Please select which of the following members should be removed from the game by their numbers. For example, to remove players 4, 8, and 12 from the inhouse game, reply with *4 8 12* \n\n'
	return response + mem_str


@bot.command(name='inhouse', help='Starts an inhouse game with members in current channel. Default number of players is 10.')
async def inhouse_start(ctx, players: int=10):
	if not check_exist(ctx.guild.id):
		await ctx.send("Please run the !setchannel command first to confingure the channels for your server.")
		return

	members = ctx.message.author.voice.channel.members
	orig = ctx.message.author
	mem_add = []
	timeout_start = time.time()
	complete = False

	if (len(members) == 0):
		await ctx.send("You must be in a voice channel to run this command.")
		return

	def check(msg):
		if msg.author.id == orig.id:
			return True
		if msg.author.guild_permissions.administrator:
			return True
		return False

	def checkr(reaction, user):
		if user.id == orig.id:
			return True
		if user.guild_permissions.administrator:
			return True
		return False

	while time.time() < timeout_start + timeout:
		resp = f'There are {len(members)+len(mem_add)} selected for the inhouse. If you would like to add more players, react with plus sign. If you would like to remove players, react with the minus sign. If you would like to continue, react with :ok:. To quit, react with the :x:.'
		msg_orig = await ctx.send(resp)
		reactions = ['\U00002795', '\U00002796', '\U0001f197', '\U0000274c']
		for reaction in reactions:
			await msg_orig.add_reaction(emoji=reaction)
		await asyncio.sleep(0.5)
		reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 600)
		reac_name = unicodedata.name(reaction.emoji)
		if reac_name == 'HEAVY MINUS SIGN':
			await msg_orig.delete()
			resp = remove_players_str(ctx, members, mem_add)
			msg1 = await ctx.send(resp)
			msg = await bot.wait_for('message', check=check, timeout=600)
			resp_list = list(map(int, msg.content.split()))
			resp_list.sort(reverse=True)
			for idx in resp_list:
				if idx <= len(members):
					del members[idx-1]
				else:
					del mem_add[idx-len(members)-1]
			await msg.delete()
			await msg1.delete()
		elif reac_name == 'HEAVY PLUS SIGN':
			await msg_orig.delete()
			resp = "Please list the names of the players you would like to add. Since they are currently not connected to a voice channel, they will not be able to be moved to their team channel. For example, to add Elijah p and rwon, reply with *Elijah p, rwon*\n"
			msg1 = await ctx.send(resp)
			msg = await bot.wait_for('message', check=check, timeout=600)
			for user in msg.content.split(","):
				mem_add.append(user.strip())
			await msg.delete()
			await msg1.delete()
		elif reac_name == 'SQUARED OK':
			complete = True
			await msg_orig.delete()
			break
		elif reac_name == 'CROSS MARK':
			complete = False
			await msg_orig.delete()
			break

	if complete:
		mem_names = []
		for member in members:
			if member.nick:
				mem_names.append(member.nick)
			else:
				mem_names.append(member.name)
		mem_names.extend(mem_add)
		timeout_start = time.time()
		while time.time() < timeout_start + timeout:
			resp = randomizer(mem_names)
			msg_orig = await ctx.send(resp)
			reactions = ['\U0001f197', '\U0001f504', '\U0000274c']
			for reaction in reactions:
				await msg_orig.add_reaction(reaction)
			await asyncio.sleep(0.5)
			reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 600.0)
			reac_name = unicodedata.name(reaction.emoji)
			if reac_name == 'SQUARED OK':
				exit = False
				break
			elif reac_name == 'ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS':
				await msg_orig.delete()
				continue
			elif reac_name == 'CROSS MARK':
				await msg_orig.delete()
				exit = True
				break

		if not exit:
			msg2 = await ctx.send('Teams confirmed! React with :ok: to move players to each channel.')
			await msg2.add_reaction(emoji='\U0001f197')
			await asyncio.sleep(0.5)

			reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 1200.0)

			data = channel_usage.find_one({"_id": ctx.guild.id})
			team1ch = discord.utils.get(ctx.guild.channels, id=data["team1"])
			team2ch = discord.utils.get(ctx.guild.channels, id=data["team2"])

			team1 = mem_names[0::2]
			team2 = mem_names[1::2]

			team1_ids = []
			team2_ids = []
			for member in members:
				if member.name in team1 or member.nick in team1:
					team1_ids.append(member.id)
					await member.move_to(team1ch)
				elif member.name in team2 or member.nick in team2:
					team2_ids.append(member.id)
					await member.move_to(team2ch)

			await msg2.delete()
			await ctx.send('Players sent to each team channel! Good luck and have fun!')

			idquery = {"_id": ctx.guild.id}
			if past_teams.find(idquery).count():
				past_teams.remove(idquery)

			post = {"_id": ctx.guild.id, "mem_names": mem_names, "team1_id": team1_ids, "team2_id": team2_ids}

			past_teams.insert_one(post)

@bot.command(name='rematch', help='Sets up a rematch between the last two generated teams.')
async def rematch(ctx):
	if not check_exist(ctx.guild.id):
		await ctx.send("Please run the !setchannel command first to confingure the channels for your server.")
		return

	orig = ctx.message.author
	def checkr(reaction, user):
		if user.id == orig.id:
			return True
		if user.guild_permissions.administrator:
			return True
		return False

	idquery = {"_id": ctx.guild.id}
	if past_teams.find(idquery).count():
		data = past_teams.find_one(idquery)
		mem_names = data["mem_names"]
		team1_ids = data["team1_id"]
		team2_ids = data["team2_id"]

		data1 = channel_usage.find_one({"_id": ctx.guild.id})
		team1ch = discord.utils.get(ctx.guild.channels, id=data1["team1"])
		team2ch = discord.utils.get(ctx.guild.channels, id=data1["team2"])
		
		timeout_start = time.time()
		swap = False
		while time.time() < timeout_start + timeout:
			mem_str1 = "\n**Team 1:** "
			mem_str2 = "\n**Team 2:** "
			count = 1
			for member in mem_names:
				if count % 2 == 0:
					if count == 2:
						mem_str2 += member
					else:
						mem_str2 += ", " + member
				else:
					if count == 1:
						mem_str1 += member
					else:
						mem_str1 += ", " + member
				count+=1
			response = 'Here are the rematch teams. To confirm the teams, react with :ok:. To switch sides, react with :left_right_arrow:. To quit, react with :x:.\n'
			
			msg_orig = await ctx.send(response + mem_str1 + mem_str2)
			reactions = ['\U0001f197', '\U00002194', '\U0000274c']
			for reaction in reactions:
				await msg_orig.add_reaction(reaction)
			await asyncio.sleep(0.5)
			reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 600.0)
			reac_name = unicodedata.name(reaction.emoji)
			if reac_name == 'SQUARED OK':
				exit = False
				break
			elif reac_name == 'LEFT RIGHT ARROW':
				swap_list(mem_names)
				swap = not swap
				await msg_orig.delete()
				continue
			elif reac_name == 'CROSS MARK':
				await msg_orig.delete()
				exit = True
				break

		if not exit:
			msg2 = await ctx.send('Teams confirmed! React with :ok: to move players to each channel.')
			await msg2.add_reaction(emoji='\U0001f197')
			await asyncio.sleep(0.5)

			reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 1200.0)

			for mem_id in team1_ids:
				if swap:
					await ctx.guild.get_member(mem_id).move_to(team2ch)
				else:
					await ctx.guild.get_member(mem_id).move_to(team1ch)
			for mem_id in team2_ids:
				if swap:
					await ctx.guild.get_member(mem_id).move_to(team1ch)
				else:
					await ctx.guild.get_member(mem_id).move_to(team2ch)

			await msg2.delete()
			await ctx.send('Players sent to each team channel! Good luck and have fun!')	
	else:
		await ctx.send("No games have been played using the InHouse Bot yet.")


@bot.command(name='endgame', help='Move people back to the lobby channel.')
async def end_game(ctx):
	if not check_exist(ctx.guild.id):
		await ctx.send("Please run the !setchannel command first to confingure the channels for your server.")
		return

	data = channel_usage.find_one({"_id": ctx.guild.id})
	lobbych = discord.utils.get(ctx.guild.channels, id=data["lobby"])
	team1ch = discord.utils.get(ctx.guild.channels, id=data["team1"])
	team2ch = discord.utils.get(ctx.guild.channels, id=data["team2"])
	for member in team1ch.members:
		await member.move_to(lobbych)
	for member in team2ch.members:
		await member.move_to(lobbych)

@bot.command(name='setchannel', help='Set the default voice channels for the lobby and team channels.')
async def set_channels(ctx):
	orig = ctx.message.author
	def checkr(reaction, user):
		if user.id == orig.id:
			return True
		if user.guild_permissions.administrator:
			return True
		return False

	timeout_start = time.time()
	l = list((c.name for c in ctx.guild.channels if c.type==ChannelType.voice))
	ch_list = [l[i:i + 10] for i in range(0, len(l), 10)] 
	reactions = ['\u0031\ufe0f\u20e3', '\u0032\ufe0f\u20e3', '\u0033\ufe0f\u20e3', '\u0034\ufe0f\u20e3', '\u0035\ufe0f\u20e3', '\u0036\ufe0f\u20e3', '\u0037\ufe0f\u20e3', '\u0038\ufe0f\u20e3', '\u0039\ufe0f\u20e3', '\U0001f51f']
	selected = []

	for i in range(1,4):
		index = 0
		if i == 1 :
			msg1_pre = await ctx.send("Please select the number of the voice channel you would like to set as your lobby. This is where players will be returned to after games are ended. To view more channels if there are multiple pages, click :track_next:. To go back, click :track_previous:.")
		if i == 2:
			msg1_pre = await ctx.send("Now, please select the number of the voice channel you would like to set as your team 1 channel. This is where players in team 1 will be placed during games. To view more channels if there are multiple pages, click :track_next:. To go back, click :track_previous:.")
		if i == 3:
			msg1_pre = await ctx.send("Finally, please select the number of the voice channel you would like to set as your team 2 channel. This is where players in team 2 will be placed during games. To view more channels if there are multiple pages, click :track_next:. To go back, click :track_previous:.")
		while time.time() < timeout_start + timeout:
			curr_list = ch_list[index]

			empt = "\n"
			for idx, ch in enumerate(curr_list):
				empt += str(idx+1) + ') ' + ch + '\n'

			msg1 = await ctx.send(empt)
			
			for reaction in reactions[0:len(curr_list)]:
				await msg1.add_reaction(reaction)
			if index != 0:
				await msg1.add_reaction('\U000023ee')
			if index < len(ch_list) - 1:
				await msg1.add_reaction('\U000023ed')
			await asyncio.sleep(1.0)

			reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 600.0)

			try:
				reac_name = unicodedata.name(reaction.emoji)
				if reac_name == "BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR":
					await msg1.delete()
					index += 1
					continue
				elif reac_name == "BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR":
					await msg1.delete()
					index -= 1
					continue
			except:
				chosen = reactions.index(reaction.emoji)
				await msg1.delete()
				await msg1_pre.delete()
				selected.append(curr_list[chosen])
				break

	idquery = {"_id": ctx.guild.id}
	if channel_usage.find(idquery).count():
		newvalues = { "$set": {"lobby": discord.utils.get(ctx.guild.channels, name=selected[0]).id, "team1": discord.utils.get(ctx.guild.channels, name=selected[1]).id, "team2": discord.utils.get(ctx.guild.channels, name=selected[2]).id}}
		channel_usage.update_one(idquery, newvalues)
		await ctx.send("The Lobby Voice Channel is now set to " + selected[0] + ". The Team 1 Voice Channel is now set to " + selected[1] + ". The Team 2 Voice Channel is now set to " + selected[2] + "." + "\nChannels were set previously. Updating existing records.")
	else:
		post = {"_id": ctx.guild.id, "lobby": discord.utils.get(ctx.guild.channels, name=selected[0]).id, "team1": discord.utils.get(ctx.guild.channels, name=selected[1]).id, "team2": discord.utils.get(ctx.guild.channels, name=selected[2]).id}
		channel_usage.insert_one(post)
		await ctx.send("The Lobby Voice Channel is now set to " + selected[0] + ". The Team 1 Voice Channel is now set to " + selected[1] + ". The Team 2 Voice Channel is now set to " + selected[2] + "." + "\nCreating default channels for your server.")

@bot.command(name='valmap', help='Pick a random map for Valorant.')
async def valorant_map(ctx):
	orig = ctx.message.author
	def checkr(reaction, user):
		if user.id == orig.id:
			return True
		if user.guild_permissions.administrator:
			return True
		return False

	maps = ["Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Split"]

	timeout_start = time.time()
	timing = 600
	while time.time() < timeout_start + timeout:
		mapnum = random.randint(0, 6)
		msg_orig = await ctx.send("Selected Map: " + maps[mapnum])

		reactions = ['\U0001f197', '\U0001f504']
		for reaction in reactions:
			await msg_orig.add_reaction(reaction)
		await asyncio.sleep(0.5)
		reaction, user = await bot.wait_for('reaction_add', check=checkr, timeout = 500.0)
		reac_name = unicodedata.name(reaction.emoji)
		if reac_name == 'SQUARED OK':
			break
		elif reac_name == 'ANTICLOCKWISE DOWNWARDS AND UPWARDS OPEN CIRCLE ARROWS':
			await msg_orig.delete()
			continue

bot.run(TOKEN)

#@setchannel.error
#async def setchannel_error(self, error, ctx):
#	if isinstance(error, commands.MissingPermissions):
#		await ctx.send(":redTick: You don't have permission to run this command. Please give all the necessary permissions to the bot when adding it to the server.")
#
#@inhouse.error
#async def inhouse_error(self, error, ctx):
#	if isinstance(error, commands.MissingPermissions):
#		await ctx.send(":redTick: You don't have permission to run this command. Please give all the necessary permissions to the bot when adding it to the server.")
#
#@endgame.error
#async def endgame_error(self, error, ctx):
#	if isinstance(error, commands.MissingPermissions):
#		await ctx.send(":redTick: You don't have permission to run this command. Please give all the necessary permissions to the bot when adding it to the server.")
#@rematch.error
#async def rematch_error(self, error, ctx):
#	if isinstance(error, commands.MissingPermissions):
#		await ctx.send(":redTick: You don't have permission to run this command. Please give all the necessary permissions to the bot when adding it to the server.")