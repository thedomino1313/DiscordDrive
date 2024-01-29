# DiscordDrive

## Description:
We aim to create a Python library that can manage a Google Drive file system through a set of Discord bot commands. These commands will be loaded as a “Cog”, which is a collection of commands that can be added to an existing Discord bot. The bot will be able to manage a file system, including creating new directories and adding and retrieving files. This adds a level of privacy to a Google Drive folder, eliminating security risks of users with access deleting files. Admins will import our library, add the Cog to their personal Discord bot, and use their personal Google account and OAuth token to interface with the Google Drive API.

## Stack:
Python

## Goals:
Interface with the Google Drive API using any user’s OAuth token
Generate an initial file structure or link to an existing one
Want to be able to upload files/folders to Google Drive
Want to be able to retrieve files/folders from Google Drive
Support some “root” directory

## Milestones:
February:
- Generate basic Cog structure and flesh out the commands and their functionality
- Get bot to interface with the Google Drive API
    - OAuth token received as input argument

March:
- Build API functionality
  - Search for files
  - Upload files
  - Retrieve files
- Build command library on the Discord end
    - Interface with individual users and allow for parallel commands
- Connect the Drive API and Discord Cog library together to make the final product

April:
- Package code and publish to PyPI!


## Team:
Ryan Karch (karchr) - Official Project Lead

Dominic Beyer (beyerd) - Co-Project Lead