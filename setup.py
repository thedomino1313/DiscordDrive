# import os
from setuptools import setup

# print(os.curdir)
# with open('./discord_drive/requirements.txt') as f:
#     required = f.read().splitlines()
    
setup(
    name='discord_drive',
    version='0.0.5',
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
    ]
)