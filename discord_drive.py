import discord
import os
import pathlib
import sys

from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
from discord.ext.commands import has_permissions, MissingPermissions
from pprint import pprint
from typing import List, Iterable


from drive import DriveAPI

load_dotenv()

class Command:
    def __init__(self, str_, params: dict):
        self._str = str_
        self._params = params
        self._timestamp = datetime.now()

class DriveAPICommands(discord.ext.commands.Cog):
    
    def __init__(self, bot: discord.ext.commands.Bot, root: str):
        self.bot = bot
        self.root = root
        self.API = DriveAPI(root)
        # self.root_alias = '~'
        self.capacity = 15
        self._command_history = defaultdict(lambda: deque())
        self._wd_cache = defaultdict(lambda: [pathlib.Path(self.root), pathlib.Path(self.root)])
        
    async def _API_ready(self, ctx: discord.ApplicationContext):
        if not (result := bool(self.API.service)):
            await ctx.respond("Please use `/authenticate` to validate your Google Account's credentials before using any commands!")
        return result

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

    # @discord.ext.commands.Cog.listener()
    async def cog_command_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.respond("You are missing permission(s) to run this command.")
        else:
            raise error

    # @with_call_order
    @discord.ext.commands.slash_command(name="upload", guild_ids=[os.getenv("DD_GUILD_ID")], description="Upload a file to your Google Drive")
    async def upload(self, ctx: discord.ApplicationContext, file: discord.Attachment):

        if not await self._API_ready(ctx):
            return
        
        await ctx.defer()
        
        locals_ = locals()
        name = await self.API.upload_from_discord(file=file, folder=self._wd_cache[ctx.author.id][0].name)
        if name:
            await ctx.respond(name)
        else:
            return
        
        
        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
    
    @discord.ext.commands.slash_command(name="pwd", guild_ids=[os.getenv("DD_GUILD_ID")], description="Print your current working directory")
    async def pwd(self, ctx):

        if not await self._API_ready(ctx):
            return
        
        # locals_ = locals()

        # self._save_to_history(
        #     id_=ctx.author.id,
        #     command=Command(
        #         str_=sys._getframe(0).f_code.co_name,
        #         params=locals_
        #     )
        # )
        
        await ctx.respond(f"{self._wd_cache[ctx.author.id][0]}")
    
    @discord.ext.commands.slash_command(name="cd", guild_ids=[os.getenv("DD_GUILD_ID")], description="Change your current working directory")
    async def cd(self, ctx: discord.ApplicationContext, path=""):

        if not await self._API_ready(ctx):
            return
        

        locals_ = locals()
        last_path = self._wd_cache[ctx.author.id][0]
        self._wd_cache[ctx.author.id][1] = last_path
        
        if path == "" or path == '~':
            # last_path = self._wd_cache[ctx.author.id]
            self._wd_cache[ctx.author.id][0] = pathlib.Path(self.root) 
            # self._wd_cache[ctx.author.id][1] = last_path
        
        elif path == '.':
            # say something like path not changed
            return
        
        elif path == "..":
            cwd = self._wd_cache[ctx.author.id][0]
            if cwd != pathlib.Path(self.root):
                self._wd_cache[ctx.author.id][0] = cwd.parent # get first ancestor
            else:
                await ctx.respond(f"You are in the root directory.")
                
        elif path == '-':
            self._wd_cache[ctx.author.id][0] = self._wd_cache[ctx.author.id][1]

        else:
            
            folder = self.API.search(name=path, parent=self._wd_cache[ctx.author.id][0].name, files=False)
            # await ctx.respond(f"{folder}")
            
            if not folder:
                await ctx.respond(f"{path} is not reachable from your current directory.")
                return

            path = folder[0]["name"]
            self._wd_cache[ctx.author.id][0] /= path

        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
        
        await ctx.respond(f"Directory changed to `{self._wd_cache[ctx.author.id][0]}`")
        
    @discord.ext.commands.slash_command(name="ls", guild_ids=[os.getenv("DD_GUILD_ID")], description="List all files in your current working directory")
    async def ls(self, ctx):

        if not await self._API_ready(ctx):
            return
        
        locals_ = locals()
        
        folder_type_mapping = {
            True: chr(128193),
            False: chr(128196)
        }
        
        await ctx.respond('\n'.join([f"{folder_type_mapping[file['mimeType'].startswith(self.API.FOLDER_TYPE)]} {file['name']}" for file in self.API.search(parent=self._wd_cache[ctx.author.id][0].name, files=True, pageSize=100, recursive=True)]))
        # for file in self.API.search(parent=self._wd_cache[ctx.author.id][0].name, files=True, pageSize=100, recursive=True):
        #     await ctx.respond(file)
        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
    
    @discord.ext.commands.slash_command(name="export", guild_ids=[os.getenv("DD_GUILD_ID")], description="Download a file from your current working directory")
    async def export(self, ctx: discord.ApplicationContext, name: str):

        if not await self._API_ready(ctx):
            return
        
        await ctx.defer()

        file = self.API.export(name=name, folder=self._wd_cache[ctx.author.id][0].name)

        if isinstance(file, str):
            await ctx.respond(file)
        else:
            await ctx.respond(file=file)
        
    
    @discord.ext.commands.slash_command(name="mkdir", guild_ids=[os.getenv("DD_GUILD_ID")], description="Make a new folder in your current working directory")
    @has_permissions(administrator=True)
    async def mkdir(self, ctx: discord.ApplicationContext, folder_name):

        if not await self._API_ready(ctx):
            return
        
        locals_ = locals()
        success = self.API.make_folder(name=folder_name, folder=self._wd_cache[ctx.author.id][0].name)
        
        if success:
            await ctx.respond(f"Folder {folder_name} created at {self._wd_cache[ctx.author.id][0]}/{folder_name}")
        else:
            await ctx.respond("Could not create folder.")
            
        self._save_to_history(
            id_=ctx.author.id,
            command=Command(
                str_=sys._getframe(0).f_code.co_name,
                params=locals_
            )
        )
    
    
    @discord.ext.commands.slash_command(name="authenticate", guild_ids=[os.getenv("DD_GUILD_ID")], description="Authenticate your google account")
    @has_permissions(administrator=True)
    async def authenticate(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await self.API.authenticate(ctx, self.bot)
        
    @discord.ext.commands.slash_command(name="getn", guild_ids=[os.getenv("DD_GUILD_ID")], description="DEBUG: Get last n commands")
    @has_permissions(administrator=True)
    async def getn(self, ctx: discord.ApplicationContext, n: int):

        if not await self._API_ready(ctx):
            return
        
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