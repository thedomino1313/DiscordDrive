# import os
from setuptools import setup

description = """
## Usage:
1. Install the library:
   ```
   pip install discord-drive
   ```
2. Follow the official [Google Drive Developer quick-start instructions](https://developers.google.com/drive/api/quickstart/python) to generate your credentials file.
3. Save the credentials file as `credentials.json` in the running directory of your Discord bot.
4. Open Google Drive, go to the directory that you want to root the bot to, and get the link.
   - It should be of format: `https://drive.google.com/drive/folders/folder_id`
5. Create a Discord bot using Pycord, and add the DiscordDrive command suite to it with the following code:
   ```python
   from discord_drive import DriveAPICommands
   bot.add_cog(DriveAPICommands(bot, "<link from step 5>"))
   ```
6. Run the bot, and use `/authenticate` to ensure that DiscordDrive is authorized to access your Google Account.

## Commands:
`/authenticate`: Regenerates the token needed to enable the API. If re-authentication is needed, the bot will DM the caller a link and wait for the authentication code given to the caller by Google\\
`/cd <directory>`: Navigates the caller down into a child directory of their current directory. Autocomplete is provided for hints.\\
`/download <file> <timeout (optional)> <public (optional)>`: Gives the user the file (or a link) to download the file specified. Files have autocomplete. Timeout defaults to 60 seconds, where the file will then no longer be allowed to be downloaded. Public defaults to False, where no other users can see the file.\\
`/ls`: Shows the caller the contents of their current directory.\\
`/pwd`: Shows the caller the file path of their current directory.\\
`/share <file> <user> <timeout (optional)>`: Sends a specified server member a dm with a file from the caller's current directory. Files and users have autocomplete. Timeout defaults to 60 seconds, where the file will then no longer be allowed to be downloaded.\\
`/upload <attachment>`: Uploads a file or zip file to the caller's current directory. Zip files must contain just the files, and no folders, as they will not be read.
"""

setup(
    name='discord_drive',
    version='0.0.6',
    description='Use Google Drive via Discord!',
    license='MIT',
    packages=['discord_drive'],
    author='Ryan Karch, Dominic Beyer',
    author_email='',
    keywords=['Discord', 'Google Drive'],
    url='https://github.com/thedomino1313/DiscordDrive',
    install_requires=[
        'py-cord',
        'google_api_python_client',
        'google_auth_oauthlib',
        'numpy',
        'opencv_python',
        'opencv_python_headless',
        'protobuf',
        'python-dotenv'
    ],
    long_description=description,
    long_description_content_type='text/markdown'
)