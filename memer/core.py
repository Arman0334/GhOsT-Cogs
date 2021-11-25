BASE_URL = "https://api.martinebot.com/"

import random
from datetime import datetime as dt
from typing import Any, Dict

import aiohttp
import discord
from discord.ext import tasks
from redbot.core import Config, commands
from redbot.core.bot import Red


class Memer(commands.Cog):
    """Get random memes from reddit."""

    __author__ = "Arman0334 (GhOsT#0231)"
    __version__ = "0.3.3"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config: Config = Config.get_conf(
            self, identifier=722168161713127435, force_registration=True
        )

        self.config.register_guild(channel=None)

        self.autoposter.start()

    def cog_unload(self) -> None:
        # Thanks MAX for telling me about cog-wide session
        self.bot.loop.create_task(self.autoposter.cancel())
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

    async def get_meme(self, channel: discord.TextChannel) -> discord.Embed:
        async with self.session.get(BASE_URL + "v1/images/memes") as resp:
            if resp.status != 200:
                embed = discord.Embed(
                    title="Error!",
                    description="Something went wrong while contacting the API",
                    colour=discord.Colour.red(),
                )
            else:
                data: dict = await resp.json()
                meme: dict = data.get("data")
                if meme.get("nsfw") is True and not channel.is_nsfw():
                    embed = discord.Embed(
                        title="Error!",
                        description=(
                            "This meme is marked as nsfw and this channel isnt"
                            " nsfw."
                        ),
                        colour=discord.Colour.red(),
                    )
                else:
                    embed = discord.Embed(
                        title=meme.get("title"),
                        url=meme.get("post_url"),
                        timestamp=dt.fromtimestamp(meme.get("created_at")),
                    )
                    embed.set_image(url=meme.get("image_url"))
                    embed.set_footer(
                        text="👍 {upvotes} | 💬 {comments}".format(
                            upvotes=meme.get("upvotes"),
                            comments=meme.get("comments"),
                        )
                    )

            return embed

    @tasks.loop(minutes=5)
    async def autoposter(self) -> None:
        """Automatically posts memes."""
        pass

    @autoposter.before_loop
    async def before_autoposter(self) -> None:
        """Wait for red to start up properly."""
        await self.bot.wait_until_red_ready()

    @commands.command(name="meme", aliases=["memes"])
    @commands.guild_only()
    async def _meme(self, ctx: commands.Context) -> None:
        """Shows some nice memes from reddit.

        Memes are taken from https://api.martinebot.com/.
        """
        meme = await self.get_meme(channel=ctx.channel)
        try:
            await ctx.reply(embed=meme, mention_author=False)
        except discord.HTTPException:
            await ctx.send(embed=meme)

    @commands.group(name="memeset")
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def _memeset(self, ctx: commands.Context) -> None:
        """Commands to manage autoposting memes."""

    @_memeset.command(name="channel")
    @commands.max_concurrency(number=1, per=commands.BucketType.guild)
    async def _channel(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> None:
        """Set the channel for auto posting memes."""
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await ctx.tick()

    @_memeset.command(name="clearchannel", aliases=["clear"])
    @commands.max_concurrency(number=1, per=commands.BucketType.guild)
    async def _clear_channel(self, ctx: commands.Context) -> None:
        """clear the channel for auto posting memes."""
        config = await self.config.guild(ctx.guild).channel()
        if not config:
            try:
                await ctx.reply("No channel has been set up to clear!")
            except discord.HTTPExecption:
                await ctx.send("No channel has been set up to clear!")
            return
        else:
            await self.config.guild(ctx.guild).channel.set(None)
            await ctx.tick()
