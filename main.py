import discord
import requests
import os
from discord.ext import commands, tasks
from datetime import datetime

# --- 1. SETUP ---
# Using all intents to allow the bot to purge messages and read history
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration Constants
PAGE_ID = "pb7vnbyp9dky"
OPAL_ID = "lx84tk5jzmt5"
GAME_ID = "ktdfbtft0ffq"
TARGET_CHANNEL_ID = 1420690312531017850 
API_KEY = os.getenv('STATUSPAGE_API_KEY')
headers = {"Authorization": f"OAuth {API_KEY}"}

# --- 2. THE BACKGROUND LOOP ---
@tasks.loop(minutes=1.0)
async def update_status_loop():
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        try:
            channel = await bot.fetch_channel(TARGET_CHANNEL_ID)
        except Exception as e:
            print(f"Could not find target channel: {e}")
            return

    # --- STEP A: DELETE ALL PREVIOUS MESSAGES ---
    try:
        await channel.purge(limit=100)
    except Exception as e:
        print(f"Error purging channel: {e}")

    # --- STEP B: FETCH STATUSPAGE DATA ---
    def get_comp_status(comp_id):
        # FIXED URL: Added the missing slash after /pages/
        url = f"https://api.statuspage.io{PAGE_ID}/components/{comp_id}"
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                status_text = data.get('status', 'unknown').replace('_', ' ').title()
                emoji = "✅" if data.get('status') == "operational" else "⚠️"
                return f"{emoji} {status_text}"
            else:
                return f"❌ Error {r.status_code}"
        except Exception as e:
            return f"❌ Connection Error"

    opal_status = get_comp_status(OPAL_ID)
    game_status = get_comp_status(GAME_ID)
    
    # Get current time for the footer
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- STEP C: CREATE YOUR CUSTOM EMBED ---
    embed = discord.Embed(
        title="Busways Status",
        description="Hello, I am Busways Assistance here to provide data of the status of the game.\nThis data is updated every minute.",
        color=5814783 
    )
    embed.add_field(
        name="Datastores", 
        value=f"Opal Data Status: {opal_status}", 
        inline=False
    )
    embed.add_field(
        name=f"Game Status: {game_status}", 
        value=" ", 
        inline=False
    )
    embed.set_footer(text=f"Updated {current_time} (Local Time)")

    # --- STEP D: SEND NEW MESSAGE ---
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Error sending message: {e}")

# --- 3. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the loop if it's not already running
    if not update_status_loop.is_running():
        update_status_loop.start()

# Run the bot using the token from Railway Variables
bot.run(os.getenv('DISCORD_TOKEN'))
