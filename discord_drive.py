import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

class DiscordDrive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.slash_command(name="test", guild_ids=[os.getenv("DD_GUILD_ID")], description="Test me")
    async def test(self, ctx):
        await ctx.respond("Boom")
    