BASE_URL = "https://api.martinebot.com/"

from datetime import datetime as dt
from typing import Any, Dict, Optional

import aiohttp
import discord
from discord.ext import tasks
from redbot.core import Config, commands
from redbot.core.bot import Red


class Memer(commands.Cog):
    """Get random memes from reddit."""

    __author__ = "Arman0334 (GhOsT#0231)"
    __version__ = "1.0.0"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config: Config = Config.get_conf(
            self, identifier=722168161713127435, force_registration=True
        )

        self.config.register_global(guilds=[])
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
        """Automatically posts memes to the set channel every 5 minutes."""
        all_guilds: list = await self.config.guilds()
        if not all_guilds:
            return

        for guild_id in all_guilds:
            guild: discord.Guild = self.bot.get_guild(guild_id)
            config: int = await self.config.guild(guild).channel()
            channel: discord.TextChannel = guild.get_channel(config)
            meme = await self.get_meme(channel=channel)
            if guild.me.permissions_in(channel).manage_webhooks:
                webhooks = await channel.webhooks()
                if not webhooks:
                    webhook = await channel.create_webhook(name="Memer")
                else:
                    usable_webhooks = [hook for hook in webhooks if hook.token]
                    # Usable webhook logic based on kato's onconnect cog
                    if not usable_webhooks:
                        webhook = await channel.create_webhook(name="Memer")
                    else:
                        webhook = usable_webhooks[0]

                await webhook.send(
                    username=self.bot.user.display_name,
                    avatar_url=self.bot.user.avatar_url,
                    embed=meme,
                )
            else:
                await channel.send(embed=meme)

    @autoposter.before_loop
    async def before_autoposter(self) -> None:
        """Wait for red to get ready."""
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
        self,
        ctx: commands.Context,
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        """Set the channel for auto posting memes.

        **Examples:**
        - `[p]memeset channel #testing`
        This will set the channel to #testing.
        - `[p]memeset channel 133251234164375552`
        This wil set the channel to #testing.

        **Arguments:**
        - `[channel]` - The channel to auto post memes to. Leave blank to use
        the current channel.
        """
        channel = channel or ctx.channel
        if not ctx.guild.me.permissions_in(channel).manage_webhooks:
            await ctx.reply(
                "I cannot send webhooks in {}!".format(channel.mention)
            )
        else:
            all_guilds_config: list = await self.config.guilds()
            if ctx.guild.id not in all_guilds_config:
                all_guilds_config.append(ctx.guild.id)
                await self.config.guilds.set(all_guilds_config)

            await self.config.guild(ctx.guild).channel.set(channel.id)
            await ctx.tick()

    @_memeset.command(name="clearchannel", aliases=["clear"])
    @commands.max_concurrency(number=1, per=commands.BucketType.guild)
    async def _clear_channel(self, ctx: commands.Context) -> None:
        """clear the channel for auto posting memes."""
        channel_config = await self.config.guild(ctx.guild).channel()
        if not channel_config:
            try:
                await ctx.reply("No channel has been set up to clear!")
            except discord.HTTPExecption:
                await ctx.send("No channel has been set up to clear!")
        else:
            all_guilds_config: list = await self.config.guilds()
            if ctx.guild.id in all_guilds_config:
                all_guilds_config.remove(ctx.guild.id)
                await self.config.guilds.set(all_guilds_config)

            await self.config.guild(ctx.guild).channel.clear()
            await ctx.tick()
