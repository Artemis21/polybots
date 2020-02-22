from models.config import Config
from discord.ext import commands
import discord


class Settings(commands.Cog):
    '''Commands for editing bot settings.
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Set the prefix.')
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, new):
        '''Set the prefix for this bot.
        '''
        Config.prefix = new
        await ctx.send(f'Prefix set to `{new}`.')

    @commands.command(brief='Set the announcement channel.')
    @commands.has_permissions(manage_guild=True)
    async def announce(self, ctx, channel: discord.TextChannel):
        '''Set the channel for the bot to send announcments to.
        '''
        Config.announce = channel
        await ctx.send('Done!')

    @commands.command(brief='Set the notify role.')
    @commands.has_permissions(manage_guild=True)
    async def notify(self, ctx, role: discord.Role):
        '''Set the role for the bot to ping for announcments.
        '''
        Config.notify = role
        await ctx.send('Done!')

    @commands.command(brief='Set the server.', hidden=True)
    @commands.is_owner()
    async def server(self, ctx, server_id):
        '''Set the server for this bot.
        '''
        Config.guild = self.bot.get_guild(server_id)
        await ctx.send('Done!')

    @commands.command(brief='Set the game category.')
    @commands.has_permissions(manage_guild=True)
    async def category(self, ctx, category: discord.CategoryChannel):
        '''Set the category for game channels to be added to.
        '''
        Config.game_cat = category
        await ctx.send('Done!')

    @commands.command(brief='Add a point tier.')
    @commands.has_permissions(manage_guild=True)
    async def tier(self, ctx, points: int, role: discord.Role):
        '''Set a point tier.
        Examples:
        `{{pre}}tier 0 @Base tier`: Set the role @Base tier at 0 points.
        `{{pre}}tier 20 "Mid tier"`: Set the role @Mid tier at 20 points.
        '''
        Config.tiers[points] = role
        await ctx.send('Done!')

    @commands.command(brief='View point tiers.')
    async def tiers(self, ctx):
        '''View the point tiers.
        '''
        text = ''
        for points in Config.tiers:
            text += f'{points}: {Config.tiers[points].name}'
        await ctx.send(text or 'No tiers set.')

    @commands.command(brief='Remove a point tier.')
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx, role: discord.Role):
        '''Remove a point tier by role.
        '''
        apoints = None
        for points in Config.tiers:
            if Config.tiers[points].id == role.id:
                apoints = points
        if apoints == None:
            return await ctx.send('That role is not set a tier.')
        del Config.tiers[points]
        await ctx.send('Done!')
