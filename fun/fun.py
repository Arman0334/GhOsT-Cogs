import random
from typing import Optional

import aiohttp
import discord
from redbot.core import Config, commands
from redbot.core.bot import Red


class Fun(commands.Cog):
    """
    Some fun commands...
    """

    __version__ = "0.2.3"

    def format_help_for_context(self, ctx: commands.Context):
        """
        Thanks Sinbad!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config = Config.get_conf(
            self,
            identifier=722168161713127435,
            force_registration=True,
        )
        default_guild = {"subreddit": "r/memes"}
        self.config.register_guild(**default_guild)

    def cog_unload(self):  # Thanks MAX
        self.bot.loop.create_task(self.session.close())

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

    @commands.command(name="meme", aliases=["memes"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def _meme(self, ctx: commands.Context):
        """Shows some quality memes from reddit."""
        subreddit = await self.config.guild(ctx.guild).subreddit()
        async with self.session.get(
            f"https://www.reddit.com/{subreddit}/top.json?sort=new"
        ) as resp:
            data = await resp.json()
            data = data["data"]
            children = data["children"]
            post = random.choice(children)["data"]
            title = post["title"]
            url = post["url_overridden_by_dest"]
            link_url = f'https://reddit.com{post["permalink"]}'
            ups = post["ups"]
            comnts = post["num_comments"]

        if post["over_18"] is True:
            return await ctx.send(
                "Cannot show content because it is nsfw,"
                " try changing the subreddit lol."
            )

        embed = (
            discord.Embed(title=title, url=link_url)
            .set_image(url=url)
            .set_footer(text="👍 {} | 💬 {}".format(ups, comnts))
        )
        await ctx.send(embed=embed)

    @commands.group(name="memeset")
    @commands.guild_only()
    @commands.admin()
    async def _memeset(self, ctx: commands.Context):
        """Base command for managing meme stuff."""

    @_memeset.command(name="subreddit", aliases=["sub"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def _subreddit(
        self, ctx: commands.Context, *, subreddit: Optional[str]
    ):
        """Set the subreddit for the meme command.

        Default subreddit is [r/memes](https://reddit.com/r/memes).

        Examples:
        - `[p]memeset subreddit r/memes`
        This will set the subreddit to r/memes.
        - `[p]memeset subreddit r/dankmemes`
        This will set the subreddit to r/dankmemes.

        Arguments:
        - `<subreddit>` The name of the subreddit to be used. Only
        enter the subreddit name, don't enter the full url or shit
        might break.
        """
        if subreddit is None:
            await self.config.guild(ctx.guild).subreddit.set(
                "r/memes"
            )
            return await ctx.send("Subreddit reset.")

        await self.config.guild(ctx.guild).subreddit.set(subreddit)
        await ctx.send(
            "The subreddit has sucessfully set to `{}`".format(
                subreddit
            )
        )


# This cog doesn't have much in it yet, but autoposting memes
# are one of the things that I plan to add in the near future.
