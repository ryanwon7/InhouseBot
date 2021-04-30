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

# TO DOs - add check to only let author/op use the !inhouse command after starting it
# - add rematch feature
# - add team create feature
# - add exit from current command feature


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


def check(author):
	def inner_check(message):
		return message.author == author


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


def randomizer(mem_names):
	random.shuffle(mem_names)
	mem_str1 = "\n**Team 1**: "
	mem_str2 = "\n**Team 2**: "
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

	response = 'Please select which of the following members should be removed from the game by their numbers. For example, to remove players 4, 8, and 12 from the inhouse game, reply with \'4 8 12\' (without apostrophes).\n\n'
	return response + mem_str


@bot.command(name='inhouse', help='Starts an inhouse game with members in current channel. Default number of players is 10.')
async def inhouse_start(ctx, players: int=10):
	members = ctx.message.author.voice.channel.members
	mem_add = []
	timeout_start = time.time()
	complete = False

	while time.time() < timeout_start + timeout:
		resp = f'There are {len(members)+len(mem_add)} selected for the inhouse. If you would like to add more players, react with plus sign. If you would like to remove players, react with the minus sign. If you would like to continue, react with :ok:. To quit, react with the :x:.'
		msg_orig = await ctx.send(resp)
		reactions = ['\U00002795', '\U00002796', '\U0001f197', '\U0000274c']
		for reaction in reactions:
			await msg_orig.add_reaction(emoji=reaction)
		await asyncio.sleep(0.5)
		reaction, user = await bot.wait_for('reaction_add', timeout = 600)
		reac_name = unicodedata.name(reaction.emoji)
		if reac_name == 'HEAVY MINUS SIGN':
			await msg_orig.delete()
			resp = remove_players_str(ctx, members, mem_add)
			msg1 = await ctx.send(resp)
			msg = await bot.wait_for('message', check=check(ctx.message.author), timeout=600)
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
			resp = "Please list the names of the players you would like to add. Since they are currently not connected to a voice channel, they will not be able to be moved to their team channel. For example, to add rwon and Elijah p, reply with \'rwon \"Elijah p\"\' (without apostrophes)\n"
			msg1 = await ctx.send(resp)
			msg = await bot.wait_for('message', check=check(ctx.message.author), timeout=600)
			for user in msg.content.split():
				mem_add.append(user)
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
			reaction, user = await bot.wait_for('reaction_add', timeout = 600.0)
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

			reaction, user = await bot.wait_for('reaction_add', timeout = 1200.0)

			data = channel_usage.find_one({"_id": ctx.guild.id})
			team1ch = discord.utils.get(ctx.guild.channels, name=data["team1"])
			team2ch = discord.utils.get(ctx.guild.channels, name=data["team2"])

			team1 = mem_names[0::2]
			team2 = mem_names[1::2]
			for member in members:
				if member.name in team1 or member.nick in team1:
					await member.move_to(team1ch)
				elif member.name in team2 or member.nick in team2:
					await member.move_to(team2ch)

			await msg2.delete()
			await ctx.send('Players sent to each team channel! Good luck and have fun!')


@bot.command(name='endgame', help='Move people back to the lobby channel.')
async def end_game(ctx):
	data = channel_usage.find_one({"_id": ctx.guild.id})
	lobbych = discord.utils.get(ctx.guild.channels, name=data["lobby"])
	team1ch = discord.utils.get(ctx.guild.channels, name=data["team1"])
	team2ch = discord.utils.get(ctx.guild.channels, name=data["team2"])
	for member in team1ch.members:
		await member.move_to(lobbych)
	for member in team2ch.members:
		await member.move_to(lobbych)


@bot.command(name='setchannel', help='Set the default voice channels for the lobby and team channels.')
async def set_channels(ctx, lobby: str, team1: str, team2: str):
	if channels_exist(ctx, [lobby, team1, team2]):
		idquery = {"_id": ctx.guild.id}
		if channel_usage.find(idquery).count():
			newvalues = { "$set": {"lobby": lobby, "team1": team1, "team2": team2}}
			channel_usage.update_one(idquery, newvalues)
			await ctx.send("Channels were set previously. Updating existing records.")
		else:
			post = {"_id": ctx.guild.id, "lobby": lobby, "team1": team1, "team2": team2}
			channel_usage.insert_one(post)
			await ctx.send("Creating default channels for your server.")
	else:
		await ctx.send("Invalid channel names provided.")

bot.run(TOKEN)
