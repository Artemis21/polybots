"""Meta commands."""
from discord.ext import commands
import discord


SOURCE = 'https://github.com/Artemis21/polybots/tree/master/polystats'
ABOUT = (
    'PolyStats was created by Artemis#8799, using images from '
    '[James McGaha\'s collection](https://drive.google.com/drive/u/1/folders/'
    '1FKxyti7vKHblDiEZ5pzIkvySFVpOXgf_), and JD\'s unit abbreviations.'
)
LINK = '[**Click here**]({url})'


class Meta(commands.Cog):
    """Meta cog."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot
        bot.help_command.cog = self

    @commands.command(brief='About the bot.')
    def about(self, ctx: commands.Context):
        """Show some information about the bot."""
        await ctx.send(embed=discord.Embed(
            title='About', description=ABOUT, colour=0xff67be
        ).add_field(
            name='Source', value=LINK.format(SOURCE)
        ).add_field(
            name='Invite', value=LINK.format(
                discord.utils.oauth2_url(self.bot.user.id)
            )
        ).add_field(
            name='Servers', value=len(self.bot.guilds)
        ))
