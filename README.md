# Discord Inhouse Bot
## Overview
This is a bot to set up, manage, and run in house matches for any games in your Discord server. It can randomly create teams for you, and will move everyone to their team channel. 

## Directory Structure
The bot.py script runs the Inhouse Discord bot. Config variables are stored in a local .env variable for local repositories of the bot, while the Heroku service has the database and discord bot token set in the config variables for Heroku.

The Procfile, runtime.txt, and requirements.txt files are all files that are used for the running of the file in heroku. Procfile contains command for heroku to run the bot as a worker dyno, while runtime.txt contains the desired version of python to execute and requirements.txt contains the necessary non standard python libraries used.

## Usage
### Channel Set Command
The first command you should run before using the bot is the !setchannel command. The following is the usecase for the !setchannel command.

`!setchannel <lobby-name> <team1-name> <team2-name>`

The three required arguments for the !setchannel command are the names of the channels for the Lobby channel, Team 1 channel, and Team 2 channel. The other commands will not function if the channels have not been set with the !setchannel command, so this command must be properly run first.

### Inhouse Base Command
To use the inhouse system, the first base command is !inhouse. The usage of the command is shown below:

`!inhouse`

The inhouse command will take all users from the voice channel of the user who sends the command, and will use these as the people who are playing in the inhouse game. To add players, use the "+" reaction. To remove players, use the "-" reaction. When adding players, you are only adding them by name for team selection - they will not be moved to team discord channel. Removing players will remove them from being added to a team. After accepting by clicking the "ok" reaction, the bot will show a randomized list of teams. To reshuffle, click the "reshuffle" reaction. To accept, click the "ok" reaction. Doing so will reach a confirmation message, and reacting "ok" to this message will move all users to the appropriate team channel.

At all message prompts, you can also quit at any time by reacting with the "X" reaction. Also note that the only people that can interact with the bot once it is summoned using the !inhouse command is the caller of the command and users with adminstrator privileges.

### End Game Command
The end game command returns all players in both designated team channels to the channel designated as the lobby, regardless of whether they were included in the original inhouse teams. The usage is shown below:

`!endgame`

### Rematch Command
The rematch command creates teams based off the last played game in the server. The usage is shown below:

`!rematch`

You will then have the option to accept, switch the sides of the teams, or quit. If accepting, clicking ok once more will move all players. At all message prompts, you can also quit at any time by reacting with the "X" reaction. Also note that the only people that can interact with the bot once it is summoned using the !rematch command is the caller of the command and users with adminstrator privileges.

## Known Bugs
The following are the list of known bugs or incorrect functionality.
* Currently do not have proper exception handling which can kill some commands.
* Channel names with the :desktop: emoji in them cannot be set for inhouse channels.
* Having an odd amount of players for a match, and then using the rematch function will not correctly create teams.

If you find any bugs, please let me know by opening an issue on the Github page.

## Work in Progress
The following commands and functionality are currently being developed:
* Create team command - use for instances when captains are picking teams, or teams are known beforehand and you want to preserve the voice channel movement feature