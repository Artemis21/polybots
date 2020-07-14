"""Meta commands."""
from discord.ext import commands
import discord

from tools.errors import on_command_error


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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Send prefix if bot is mentioned."""
        if message.guild:
            me = message.guild.me
        else:
            me = self.bot.user
        if me in message.mentions:
            await message.channel.send(
                f'My prefix is `{self.bot.command_prefix}`.'
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle an error."""
        await on_command_error(ctx, error)

    @commands.command(brief='About the bot.')
    async def about(self, ctx: commands.Context):
        """Show some information about the bot."""
        await ctx.send(embed=discord.Embed(
            title='About', description=ABOUT, colour=0xff67be
        ).add_field(
            name='Source', value=LINK.format(url=SOURCE)
        ).add_field(
            name='Invite', value=LINK.format(
                url=discord.utils.oauth_url(
                    self.bot.user.id, permissions=discord.Permissions(
                        send_messages=True, read_messages=True
                    )
                )
            )
        ).add_field(
            name='Servers', value=len(self.bot.guilds)
        ))
