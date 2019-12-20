BigTinyBot is a small bot intented to help with the TinyTourney. Its functions include:
 - registering teams
 - keeping track of remaining teams and lives
 - keeping track of no. of wins
 - matchmaking

__**Registering:**__
You should only do this once you have a teammate. To register, just use the command `&register TeamName @partner`, then do `&elo XXXX`, where `XXXX` is your combined local ELO. Remember, this must be below `2550`. Note: If you want a space in your team name, do `&register "Team Name" @partner`.
You can delete your team with the command `&quit`. Consult your teammate first!
__**Other team-related commands:**__
A team ID is a 5-digit code, unique to your team. They are case sensitive. You can view a list of every team with their ID's with the `&teams` command.
To view a specific team, use the `&team TEAMID` command. Just doing `&team` will show details of your own team.
__**Games:**__
To start a new game, use the `&match` command. This will find you a team to play against if possible. When a match is over, the *loosers* should do `&conclude <opponent_id>`. Example: team AAAAA wants a new game. They do `&match` and it tells them to start a game against team BBBBB. So, they register this game in the PolyEloBot. In the end, it turns out that BBBBB won. Now, AAAAA must do `&conclude BBBBB`. If they don't, a player can contact a tourney mod who has the power to do it for them.
__**Other:**__
View the current state of the tourney with the `&tourney` command. Get help on any command with `&help command_name`, or do `&help` for a list of commands.
