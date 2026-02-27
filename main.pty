import discord
import os
from discord.ext import commands

# Fetch token from Railway environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.run(TOKEN)
