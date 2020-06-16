

async def end_game_command(
        ctx: Context, level: int, winner: sheetsapi.Player,
        loser1: sheetsapi.Player, loser2: sheetsapi.Player):
    """Command to mark a game as complete."""
    async with ctx.typing():
        sheetsapi.set_result(
            level, winner.discord_name, loser1.discord_name,
            loser2.discord_name
        )
    await ctx.send('Win recorded!')




