import os
import discord
import time
import random
import asyncio
from dotenv import load_dotenv
#import pymongo
#from pymongo import MongoClient

## INTENTS
intents = discord.Intents.default()
intents.members = True # Privileged Intent

games = [
	discord.commands.OptionChoice(name="valorant", value="valorant"),
	discord.commands.OptionChoice(name="league", value="league")]

valorant_maps = ['Ascent', 'Bind', 'Breeze', 'Fracture', 'Haven', 'Icebox', 'Pearl', 'Split']

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot(intents=intents)

def map_picker():
	maps = len(valorant_maps)
	map_index = random.randrange(maps)
	new_map = valorant_maps[map_index]
	return '\n**Selected Map**: ' + new_map + '\n'

def randomizer(mem_names, gamemode):
	random.shuffle(mem_names)
	if (gamemode  == 1):
		mem_str1 = "\n**Blue Side:** "
		mem_str2 = "\n**Red Side:** "
	elif (gamemode == 2):
		mem_str1 = "\n**Attackers:** "
		mem_str2 = "\n**Defenders:** "
	else:
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
	if gamemode == 2:
		response = 'Here are randomized teams. To accept, click Continue. To randomize teams again, click Reroll Teams. To change the selected map, click Reroll Map. To quit, click Quit.\n'
		return (response + mem_str1 + mem_str2)
	else:
		response = 'Here are randomized teams. To accept, click Continue. To randomize teams again, click Reroll Teams. To quit, click Quit.\n'
		return (response + mem_str1 + mem_str2)

class GameEndButtons(discord.ui.View):
	def __init__(self, caller, lobby, cat, text, v1, v2, timeout):
		self.caller = caller
		self.lobby = lobby
		self.cat = cat
		self.text = text
		self.v1 = v1
		self.v2 = v2
		super().__init__(timeout = timeout)
		
	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for member in self.v1.members:
			await member.move_to(self.lobby)
		for member in self.v2.members:
			await member.move_to(self.lobby)

		await self.text.delete()
		await self.v1.delete()
		await self.v2.delete()
		await self.cat.delete()

		button.disabled = True # set button.disabled to True to disable the button
		button.label = "Game Completed" # change the button's label to something else
		await self.message.edit(content="GG! Game has been completed.", view=self) # Go to next part

	@discord.ui.button(label="End Game", style=discord.ButtonStyle.danger)
	async def add_button_callback(self, button, interaction):
		for member in self.v1.members:
			await member.move_to(self.lobby)
		for member in self.v2.members:
			await member.move_to(self.lobby)

		await self.text.delete()
		await self.v1.delete()
		await self.v2.delete()
		await self.cat.delete()

		button.disabled = True # set button.disabled to True to disable the button
		button.label = "Game Completed" # change the button's label to something else
		await interaction.response.edit_message(content="GG! Game has been completed.", view=self) # edit the message's view

class LoadingButtonsVal(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, resp, map_resp, lobby, timeout):
		self.caller = caller
		self.members = members
		self.mem_names = mem_names
		self.gamemode = gamemode
		self.resp_string = resp
		self.map = map_resp
		self.lobby = lobby
		super().__init__(timeout = timeout)
		
	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	@discord.ui.button(label="Start Game", style=discord.ButtonStyle.success)
	async def continue_button_callback(self, button, interaction):
		guild = interaction.guild
		category = await guild.create_category("Inhouse Game Lobby")
		textchat = await guild.create_text_channel("inhouse-chat", category=category)
		team1ch = await guild.create_voice_channel("Team 1", category=category)
		team2ch = await guild.create_voice_channel("Team 2", category=category)

		team1 = self.mem_names[0::2]
		team2 = self.mem_names[1::2]
		for member in self.members:
			if member == 0:
				continue
			if member.name in team1 or member.nick in team1:
				await member.move_to(team1ch)
			elif member.name in team2 or member.nick in team2:
				await member.move_to(team2ch)
		await interaction.response.edit_message(content="The game has been started and each team has moved to their own discord channel! To end the game and return everyone to the original chat, click **End Game**.", view=GameEndButtons(self.caller, self.lobby, category, textchat, team1ch, team2ch, timeout=10800)) # Go to next part

	@discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
	async def reroll_teams_callback(self, button, interaction):
		await interaction.response.edit_message(content = self.resp_string + self.map, view=GameCreateButtonsVal(self.caller, self.members, self.mem_names, self.gamemode, self.resp_string, self.map, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary)
	async def quit_button_callback(self, button, interaction):
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(content="GG!", view=self)

class LoadingButtons(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, resp, lobby, timeout):
		self.caller = caller
		self.members = members
		self.mem_names = mem_names
		self.gamemode = gamemode
		self.resp_string = resp
		self.lobby = lobby
		super().__init__(timeout = timeout)
		
	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	@discord.ui.button(label="Start Game", style=discord.ButtonStyle.success)
	async def continue_button_callback(self, button, interaction):
		guild = interaction.guild
		try:
			category = await guild.create_category("Inhouse Game Lobby")
			textchat = await guild.create_text_channel("inhouse-chat", category=category)
			if self.gamemode == 1:
				team1ch = await guild.create_voice_channel("Blue Side", category=category)
				team2ch = await guild.create_voice_channel("Red Side", category=category)
			else:
				team1ch = await guild.create_voice_channel("Team 1", category=category)
				team2ch = await guild.create_voice_channel("Team 2", category=category)
		except:
			for child in self.children:
				child.disabled = True
			await interaction.response.edit_message(content="The Bot needs the Manage Channel Permission. Please reinvite the bot and ensure it receives the proper permissions.", view=self)
			return

		team1 = self.mem_names[0::2]
		team2 = self.mem_names[1::2]
		for member in self.members:
			if member == 0:
				continue
			if member.name in team1 or member.nick in team1:
				try:
					await member.move_to(team1ch)
				except:
					continue
			elif member.name in team2 or member.nick in team2:
				try:		
					await member.move_to(team2ch)
				except:
					continue
		await interaction.response.edit_message(content="The game has been started and each team has moved to their own discord channel! To end the game and return everyone to the original chat, click **End Game**.", view=GameEndButtons(self.caller, self.lobby, category, textchat, team1ch, team2ch, timeout=10800)) # Go to next part

	@discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
	async def reroll_teams_callback(self, button, interaction):
		await interaction.response.edit_message(content = self.resp_string, view=GameCreateButtons(self.caller, self.members, self.mem_names, self.gamemode, self.resp_string, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary)
	async def quit_button_callback(self, button, interaction):
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(content="GG!", view=self)

class GameCreateButtonsVal(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, resp, map_resp, lobby, timeout):
		self.caller = caller
		self.members = members
		self.mem_names = mem_names
		self.gamemode = gamemode
		self.resp_string = resp
		self.map = map_resp
		self.lobby = lobby
		super().__init__(timeout = timeout)
		
	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	@discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
	async def continue_button_callback(self, button, interaction):
		await interaction.response.edit_message(content="To start the game and move everyone to their channels, click **Start Game**. To go back and edit settings, click **Previous**. To exit, click **Quit**.", view=LoadingButtonsVal(self.caller, self.members, self.mem_names, self.gamemode, self.resp_string, self.map, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Reroll Teams", style=discord.ButtonStyle.primary)
	async def reroll_teams_callback(self, button, interaction):
		new_teams = randomizer(self.mem_names, self.gamemode)
		await interaction.response.edit_message(content = new_teams + self.map, view=GameCreateButtonsVal(self.caller, self.members, self.mem_names, self.gamemode, new_teams, self.map, self.lobby, timeout=3600)) # Go to next part


	@discord.ui.button(label="Reroll Map", style=discord.ButtonStyle.danger,)
	async def reroll_map_callback(self, button, interaction):
		map_resp = map_picker()
		await interaction.response.edit_message(content = self.resp_string + map_resp, view=GameCreateButtonsVal(self.caller, self.members, self.mem_names, self.gamemode, self.resp_string, map_resp, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary)
	async def quit_button_callback(self, button, interaction):
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(content="GG!", view=self)

class GameCreateButtons(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, resp, lobby, timeout):
		self.caller = caller
		self.members = members
		self.mem_names = mem_names
		self.gamemode = gamemode
		self.resp_string = resp
		self.lobby = lobby
		super().__init__(timeout = timeout)
		
	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	@discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
	async def continue_button_callback(self, button, interaction):
		await interaction.response.edit_message(content="To start the game and move everyone to their channels, click **Start Game**. To go back and edit settings, click **Previous**. To exit, click **Quit**.", view=LoadingButtons(self.caller, self.members, self.mem_names, self.gamemode, self.resp_string, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Reroll Teams", style=discord.ButtonStyle.primary)
	async def reroll_teams_callback(self, button, interaction):
		new_teams = randomizer(self.mem_names, self.gamemode)
		await interaction.response.edit_message(content = new_teams, view=GameCreateButtons(self.caller, self.members, self.mem_names, self.gamemode, new_teams, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary)
	async def quit_button_callback(self, button, interaction):
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(content="GG!", view=self)

class AddPlayerModal(discord.ui.Modal):
	def __init__(self, members, mem_names, caller, gamemode, lobby, *args, **kwargs) -> None:
		self.members = members
		self.mem_names = mem_names
		self.caller = caller
		self.gamemode = gamemode
		self.lobby = lobby

		super().__init__(*args, **kwargs)

		self.add_item(discord.ui.InputText(label="Player Name"))

	async def callback(self, interaction: discord.Interaction):
		self.mem_names.append(self.children[0].value)
		self.members.append(0)

		resp = f'There are currently {len(self.members)} in the channel who are selected for the inhouse. To add more players, click the **Add Players** button. To remove players, use the **Remove Players** button. Once you are ready to start the game, click the **Continue** button. To quit, click the **Quit** button.'
		await interaction.response.edit_message(content=resp, view=StartMenuButtons(self.caller, self.members, self.mem_names, self.gamemode, self.lobby, timeout=3600))

class RemovePlayerSelect(discord.ui.Select):
	def __init__(self, members, mem_names, caller, gamemode, lobby):
		self.members = members
		self.mem_names = mem_names
		options = []
		self.caller = caller
		self.gamemode = gamemode
		self.lobby = lobby
		for member in mem_names:
			options.append(discord.SelectOption(label=member))

		super().__init__(placeholder = "Player Name", min_values = 1, options=options)

	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.adminis

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	async def callback(self, interaction: discord.Interaction):
		for selected in self.values:
			for name in self.mem_names:
				if selected == name:
					del self.members[self.mem_names.index(name)]
					self.mem_names.remove(name)

		resp = f'There are currently {len(self.members)} in the channel who are selected for the inhouse. To add more players, click the **Add Players** button. To remove players, use the **Remove Players** button. Once you are ready to start the game, click the **Continue** button. To quit, click the **Quit** button.'
		await interaction.response.edit_message(content=resp, view=StartMenuButtons(self.caller, self.members, self.mem_names, self.gamemode, self.lobby, timeout=3600))

class RemovePlayerView(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, lobby, timeout):
		super().__init__(timeout = timeout)
		self.add_item(RemovePlayerSelect(members, mem_names, caller, gamemode, lobby))


class StartMenuButtons(discord.ui.View):
	def __init__(self, caller, members, mem_names, gamemode, lobby ,timeout):
		self.caller = caller
		self.members = members
		self.mem_names = mem_names
		self.gamemode = gamemode
		self.lobby = lobby
		super().__init__(timeout = timeout)

	async def interaction_check(self, interaction: discord.Interaction):
		return (interaction.user.id == self.caller.id) or interaction.user.guild_permissions.administrator

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True
		await self.message.edit(content="Command Timed Out.", view=self) # Go to next part

	@discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
	async def continue_button_callback(self, button, interaction):
		resp = randomizer(self.mem_names, self.gamemode)
		if self.gamemode == 2:
			map_resp = map_picker()
			await interaction.response.edit_message(content=resp + map_resp, view=GameCreateButtonsVal(self.caller, self.members, self.mem_names, self.gamemode, resp, map_resp, self.lobby, timeout=3600)) # Go to next part
		else:
			await interaction.response.edit_message(content=resp, view=GameCreateButtons(self.caller, self.members, self.mem_names, self.gamemode, resp, self.lobby, timeout=3600)) # Go to next part
	
	@discord.ui.button(label="Add Player", style=discord.ButtonStyle.primary)
	async def add_button_callback(self, button, interaction):
		await interaction.response.send_modal(AddPlayerModal(self.members, self.mem_names, self.caller, self.gamemode, self.lobby, title="Add a Player")) # Go to next part

	@discord.ui.button(label="Remove Player", style=discord.ButtonStyle.danger)
	async def remove(self, button, interaction):
		resp = "Please select which of the users below you would like to remove."
		await interaction.response.edit_message(content=resp, view=RemovePlayerView(self.caller, self.members, self.mem_names, self.gamemode, self.lobby, timeout=3600)) # Go to next part

	@discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary)
	async def quit_button_callback(self, button, interaction):
		for child in self.children:
			child.disabled = True
		await interaction.response.edit_message(content="GG!")

@bot.slash_command(description='Starts an inhouse lobby with the members in current voice channel.')
@discord.commands.option("game_mode", description="Set the type of game this inhouse will be. Optional, can set as league or valorant.", choices=games, default="none")
async def inhouse(
	ctx: discord.ApplicationContext,
	game_mode: str,
):
	caller = ctx.author
	try:
		lobby = caller.voice.channel
	except:
		await ctx.send("You must be in a voice channel to run this command.")
		return

	timeout_start = time.time()
	complete = False

	if (len(lobby.members) == 0):
		await ctx.send("You must be in a voice channel to run this command.")
		return

	mem_names = []
	for member in lobby.members:
		if member.nick:
			mem_names.append(member.nick)
		else:
			mem_names.append(member.name)

	if (game_mode == "league"):
		gamemode = 1
	elif (game_mode == "valorant"):
		gamemode = 2
	else:
		gamemode = 0

	resp = f'There are currently {len(mem_names)} in the channel who are selected for the inhouse. To add more players, click the **Add Players** button. To remove players, use the **Remove Players** button. Once you are ready to start the game, click the **Continue** button. To quit, click the **Quit** button.'
	
	await ctx.respond(resp, view=StartMenuButtons(caller, lobby.members, mem_names, gamemode, lobby, timeout=3600))

bot.run(TOKEN)