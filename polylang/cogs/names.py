from main.gamename import game
from main.cityname import city, alphabet
from main.elyrion import ely_to_eng, eng_to_ely
from discord.ext import commands
import discord


async def imitate(ctx, text, original):
    try:
        whs = await ctx.channel.webhooks()
        if whs:
            wh = whs[0]
        else:
            wh = await ctx.channel.create_webhook(name='Toolkit')
        m = await wh.send(
            text, username=ctx.author.display_name,
            avatar_url=str(ctx.author.avatar), wait=True
        )
    except discord.Forbidden:
        e = discord.Embed(description=text)
        e.set_author(
            name=ctx.author.display_name,
            icon_url=str(ctx.author.avatar)
        )
        e.set_footer(
            text='For full fuctionality, please give the bot the manage webhooks '
                 'permission.'
        )
        m = await ctx.send(embed=e)
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        await ctx.send(
            'For full fuctionality, please give the bot the manage messages '
            'permission.'
        )
    await m.add_reaction('❓')
    def check(reaction, user):
        return (
            reaction.emoji == '❓' and reaction.message.id == m.id 
            and not user.bot
        )

    while True:
        _, user = await ctx.bot.wait_for('reaction_add', check=check)
        await user.create_dm()
        await user.dm_channel.send(original)


class Names(commands.Cog):
    """Generate names for cities and games. Copies original game logic.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Get a city name.')
    async def city(self, ctx, tribe='', number: int = 1):
        """
        Generate a city name. You may provide a tribe to search for. If no \
        tribe is provided, a random one will be chosen.
        Examples:
        `{{pre}}city` --> a random city name
        `{{pre}}city lux` --> a luxidoor city name
        `{{pre}}city hood 10` --> 10 hoodrick city names
        """
        await ctx.send(city(tribe, number))

    @commands.command(brief='Get a game name.')
    async def game(self, ctx, crazy: bool = False, number: int = 1):
        """
        Generate a game name. Set crazy to true for crazy game names. As \
        per the game, setting crazy to true does bot *guaruntee* craziness, \
        only gives a possibilty.
        Exampels:
        `{{pre}}game` --> generate a normal game name
        `{{pre}}game true` --> generate a crazy game name
        `{{pre}}game false 5` --> get 5 normal game names
        """
        await ctx.send(game(crazy, number))

    @commands.command(brief='Get an alphabet.')
    async def letters(self, ctx, tribe=''):
        """
        Get a tribe's alphabet. You may provide a tribe to search for. If \
        no tribe is provided, a random one will be chosen.
        Examples:
        `{{pre}}letters` --> a tribe's alphabet
        `{{pre}}letters lux` --> the luxidoorian alphabet
        """
        await ctx.send(alphabet(tribe))

    @commands.command(brief='Translate to Elyrion.')
    async def elyrion(self, ctx, *, english):
        """
        Translate text to elyrion.

        Examples:
        `{{pre}}elyrion This is what I want to convert.`
        """
        text = eng_to_ely(english)
        if ctx.guild:
            await imitate(ctx, text, english)
        else:
            await ctx.send(text)

    @commands.command(brief='Translate from Elyrion.')
    async def english(self, ctx, *, elyrion):
        """
        Translate text from elyrion.

        Examples:
        `{{pre}}elyrion Ŧţi^ i^ ~ţaŦ i ~aŋŦ Ŧȱ #ȱŋ‡∑rŦ.`
        """
        await ctx.send(ely_to_eng(elyrion))
