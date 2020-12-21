"""Commands to view and search for rules."""
import typing

import discord
from discord.ext import commands

from tools import menus, rules


class Rules(commands.Cog):
    """Commands to view and search for rules."""

    def __init__(self, bot: commands.Bot):
        """Store a reference to the bot."""
        self.bot = bot

    @commands.command(brief='Get a rule by number.')
    async def rule(self, ctx: commands.Context, number: str):
        """Get a rule by its number.

        Example: `{{pre}}rule 5.2`
        """
        if rules.rule_exists(number):
            await self.display_rule(number, channel=ctx, user=ctx.author)
        else:
            await ctx.send(f'Could not find rule "{number}".')

    @commands.command(brief='See all rules.')
    async def rules(self,
            ctx: commands.Context, *, category: typing.Optional[str]):
        """Get a list of all the rule categories, or the rules in a category.

        Examples:
        `{{pre}}rules`
        `{{pre}}rules 5`
        `{{pre}}rules submitting results`
        """
        if not category:
            await self.full_rule_list(channel=ctx, user=ctx.author)
        else:
            if (category_id := rules.get_category(category)):
                await self.category_index(
                    category_id, channel=ctx, user=ctx.author
                )
            else:
                await ctx.send(f'Could not find rule category "{category}".')

    async def full_rule_list(self, **menu_options: dict[str, typing.Any]):
        """Send a list of all rules."""
        options = rules.get_all_categories_index()
        await menus.Menu(
            client=self.bot,
            title='Giants League Rules',
            options=options,
            callback=self.on_category_select,
            show_emojis=False,
            **menu_options
        ).send()

    async def on_category_select(self, event: menus.MenuEvent):
        """Display a category selected by menu."""
        event.menu.stop_listening()
        await self.category_index(
            event.option, message=event.menu.message, user=event.user
        )

    async def category_index(self,
            category_id: str, **menu_options: dict[str, typing.Any]):
        """Display a category selected by command or menu."""
        title = rules.get_all_categories_index()[category_id]
        options = rules.get_category_index(category_id)
        options['back'] = '◀️ Back'
        emojis = list(menus.NUMBER_EMOJIS)
        emojis[len(options) - 1] = '◀️'
        await menus.Menu(
            client=self.bot,
            title=title,
            options=options,
            callback=self.on_rule_select,
            show_emojis=False,
            emojis=emojis,
            **menu_options
        ).send()

    async def on_rule_select(self, event: menus.MenuEvent):
        """Display a selected rule."""
        event.menu.stop_listening()
        if event.option == 'back':
            await self.full_rule_list(
                message=event.menu.message, user=event.user
            )
            return
        await self.display_rule(
            event.option, message=event.menu.message, user=event.user
        )

    async def display_rule(self,
            rule_id: str, **menu_options: dict[str, typing.Any]):
        """Display a rule selected by command or menu."""
        options = {rule_id.split('.')[0]: rules.get_rule(rule_id)}
        await menus.Menu(
            client=self.bot,
            title=rule_id,
            options=options,
            callback=self.on_rule_back,
            show_emojis=False,
            emojis=['◀️'],
            **menu_options
        ).send()


    async def on_rule_back(self, event: menus.MenuEvent):
        """Go back to a category index."""
        event.menu.stop_listening()
        await self.category_index(
            event.option, message=event.menu.message, user=event.user
        )
