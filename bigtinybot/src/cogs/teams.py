from models import details
from utils import logs, contact
from utils.checks import caution, admin
from utils.matchmaking import find_game
from utils.paginator import CodePaginator
from discord.ext import commands, tasks
from pandas import DataFrame
import discord
import io


async def handle_sm(ctx, s, m):
    if type(m) == discord.Embed:
        return await ctx.send(embed=m)
    await ctx.send(m)


class Teams(commands.Cog):
    """Info on teams and the tourney.
    """
    def __init__(self, bot):
        self.bot = bot
        self.data = details.Teams
        self.ready = False

    def cog_unload(self):
        self.data.save()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.ready:
            logs.log(
                'Bot restarted, but hopefully no changes lost.',
                'OTHER'
            )
            await contact.load(self.bot)
            self.data.load(self.bot)
            self.save.start()
            self.ready = True

    @tasks.loop(minutes=1)
    async def save(self):
        self.data.save()

    @commands.command(brief='Register your team.')
    async def register(self, ctx, name, partner: discord.Member):
        """Register a team to take part in the tourney.
        `name` is the name of the team. `partner` is you teammate.
        IMPORTANT: at the time of signing up, your global ELO + your \
        teammate's global ELO *must* be less than 2650!
        """
        s, m = self.data.add_team(name, (ctx.author, partner))
        await handle_sm(ctx, s, m)
        if s:
            team = self.data.find_by_member(ctx.author)
            logs.log(
                f'Team {team.name}, ID {team.team_id} created with '
                f'{ctx.author} and {partner}.',
                'TEAMS'
            )

    @commands.command(brief='Delete a team.')
    async def quit(self, ctx, team_id=None):
        """Remove a team from the tourny. Only tournament admins may remove
        someone elses team.
        `team_id` is the id of the team to delete, defaults to the team you \
        are in.
        """
        if not await caution(ctx, self.bot):
            return
        if admin(ctx.author) and team_id:
            tid = team_id
            team = self.data.teams.find_by_id(team_id)
        else:
            team = self.data.find_by_member(ctx.author)
            if not team:
                return await ctx.send('You\'re not even in the tourney!')
            tid = team.team_id
        s, m = self.data.remove_team(tid)
        await handle_sm(ctx, s, m)
        if s:
            logs.log(
                f'Team {team.name}, ID: {team.team_id} was deleted.', 'TEAMS'
            )

    @commands.command(brief='View a team.')
    async def team(self, ctx, team_id=None):
        """View the details of a team.
        `team_id` is the id of the team to view, defaults to the team you \
        are in.
        """
        if not team_id:
            team = self.data.find_by_member(ctx.author)
            if not team:
                return await ctx.send('No team found...')
            team_id = team.team_id
        await handle_sm(ctx, *self.data.team_details(team_id))

    @commands.command(brief='Search by member.')
    async def userteam(self, ctx, member: discord.Member):
        """Search for a team by team member, eg. `&userteam @Artemis` or \
        `&userteam Ramana`.
        """
        team = self.data.find_by_member(member)
        if team:
            await ctx.send(embed=team.display())
        else:
            await ctx.send('No team found...')

    @commands.command(brief='Search by name.')
    async def search(self, ctx, *, name):
        """Search for a team by team name, or a portion of the team name, eg. \
        to search for team "The Birbs", both `&search The Birbs` and \
        `&search birbs` should work.
        """
        for team in self.data.teams.values():
            if name.lower() in team.name.lower():
                return await ctx.send(embed=team.display())
        await ctx.send('No team found...')

    @commands.command(brief='View all teams.')
    async def teams(self, ctx):
        """View a list of every team, including remaning lives, team name and \
        team ID.
        """
        tlist = list(self.data.teams.values())
        tlist.sort(reverse=True, key=lambda x: (x.lives, x.wins))
        lines = ''
        qs = {1: '- ', 2: '  ', 3: '+ '}
        n = 1
        for i in tlist:
            q = qs[i.lives]
            lines += f'{q}{n}. {i.team_id} {i.name}\n'
            lines += f'{q}Lives: {i.lives}, Wins: {i.wins}\n\n'
            n += 1
        lines = lines[:-1]
        head = 'diff'
        await CodePaginator(ctx, lines, head, 24).setup()

    @commands.command(brief='Get the data in excel.')
    async def excel(self, ctx):
        """Get an excel file containing all the teams' stats.
        """
        columns = {
            'Name': [], 'ID': [], 'ELO': [], 'Lives': [], 'Games': [],
            'Wins' :[], 'Hosts':[], 'Player 1': [], 'Player 2': []
        }
        for i in self.data.teams.values():
            columns['Name'].append(i.name)
            columns['ID'].append(i.team_id)
            columns['ELO'].append(i.extra)
            columns['Lives'].append(i.lives)
            columns['Games'].append(i.games)
            columns['Wins'].append(i.wins)
            columns['Hosts'].append(i.hosts)
            columns['Player 1'].append(i.players[0])
            columns['Player 2'].append(i.players[1])
        df = DataFrame(columns)
        df.to_excel('data/TTteams.xlsx', sheet_name='teams', index=False)
        f = discord.File('data/TTteams.xlsx', 'TTteams.xlsx')
        await ctx.send(file=f)

    @commands.command(brief='View tourney details.')
    async def tourney(self, ctx):
        """View the current state of the tournament.
        """
        await ctx.send(embed=self.data.details())

    @commands.command(brief='Record a completed game.')
    async def conclude(self, ctx, opponent_id, team_id=None):
        """Record a completed game. This may either be done by the loosing \
        team or a tournament admin.
        `opponent_id`: the ID of the winning team.
        `team_id`: the ID of the loosing team, defaults to that of the person \
        running the command.
        """
        if admin(ctx.author) and team_id:
            tid = team_id
        else:
            team = self.data.find_by_member(ctx.author)
            if not team:
                return await ctx.send('You\'re not even in the tourney!')
            tid = team.team_id
        await ctx.send(
            f'Pending confirmation: {opponent_id.upper()} beat {tid.upper()}.'
        )
        if not await caution(ctx, self.bot):
            return
        s, m = self.data.conclude(tid, opponent_id)
        await handle_sm(ctx, s, m)
        if s:
            logs.log(f'{opponent_id.upper()} beat {tid.upper()}.', 'WINS')
            logs.log(f'{opponent_id.upper()} beat {tid.upper()}.', 'GAMES')
            for i in m.split('\n'):
                logs.log(i, 'OTHER')

    # Automatic match command:

    # @commands.command(brief='Find a new match.')
    # async def match(self, ctx):
        # """Find a new match. This may not always be possible.
        # """
        # team = self.data.find_by_member(ctx.author)
        # if not team:
            # return await ctx.send('You\'re not even in the tourney!')
        # return await handle_sm(
            # ctx, *find_game(team, self.data)
        # )

    @commands.command(brief='Edit ELO.')
    async def elo(self, ctx, info, team_id=None):
        """Set your team's combined global ELO. This may not be more than 2650.
        Tourney admins can also provide a team ID to set ELO for another team.
        """
        if admin(ctx.author) and team_id:
            tid = team_id
        else:
            team = self.data.find_by_member(ctx.author)
            if not team:
                return await ctx.send('You\'re not even in the tourney!')
            tid = team.team_id
        return await handle_sm(
            ctx, *self.data.set_extra(tid, info)
        )

    @commands.command(brief='Edit team name.')
    async def rename(self, ctx, *, name):
        """Change your team's name.
        """
        team = self.data.find_by_member(ctx.author)
        if not team:
            return await ctx.send('You\'re not even in the tourney!')
        return await handle_sm(
            ctx, *self.data.rename(team.team_id, name)
        )

    @commands.command(brief='Switch teammate.')
    async def switch(self, ctx, new: discord.Member):
        """Change your teammate. Make sure your old teammate is happy with \
        this!
        """
        team = self.data.find_by_member(ctx.author)
        if not team:
            return await ctx.send('You\'re not even in the tourney!')
        s, m = self.data.set_players(team.team_id, ctx.author, new)
        await handle_sm(ctx, s, m)
        if s:
            logs.log(
                f'{ctx.author} swapped their teammate for {new} in team '
                f'{team.team_id}.',
                'TEAMS'
            )

    @commands.command(brief='Swap out with another player.')
    async def swap(self, ctx, new: discord.Member, old: discord.Member=None):
        """Swap out with another player - they take your position in the \
        tourney. A tourney admin may swap someone else out.
        """
        old = old or ctx.author
        if old != ctx.author and not admin(ctx.author):
            return await ctx.send('Only admins may swap someone else out!')
        team = self.data.find_by_member(old)
        if not team:
            return await ctx.send('You\'re not even in the tourney!')
        players = list(team.players)
        if players[0] == old:
            players[0] = new
        else:
            players[1] = new
        s, m = self.data.set_players(team.team_id, *players)
        await handle_sm(ctx, s, m)
        if s:
            logs.log(
                f'{old} swapped out with {new} in team {team.team_id}.',
                'TEAMS'
            )

    @commands.command(brief='View logs.')
    async def logs(self, ctx, level=None):
        """View logs from the tourney. Provide the `level` parameter to only \
        see one type of log - choose from `GAMES`, `WINS`, `TEAMS` and \
        `TOURNEY` (not case sensitive). If it is over the 2000 char limit, a \
        download will be provided.
        """
        text = logs.fetch(level)
        if len(text) > 2000:
            strio = io.StringIO(text)
            f = discord.File(strio, 'TTlog.txt')
            extra = '...```Full version:'
            await ctx.send(
                text[:2000-len(extra)] + extra,
                file=f
            )
        else:
            await ctx.send(text)


class Admin(commands.Cog):
    """Admin only commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.data = details.Teams

    @commands.command(brief='Open the tourney.')
    async def open_signups(self, ctx):
        """Open signups for the tourney. This may only be done by a tourney \
        admin and may only be done once - proceed with caution!
        """
        if not admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await caution(ctx, self.bot):
            return
        s, m = self.data.open()
        await handle_sm(ctx, s, m)
        if s:
            logs.log('Signups opened.', 'TOURNEY')

    @commands.command(brief='Start the tourney.')
    async def start_tourney(self, ctx):
        """Let the tourney begin! This may only be done by a tourney \
        admin and may only be done once - proceed with caution!
        """
        if not admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await caution(ctx, self.bot):
            return
        s, m = self.data.start()
        if s:
            logs.log('Tourney started.', 'TOURNEY')
        await handle_sm(ctx, s, m)

    @commands.command(brief='Reset the tourney.')
    async def reset(self, ctx):
        """Delete all tourney data. This may only be done by a tourney \
        admin and is irreversible - proceed with caution!
        """
        if not admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        if not await caution(ctx, self.bot):
            return
        self.data.reset()
        await ctx.send('And with a "Poof!" all their data was gone.')
        logs.log('Tourney reset.', 'TOURNEY')

    @commands.command(brief='Start a new match.')
    async def match(self, ctx, home, away, round_num='1/2/3'):
        """Start a new match, home vs away. This is for manual matchmaking by \
        tourney mods. Provide `round_num` to add data to the announcement.
        """
        if not admin(ctx.author):
            return await ctx.send('You must be an admin to run this command!')
        s, m = self.data.open_game(home, away)
        await handle_sm(ctx, s, m)
        if s:
            log_m = f'{home} to host against {away}.'
            logs.log(log_m, 'GAMES')
            team1 = self.data.find_by_id(home)
            team2 = self.data.find_by_id(away)
            round_info = (
                f' in round {round_num}.\nRemember to prefix the game name '
                f'with `TT{round_num}`!'
            )
            send_m = f'{team1} to host against {team2}{round_info}'
            await contact.ANNOUNCE.send(send_m)
