# Discord Inhouse Bot
## Overview
This is a bot to set up, manage, and run in house matches for any games in your Discord server. It can randomly create teams for you, and will move everyone to their team channel. 

## Directory Structure
The bot.py script runs the Inhouse Discord bot. There is a hidden file, .env, which is not included in the GitHub repositiory, which has the information regarding the bot token as well as the MongoDB connection string.

## Usage
### Channel Set Command
The first command you should run before using the bot is the !setchannel command. The following is the usecase for the !setchannel command.

`!setchannel <lobby-name> <team1-name> <team2-name>`

The three required arguments for the !setchannel command are the names of the channels for the Lobby channel, Team 1 channel, and Team 2 channel. The other commands will not function if the channels have not been set with the !setchannel command, so this command must be properly run first.

### Inhouse Base Command
To use the inhouse system, the first base command is !inhouse. The usage of the command is shown below:

`!inhouse [players]`

The !inhouse command as an optional argument of the number of players that will take part in the game. The default number of players is ten, however at the moment having different number of players does not have any effect at all. In the future support will be added to change the structure of the command based on the number of players participating.

The command will take all users from the voice channel of the user who sends the command, and will use these as the people who are playing in the inhouse game. To add players, use the "+" reaction. To remove players, use the "-" reaction. When adding players, you are only adding them by name for team selection - they will not be moved to team discord channel. Removing players will remove them from being added to a team. After accepting by clicking the "ok" reaction, the bot will show a randomized list of teams. To reshuffle, click the "reshuffle" reaction. To accept, click the "ok" reaction. Doing so will reach a confirmation message, and reacting "ok" to this message will move all users to the appropriate team channel.

### End Game Command
The end game command returns all players in both designated team channels to the channel designated as the lobby, regardless of whether they were included in the original inhouse teams. The usage is shown below:

`!endgame`

## Known Bugs
The following are the list of known bugs or incorrect functionality.
* When adding players in the add part of !inhouse command, entering a user with a space in their name results in two different players being added

If you find any bugs, please let me know by opening an issue on the Github page.

## Work in Progress
The following commands and functionality are currently being developed:
* Limit reactions to only the user who authored the original !inhouse command
* Rematch command - load teams from the last generated set of teams
* Create team command - use for instances when captains are picking teams, or teams are known beforehand and you want to preserve the voice channel movement feature
* Exit from current command - letting a command timeout or simply starting a new command will exit the current command. Looking to build a cleaner way to exit the current command without raising exceptions.