from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()
    
setup(
    name='discord_drive',
    version='0.0.1',
    description='Use Google Drive via Discord!',
    license='MIT',
    packages=['discord_drive'],
    author='Ryan Karch, Dominic Beyer',
    author_email='',
    keywords=['Discord', 'Google Drive'],
    url='https://github.com/thedomino1313/DiscordDrive',
    install_requires=required
)