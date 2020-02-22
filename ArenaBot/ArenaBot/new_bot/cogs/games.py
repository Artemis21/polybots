from models.games import Games as Data
from models.modes import Modes
from discord.ext import commands
import discord


class GameConv(commands.Converter):
    async def convert(self, ctx, arg):
        if game_id not in Data.games:
            raise discord.CommandError(f'Game ID `{game_id}` not found.')
        return Data.games[game_id]

    async def default(self, ctx):
        game = Data.get(ctx.channel)
        if not game:
            await ctx.send('No game associated with this channel.')
            return None
        return game


class Games(commands.Cog):
    '''Commands for managing games.
    '''
    def __init__(self, bot):
        self.bot = bot

    def pretty_game(self, game, incl_open=False):
        if game.open:
            maxpl = game.mode.players * game.mode.teams
            extra = f'{len(game.players)}/{maxpl} players'
        else:
            extra = '#' + game.channel.name
        mode = game.mode.name
        id = game.id
        isopen = ['in progess', '      open'][game.open]
        isopen = ['', f' {isopen} -'][incl_open]
        return f'ID {id:>3}:{isopen} {mode:>9} ({extra})'

    @commands.command(brief='View all games.')
    async def games(self, ctx):
        '''View all games in the bot, either in progress or open.
        '''
        games = []
        for id in Data.games:
            games.append(self.pretty_game(game), True)
        await ctx.send('```'+('\n\n'.join(games) or 'No games')+'```')

    @commands.command(brief='View open games.', aliases=['open'])
    async def opengames(self, ctx):
        '''View all open and joinable games.
        '''
        games = []
        for id in Data.games:
            game = Data.games[id]
            if not game.open:
                continue
            if game.tier and game.tier not in ctx.author.roles:
                continue
            games.append(self.pretty_game(game))
        await ctx.send('```'+('\n\n'.join(games) or 'No games')+'```')

    @commands.command(brief='View a game.')
    async def game(self, ctx, game: GameConv=None):
        '''View a game's details. `game` defaults to that of this channel, \
        if any.
        '''
        game = game or await GameConv.default(ctx)
        if not game:
            return
        await ctx.send(embed=game.display())

    @commands.command(brief='Join a game.')
    async def join(self, ctx, game_id):
        '''Join a game. Give a game ID.
        '''
        if game_id not in Data.games:
            return await ctx.send(f'Game ID `{game_id}` not found.')
        game = Data.games[game_id]
        if not game.open:
            return await ctx.send('That game is full.')
        mes = await game.add_player(ctx.author)
        await ctx.send(mes)

    @commands.command(brief='Get a modifier.')
    async def modifier(self, ctx):
        '''Get game modifiers. The host should do this at the start of the \
        game, and, in scrambles, on every turn multiple of 5. See the rules \
        for more info.
        '''
        game = await GameConv.default(ctx)
        if not game:
            return
        if game.players[0].id != ctx.author.id:
            return await ctx.send('Only the host may get the modifiers.')
        await ctx.send(game.modifier())

    @commands.command(brief='View all modes.')
    async def modes(self, ctx):
        '''View a list of every game mode.
        '''
        await ctx.send(Modes.pretty_modes())

    @commands.command(brief='Open a new game.', aliases=['new', 'newgame'])
    @commands.has_permissions(manage_channels=True)
    async def opengame(
        self, ctx, mode: Modes.get_mode, tier: discord.Role=None
    ):
        '''Open a new game.
        Examples:
        `{{pre}}opengame skirmish3` open a new 3 player skirmish
        `{{pre}}opengame double @Mid tier` open a double modifier game only \
        for people with the mid tier role
        `{{pre}}opengame rumble4 "Base tier"` open a 4 player rumble only for \
        people with the base tier role
        '''
        game = Data.new(mode, tier)
        await ctx.send(f'Game created! ID: `{game.id}`.')

    @commands.command(brief='Delete a game.')
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx, game: GameConv=None):
        '''Delete a game. `game` defaults to that of this channel, if any.
        '''
        game = game or await GameConv.default(ctx)
        if not game:
            return
        await game.delete()
        await ctx.send('Done')

