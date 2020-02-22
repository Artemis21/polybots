import discord
from discord.ext import commands
from utils.colours import colours
import datetime as dt


def list_perms(error):
    ps = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in
          error.missing_perms]
    return ', '.join(ps)


def get_error(error):
    errtype = 'Internal error'
    if isinstance(error, commands.ConversionError):
        try:
            print('ConversionError:', error)
        except Exception:
            pass
        return (
            errtype, 'One of the values you provided couldn\'t be processed.'
        )
    elif isinstance(error, commands.CommandInvokeError):
        try:
            print('CommandInvokeError:', error)
        except Exception:
            pass
        return errtype, 'There was an error running that command.'
    elif isinstance(error, commands.UserInputError):
        errtype = 'Bad values provided'
        if isinstance(error, commands.MissingRequiredArgument):
            return errtype, f'You must provide the {error.param.name} value.'
        elif isinstance(error, commands.TooManyArguments):
            return errtype, 'You provided too many values.'
        elif isinstance(error, commands.BadArgument):
            return errtype, 'You provided an invalid value.'
        elif isinstance(error, commands.BadUnionArgument):
            return errtype, f'You passed an invalid {error.param.name} value.'
        elif isinstance(error, commands.ArgumentParsingError):
            if isinstance(error, commands.UnexpectedQuoteError):
                return (
                    errtype,
                    f'You put a `{error.quote}` character where it shouldn\'t '
                    'be.'
                )
            elif isinstance(error, commands.InvalidEndOfQuotedStringError):
                return (
                    errtype,
                    f'You must put a space after a quoted value (instead '
                    'found `{error.char}`).'
                )
            elif isinstance(error, commands.ExpectedClosingQuoteError):
                return (
                    errtype,
                    f'You didn\'t add the end `{error.close_quote}` to a '
                    'quoted value.'
                )
            else:
                return errtype, 'You did something wrong with a quoted value.'
        else:
            return errtype, 'You provided values to the command incorrectly.'
    errtype = 'Command cannot be used'
    if isinstance(error, commands.CommandNotFound):
        return errtype, 'That command was not found.'
    elif isinstance(error, commands.DisabledCommand):
        return errtype, 'This command is currently disabled.'
    elif isinstance(error, commands.CommandOnCooldown):
        return (
            errtype,
            'Slow down! You may use this command again in'
            f'{dt.timedelta(seconds=int(error.retry_after))}.'
        )
    elif isinstance(error, commands.CheckFailure):
        if isinstance(error, commands.PrivateMessageOnly):
            return errtype, 'This command may only be used in DMs.'
        elif isinstance(error, commands.NoPrivateMessage):
            return errtype, 'This command may not be used in DMs.'
        elif isinstance(error, commands.NotOwner):
            return errtype, 'This command may only be used by the bot owner.'
        elif isinstance(error, commands.MissingPermissions):
            return (
                errtype,
                'You must have the following permission\s to run this command:'
                f'{list_perms(error)}.'
            )
        elif isinstance(error, commands.BotMissingPermissions):
            return (
                errtype,
                'The bot must have the following permission\s to run this '
                f'command: {list_perms(error)}.'
            )
        elif isinstance(error, commands.MissingRole):
            return (
                errtype,
                f'You must have the `{error.missing_role}` role to run this '
                'command.'
            )
        elif isinstance(error, commands.BotMissingRole):
            return (
                errtype,
                f'The bot must have the `{error.missing_role}` role to run '
                'this command.'
            )
        elif isinstance(error, commands.MissingAnyRole):
            return (
                errtype,
                'You must have one of the following roles to run this '
                f'command: `{", ".join(error.missing_roles)}`.'
            )
        elif isinstance(error, commands.BotMissingAnyRole):
            return (
                errtype,
                f'The bot must have one of the following roles to run this '
                f'command: `{", ".join(error.missing_roles)}`.'
            )
        elif isinstance(error, commands.NSFWChannelRequired):
            return errtype, 'This command may only be run in an NSFW channel.'
        else:
            return errtype, 'This command can\'t be run here and now.'
    else:
        print(error)
        return 'Unknown', 'Something went wrong. That\'s all we know.'


async def handle(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        return
    title, desc = get_error(error)
    desc += (
        f'** ({error})'
        f'\n\nUse `{ctx.prefix}help [command]` for more information on how to '
        'use a command.'
    )
    desc = '**' + desc
    title = 'Error: ' + title
    embed = discord.Embed(colour=colours['red'], description=desc)
    embed.set_author(name=title, icon_url=ctx.bot.user.avatar_url)
    await ctx.send(embed=embed)
