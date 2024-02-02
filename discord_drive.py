import discord
import os
import sys

from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from pprint import pprint
from typing import List

load_dotenv()

class Command:
    def __init__(self, str_, params: dict):
        self._str = str_
        self._params = params
        self._timestamp = datetime.now()

class DriveAPICommands(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.capacity = 15
        self._history = defaultdict(lambda: deque())
        
    def _save_to_history(self, id_, command: Command):
        if len(self._history[id_]) == self.capacity:
            self._history[id_].popleft()
            
        self._history[id_].append(command)
        # print(self._history[id_].pop()._str)
        # print(command._str, command._params)
    
    def _get_last_command(self, id_) -> Command:
        return self._history[id_].pop()
    
    def _get_last_commands(self, id_, n: int) -> List[Command]:
        
        if n > len(self._history[id_]):
            raise IndexError
        
        commands = []
        for _ in range(n):
            commands.append(self._get_last_command(id_))
        
        return commands

    # @with_call_order
    @commands.slash_command(name="upload", guild_ids=[os.getenv("DD_GUILD_ID")], description="Upload a file to your Google Drive")
    async def upload(self, ctx, share_link: str):
        
        locals_ = locals()

        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
        
        # print(locals_)
        await ctx.respond("File uploaded!")
        
    @commands.slash_command(name="getn", guild_ids=[os.getenv("DD_GUILD_ID")], description="Get last n commands")
    async def getn(self, ctx, n: int):
        locals_ = locals()
        
        try:
            commands = self._get_last_commands(ctx.author.id, int(n))
        except IndexError:
            await ctx.respond("Error retrieving commands")
            return
            
        
        for command in commands:
            pprint(f"{command._timestamp} - Command: {command._str}\nParams: {command._params}")
        
        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
        
        # print(locals_)
        await ctx.respond("Commands printed")