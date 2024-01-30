import os
import sys

from collections import defaultdict, deque
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

class DriveAPICommands(commands.Cog):
    
    # @store_history
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._history = defaultdict(lambda: deque())
        
    def _save_to_history(self, id_):
        self._history[id_].appendleft(sys._getframe(1).f_code.co_name)
        # print(id_, self._history[id_])

    @commands.slash_command(name="test", guild_ids=[os.getenv("DD_GUILD_ID")], description="Test me")
    async def test(self, ctx):
        self._save_to_history(ctx.author.id)
        await ctx.respond("Boom")
        
    @commands.slash_command(name="test2", guild_ids=[os.getenv("DD_GUILD_ID")], description="Test me")
    async def test2(self, ctx):
        self._save_to_history(ctx.author.id)
        await ctx.respond("Boom!")    
    
        
    # @commands.slash_command(name="")
    