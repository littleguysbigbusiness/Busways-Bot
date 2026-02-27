import discord
import requests
import os
from discord.ext import commands, tasks
from datetime import datetime

# --- 1. SETUP ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration Constants
PAGE_ID = "pb7vnbyp9dky"
OPAL_ID = "lx84tk5jzmt5"
GAME_ID = "ktdfbtft0ffq"
# Updated IDs from your new link
TARGET_CHANNEL_ID = 1420690312531017850 
TARGET_MESSAGE_ID = 1476842017886572648 

API_KEY = os.getenv('STATUSPAGE_API_KEY')
headers = {"Authorization": f"OAuth {API_KEY}"}

# --- 2. THE BACKGROUND LOOP ---
@tasks.loop(minutes=1.0)
async def update_status_loop():
    try:
        # Fetch the specific channel and message
        channel = bot.get_channel(TARGET_CHANNEL_ID) or await bot.fetch_channel(TARGET_CHANNEL_ID)
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        
        # Helper function to get status from API
        def get_comp_status(comp_id):
            url = f"https://api.statuspage.io{PAGE_ID}/components/{comp_id}"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    status_text = data.get('status', 'unknown').replace('_', ' ').title()
                    emoji = "✅" if data.get('status') == "operational" else "⚠️"
                    return f"{emoji} {status_text}"
                else:
                    # Logs the specific error code if the API key or ID is wrong
                    print(f"API Error for {comp_id}: Status {r.status_code}")
                    return f"❌ Connection Error ({r.status_code})"
            except Exception as e:
                print(f"Network Error for {comp_id}: {e}")
                return "❌ Connection Error"

        opal_status = get_comp_status(OPAL_ID)
        game_status = get_comp_status(GAME_ID)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create your custom embed
        embed = discord.Embed(
            title="Busways Status",
            description="Hello, I am Busways Assistance here to provide data of the status of the game.\nThis data is updated every minute.",
            color=5814783 
        )
        embed.add_field(name="Datastores", value=f"Opal Data Status: {opal_status}", inline=False)
        embed.add_field(name=f"Game Status: {game_status}", value=" ", inline=False)
        embed.set_footer(text=f"Updated {current_time} (Local Time)")

        # EDIT the existing message
        await message.edit(embed=embed)
        print(f"Successfully updated status at {current_time}")

    except Exception as e:
        print(f"Error in update loop: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not update_status_loop.is_running():
        update_status_loop.start()

bot.run(os.getenv('DISCORD_TOKEN'))
