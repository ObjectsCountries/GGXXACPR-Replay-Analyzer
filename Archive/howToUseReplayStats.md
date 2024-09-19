# Using ReplayStats.py

ReplayStats.py is a companion script to the OrganizeReplaysMetaData.py script.

You'll need to run that organization first for this to work.
Additionally, this script should be placed within the same folder directory as your organizer, and config file.

After your replays are organized, you can run this script on the command line.
It will print out your personal character matchup statistics.

You can include a list of players as an optional parameter, and it will only aggregate information against those players.
Alternatively, if you include a parameter after that list, it will exclude them instead.

As always, if you have any questions or run into any problems with this, feel free to contact me.

## Example Commands

`(file directory)>ReplayStats.py`

This will use all of your replays to display your matchup statistics.

`(file directory)>ReplayStats.py player1,player2`

This will only include replays against player1 or player2 to display your matchup stats against them.

`(file directory)>ReplayStats.py player1,player2 exclude`

This will exclude replays against player1 and player2 to display your matchup stats against everyone else.