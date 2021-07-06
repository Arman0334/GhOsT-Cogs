import aiohttp
import random

import discord
from redbot.core import commands
from redbot.core.bot import Red


class Fun(commands.Cog):
    """
    Some fun commandss...
    """

    __version__ = "0.0.1"

    def format_help_for_context(self, ctx: commands.Context):
        """
        Thanks Sinbad!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot: Red) -> None:
        self.bot = bot

    async def red_get_data_for_user(self, *, user_id: int):
        """
        This cog does not story any end user data.
        """
        return {}

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete.
        """
        return

    @commands.command(aliases=["memes"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx: commands.Context):
        """Shows some memes from reddit."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.reddit.com/r/memes/new.json?sort=hot"
            ) as resp:
                data = await resp.json()
                data = data["data"]
                children = data["children"]
                post = random.choice(children)["data"]
                title = post["title"]
                url = post["url_overridden_by_dest"]

        embed = discord.Embed(title=title).set_image(url=url)
        await session.close()
        await ctx.send(embed=embed)
