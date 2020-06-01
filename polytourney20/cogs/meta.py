"""The meta cog."""
import discord
from discord.ext import commands

from tools.config import Config
from tools.errors import on_command_error
from tools.checks import admin


ABOUT = (
    '{bot_name} was created by Artemis#8799 for the 2020 Supreme Summer '
    'Skirmish. You can find more information about the tournament '
    '[here](https://polytopia.fun). The bot mostly acts as an interface to '
    'the Google spreadsheet.'
)
INVITE = (
    'https://discord.com/api/oauth2/authorize?client_id=715154552600526920&'
    'permissions=379969&scope=bot'
)
config = Config()


class Meta(commands.Cog):
    """Commands relating to the bot itself."""

    def __init__(self, bot):
        """Store the bot."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Set the help command cog to this one."""
        self.bot.help_command.cog = self    # pylint: disable=no-member

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Send prefix if bot is mentioned."""
        if message.guild.me in message.mentions:
            await message.channel.send(f'My prefix is `{config.prefix}`.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle an error."""
        await on_command_error(ctx, error)

    @commands.command(brief='About the bot.')
    async def about(self, ctx):    # noqa: ANN001
        """Get some information about the bot."""
        embed = discord.Embed(
            title='About',
            description=ABOUT.format(bot_name=self.bot.user.name),
            colour=0x45b3e0
        )
        embed.add_field(name='Invite', value=f'**[Click Here]({INVITE})**')
        embed.set_footer(
            text='artybot.xyz',
            icon_url='https://artybot.xyz/static/icon.png'
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Set the prefix.')
    @admin()
    async def prefix(self, ctx, prefix):    # noqa: ANN001
        """Set the command prefix."""
        config.prefix = prefix
        await ctx.send(f'Prefix is now `{prefix}`.')

    @commands.command(brief='Set announcement channel.')
    @admin()
    async def announcements(self, ctx, channel: discord.TextChannel):
        """Set the command prefix."""
        config.log_channel = channel
        await ctx.send(
            f'Announcements will now be made in {channel.mention}.'
        )

    @commands.command(
        brief='Add an admin user.',
        name='add-admin', aliases=['admin']
    )
    @commands.is_owner()
    async def addadmin(self, ctx, user: discord.Member):
        """Set a user as admin.

        Admins can do anything except add and remove admins.
        """
        admins = config.admins
        if (user.id not in (admin.id for admin in admins)):
            admins.append(user)
            config.admins = admins
            await ctx.send('Done!')
        else:
            await ctx.send(f'{user} is already an admin.')

    @commands.command(
        brief='Remove an admin user.', name='remove-admin',
        aliases=['unadmin']
    )
    @commands.is_owner()
    async def removeadmin(self, ctx, user: discord.Member):
        """Unset a user as admin."""
        admins = config.admins
        for admin in admins:
            if admin.id == user.id:
                admins.remove(admin)
                config.admins = admins
                await ctx.send('Done!')
                return
        await ctx.send(f'{user} is not an admin anyway.')
