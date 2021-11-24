import json
from pathlib import Path

from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

from .core import Memer

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)


def setup(bot: Red) -> None:
    cog = Memer(bot)
    bot.add_cog(cog)
