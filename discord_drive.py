import discord
import os
import pathlib
import sys

from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from pprint import pprint
from typing import List


from drive import DriveAPI

load_dotenv()

class Command:
    def __init__(self, str_, params: dict):
        self._str = str_
        self._params = params
        self._timestamp = datetime.now()

class DriveAPICommands(commands.Cog):
    
    def __init__(self, bot: commands.Bot, root: str):
        self.bot = bot
        self.root = root
        self.API = DriveAPI(root)
        # self.root_alias = '~'
        self.capacity = 15
        self._command_history = defaultdict(lambda: deque())
        self._wd_cache = defaultdict(lambda: pathlib.Path(self.root))
        
    def _save_to_history(self, id_, command: Command):
        if len(self._command_history[id_]) == self.capacity:
            self._command_history[id_].popleft()
            
        self._command_history[id_].append(command)
        # print(self._history[id_].pop()._str)
        # print(command._str, command._params)
    
    def _get_last_command(self, id_) -> Command:
        return self._command_history[id_].pop()
    
    def _get_last_commands(self, id_, n: int) -> List[Command]:
        
        if n > len(self._command_history[id_]):
            raise IndexError
        
        commands = []
        for _ in range(n):
            commands.append(self._get_last_command(id_))
        
        return commands

    # @with_call_order
    @commands.slash_command(name="upload", guild_ids=[os.getenv("DD_GUILD_ID")], description="Upload a file to your Google Drive")
    async def upload(self, ctx: commands.Context, file: discord.Attachment):
        
        locals_ = locals()

        name = await self.API.upload_from_discord(file)
        if name:
            await ctx.respond(f"File {name} uploaded!")
        else:
            return
        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
    
    @commands.slash_command(name="pwd", guild_ids=[os.getenv("DD_GUILD_ID")], description="Print your current working directory")
    async def pwd(self, ctx):
        locals_ = locals()

        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
        
        await ctx.respond(f"{self._wd_cache[ctx.author.id]}")
    
    @commands.slash_command(name="cd", guild_ids=[os.getenv("DD_GUILD_ID")], description="Change your current working directory")
    async def cd(self, ctx: commands.Context, path=""):
            
        
        """
        
        cases:

            In directory D... can always CD when given path starting with root
            
            SAME DIRECTORY
            In directory D, user supplies absolute path to D
                            user supplies alternate relative path to D
                            
            DIFFERENT DIRECTORY
            In directory X, user supplies valid RELATIVE path to D
                            user supplies valid ABSOLUTE path that starts at root
                            
            ..
            Go up one level
            
            .
            Refers to current directory
            
            ~
            Root alias
            
            Unix, Unix-like
            cd by itself or cd ~ will always put the user in their home directory.
            cd . will leave the user in the same directory they are currently in (i.e. the current directory won't change). This can be useful if the user's shell's internal code can't deal with the directory they are in being recreated; running cd . will place their shell in the recreated directory.
            X cd ~username will put the user in the username's home directory.
            cd dir (without a /) will put the user in a subdirectory; for example, if they are in /usr, typing cd bin will put them in /usr/bin, while cd /bin puts them in /bin.
            cd .. will move the user up one directory. So, if they are /usr/bin/tmp, cd .. moves them to /usr/bin, while cd ../.. moves them to /usr (i.e. up two levels). The user can use this indirection to access subdirectories too. So, from /usr/bin/tmp, they can use cd ../../local to go to /usr/local
            cd - will switch the user to the previous directory. For example, if they are in /usr/bin/tmp, and go to /etc, they can type cd - to go back to /usr/bin/tmp. The user can use this to toggle back and forth between two directories without pushd and popd.

            
        
        
        
        
        
        
        
        """
        # locals_ = locals()

        
        # if path does contain contents of WD
        # example: WD: /root/ CD: /root/branch -> WD: /root/branch
        # if path in user_wd:
        #     end_path = user_wd.find(path) + len(path)
        # do some verification that the folder path is accessible from the current working directory
        # do some regex to match first part of folder path -- and only append last part to pwd
        # self.wd_cache[ctx.author.id] = f"{user_wd}{}"
        locals_ = locals()
        
        if path == "" or path == '~':
            self._wd_cache[ctx.author.id] = pathlib.Path(self.root)
        
        elif path == '.':
            # say something like path not changed
            return
        
        elif path == "..":
            cwd = self._wd_cache[ctx.author.id]
            if cwd != pathlib.Path(self.root):
                self._wd_cache[ctx.author.id] = cwd.parent # get first ancestor
            else:
                await ctx.respond(f"You are in the root directory.")

        else:
            
            folder = self.API.search(name=path, parent=self._wd_cache[ctx.author.id].name, files=False)
            await ctx.respond(f"{folder}")
            
            if not folder:
                await ctx.respond(f"{path} is not reachable from your current directory.")
                return

            path = folder[0]["name"]
            self._wd_cache[ctx.author.id] /= path

        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
        
        await ctx.respond(f"Directory changed")
        
    @commands.slash_command(name="ls", guild_ids=[os.getenv("DD_GUILD_ID")], description="List all files in your current working directory")
    async def ls(self, ctx):
        pass
    
    @commands.slash_command(name="mkdir", guild_ids=[os.getenv("DD_GUILD_ID")], description="Make a new folder in your current working directory")
    async def mkdir(self, ctx: commands.Context, folder_name):
        pass
        
    @commands.slash_command(name="getn", guild_ids=[os.getenv("DD_GUILD_ID")], description="DEBUG: Get last n commands")
    async def getn(self, ctx: commands.Context, n: int):
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