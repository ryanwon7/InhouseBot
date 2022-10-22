# Discord Inhouse Bot
## Overview
This is a bot to set up, manage, and run in house matches for any games in your Discord server. It can randomly create teams for you, and will move everyone to their team channel. 

## Directory Structure
The inhouse_bot.py script runs the Inhouse Discord bot. Config variables are stored in a local .env variable for local run environment of the bot, which is hosted on a private Raspberry Pi Server.


## Usage
### Inhouse Slash Command
To use the inhouse system, the slash command is /inhouse. The usage of the command is shown below:

`/inhouse`

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse1.gif)

With the inhouse slash command, you can optionally choose the game mode as either League or Valorant. Choosing either one gives minor cosmetic and text changes, and choosing Valorant allows you to choose a random map as well. You can also run the command without the game mode option, as shown below.

![](https://github.com/InhouseBot/production/resources/inhouse2.png)

##### Add or Remove Players
You can add players to the inhouse game lobby by clicking the Add Player button. Please note that adding player will only add them to the team creation, but will not move them to the voice channels.

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse3.gif)

To Remove a player from the inhouse game lobby, click Remove Player.

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse4.gif)

##### Game Creation
Upon clicking continue, you will be presented with teams as well as a map choice if you set the gamemode to Valorant. 

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse5.gif)

From here, you can click reroll teams to either re-randomize the teams, or click Reroll Map if the gamemode is Valorant to change the map. Once everything is finished, you can click Continue. This will show a confirmation screen as seen below.

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse6.gif)

From here, you can also click Previous to go back to change any of the settings. Click Starting Game will create channels and move existing players to them, as shown below.

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse7.gif)

Finally, once the game is completed and everyone should return to the original discord channel, click the End Game button.

![](https://github.com/InhouseBot/blob/production/resourcesresources/inhouse8.gif)

At any time to exit the bot, click Quit.

## Known Bugs
The following are the list of known bugs or incorrect functionality.
* Currently do not have proper exception handling which can kill some commands.
* Occasionally rerolling a map in Valorant gamemode will return the same map.
* The Slash command will sometimes display ("Command Failed") even though the interaction is continuing.

If you find any bugs, please let me know by opening an issue on the Github page.

## Work in Progress
The following commands and functionality are currently being developed:
* Create team command - use for instances when captains are picking teams, or teams are known beforehand and you want to preserve the voice channel movement feature
* Spanish Language Support