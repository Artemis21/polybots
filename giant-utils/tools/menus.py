"""A Discord.py utility for reaction-based menus.

This is not suitable for permanent menus (eg. reaction roles) because it
only works while the original message is in the menu cache.
"""
from collections import namedtuple
import typing

import discord


MenuEvent = namedtuple('MenuEvent', ['user', 'option', 'menu'])
NUMBER_EMOJIS = [
    *(f'{n}\N{COMBINING ENCLOSING KEYCAP}' for n in range(1, 10)), '🔟'
]


class Menu():
    """A reaction-based menu."""

    def __init__(self,
            client: discord.Client, title: str,
            callback: typing.Coroutine,
            options: dict[typing.Any, str],
            channel: typing.Optional[discord.abc.Messageable] = None,
            message: typing.Optional[discord.Message] = None,
            show_emojis: bool = True,
            user: typing.Optional[discord.User] = None,
            emojis: typing.Optional[list[str]] = None):
        """Create a new menu.

        If `message` is provided, the menu will re-use that message by editing
        it. Otherwise, it will send a new message to `channel`.

        The values of `options` will be displayed to the user, the keys will
        be used in the callback.

        If `user` is provided, only reactions from that user will be accepted.

        `show_emojis` determines whether emojis will be shown alongside each
        option, or just added as reactions. `emojis` specifies the emojis to
        use (it should be at least as long as `options`). It defaults to the
        emojis 1️⃣ to 🔟.
        """
        client.add_listener(self.on_reaction_add)
        self.callback = callback
        self.client = client
        self.channel = channel
        self.message = message
        self.user = user
        self.option_ids = list(options)
        self.emojis = (emojis or NUMBER_EMOJIS)[:len(options)]
        self.embed = discord.Embed(title=title, description='\n'.join(
            '{emoji} {description}'.format(
                emoji=(f'{emoji} ' if show_emojis else ''),
                description=description
            ) for emoji, description in zip(self.emojis, options.values())
        ))

    async def send(self):
        """Send the menu so that it can be used."""
        if self.message:
            await self.message.edit(embed=self.embed)
            await self.ensure_correct_reactions()
        else:
            self.message = await self.channel.send(embed=self.embed)
            for emoji in self.emojis:
                await self.message.add_reaction(emoji)

    async def ensure_correct_reactions(self):
        """Find the shortest way to switch to some set of reactions."""
        self.message = await self.message.channel.fetch_message(
            self.message.id)
        current = {i.emoji for i in self.message.reactions if i.me}
        target = set(self.emojis)
        to_remove = current - target
        to_add = target - current
        if len(target) < len(to_remove):
            await self.message.clear_reactions()
            for emoji in self.emojis:
                await self.message.add_reaction(emoji)
            return
        for emoji in to_remove:
            await self.message.clear_reaction(emoji)
        for reaction in self.message.reactions:
            if reaction.emoji in self.emojis:
                async for user in reaction.users():
                    if user == self.user or not self.user:
                        await reaction.remove(user)
        for emoji in sorted(to_add):
            await self.message.add_reaction(emoji)

    async def on_reaction_add(self,
            reaction: discord.Reaction, user: discord.User):
        """Process a reaction being added."""
        if self.user and user != self.user:
            return
        if reaction.message != self.message:
            return
        if reaction.emoji not in self.emojis:
            return
        index = self.emojis.index(reaction.emoji)
        option = self.option_ids[index]
        await self.callback(MenuEvent(user, option, self))

    def stop_listening(self):
        """Stop listening for the menu being used."""
        self.client.remove_listener(self.on_reaction_add)
