# Kirbot
Kirbot is a relatively simple bot, written in python.

Its main functionality includes stream alerts and notifications,
a full fledged custom command system,
commands to get run info from speedrun.com, as well
as a permission system to restrict access to some of these commands

## Building
Kirbot depends on discord.py, which can be installed like so:

`python3 -m pip install -U discord.py`

A config.json file will need to be configured like in the example.


# Commands

## Speedrun
`!search Game Name` Searches for the corresponding abbreviation for a game.
This can be done automatically by commands by surrounding the game name in quotes "".

`abbreviation` may be replaced with `"Game Name"` in any of the following commands to search for the corresponding
abbreviation for a game, before then executing the rest of the command.


`!categories abbreviation` Fetches a list of categories for a game. Categories are important to being able to fetch specific runs.

`!wr abbreviation category` Gets the wr for a given game, and category.

`!Nth abbreviation category` Gets the *Nth* time for a given *game*, and *category*.
Negative numbers can be used as well, in order to get times from last place. (i.e.
-1st "Chrono Trigger" Any% will get the last place time for that category)
This command will also pattern match `!*st` and `!*nd`


## Permissions
There are currently 3 levels of permissions that you can assign to certain roles in
your server. If permission level X is set to role A, only members of that role A or higher can access commands of level X or lower.


`!permissions info` Gives you info about these commands

`!permissions list` Roles have a given hierarchy in a server, based on how they're
ordered by the owner. This command lets you see that hierarchy, as well as the individual levels.

`!permissions set N role` Sets permission level *N* to *role*


## Streams
These commands allow you to setup a stream list, and have kirbot alert you when streams go live, and edit messages when they go offline.

`!streaminfo twitchname` Fetches some basic info on a stream currently live,
such as *status*, *viewer count*, and *uptime*

`!streams info` Gives you info about these commands.

`!streams live` Returns a list of streams currently live in a server

`!streams count` Returns a count of streams currently in the list

`!streams add twitchname` Adds a new twitchname to the stream list in that server. Kirbot will verify that that name is actually a valid twitch handle before adding it to its list.

`!streams adds name1, name2, ...` Adds as many streams as you want to the list. Because of the asyncronous nature of commands, It's better to split batch adding into multiple commands, that can run concurrently.

`!streams remove twitchname` Removes a stream from the list.

`!streams enable` Enables alerts in the channel from which this command is used

`!streams disable` Disables alerts in that server

## Filters
Filters allow you to restrict Kirbot to only alerting streams playing certain games

`!filters info`

`!filters list` Lists out the filters currently in place.

`!filters add gamename` Adds a new game to the list of filters

`!filters remove gamename` Removes a game from the list of filters

`!filters enable` Activates stream filtering.

`!filters disable` Disactivates stream filtering.


## Custom Commands
Allows you to create full Embeds for commands, instead of just text. Some of the functionality may seem superfluous to those who aren't familiar with how discord embeds work.

Custom commands can be accessed with ?*name*

`!commands info`

`!commands list` Lists all the commands created in this server.

`!commands new name description` Adds a new custom command, under *name*, with *description* as the text of the command

`!commands remove name` Removes the corresponding command from the list.

`!commands edit param1(content) param2(content)`
This command edits a preexisting command.
The parameters this command can take are *title()*, *description()*, *url()*, and *color()*. You can include any of them in the command. Use `!commands colors` for a list of colors.

`!commands addfields title(content) value(content)`  Every embed field has a title and a value. Up to 24 fields can be added to a message (discord restriction).

`!commands delfield n` Deletes the nth field (starting at 0) of a command.
