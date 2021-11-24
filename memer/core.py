BASE_URL = "https://api.martinebot.com/"

import random
from datetime import datetime as dt
from typing import Any, Dict

import aiohttp
import discord
from redbot.core import commands
from redbot.core.bot import Red


class Memer(commands.Cog):
    """Get random memes from reddit."""

    __author__ = "Arman0334 (GhOsT#0231)"
    __version__ = "0.3.2"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self) -> None:
        # Thanks MAX for telling me about this
        self.bot.loop.create_task(self.session.close())

    def format_help_for_context(self, ctx: commands.Context) -> str:
        # Thanks Sinbad!
        pre = super().format_help_for_context(ctx)
        return (
            f"{pre}\n\nAuthor: {self.__author__}\nVersion: {self.__version__}"
        )

    async def red_get_data_for_user(self, *, user_id: int) -> dict:
        # This cog does not story any end user data.
        return {}

    async def red_delete_data_for_user(self, **kwargs: Dict[str, Any]) -> None:
        # Nothing to delete.
        return

    @commands.command(name="meme", aliases=["memes"])
    @commands.guild_only()
    async def _meme(self, ctx: commands.Context) -> None:
        """Shows some nice memes from reddit.

        Memes are taken from https://api.martinebot.com/.
        """
        async with self.session.get(BASE_URL + "v1/images/memes") as resp:
            if resp.status != 200:
                await ctx.reply(
                    (
                        "Something went wrong while contacting the API! Error "
                        "Code: {}"
                    ).format(resp.status)
                )
                return
            else:
                data = await resp.json()
                meme = data.get("data")
                nsfw = meme.get("nsfw")
                if nsfw and not ctx.channel.is_nsfw():
                    await ctx.reply(
                        (
                            "I couldn't send the meme because it contains NSFW"
                            " content and this channel is not marked as NSFW."
                        )
                    )
                    return
                else:
                    embed = discord.Embed(
                        title=meme.get("title"),
                        url=meme.get("post_url"),
                        timestamp=dt.fromtimestamp(meme.get("created_at")),
                    )
                    embed.set_image(url=meme.get("image_url"))
                    embed.set_footer(
                        text="👍 {upvotes} 👎 {downvotes} 💬 {comments}".format(
                            upvotes=meme.get("upvotes"),
                            downvotes=meme.get("downvotes"),
                            comments=meme.get("comments"),
                        )
                    )

                await ctx.send(embed=embed)
