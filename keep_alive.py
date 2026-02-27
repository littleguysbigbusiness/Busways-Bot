from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is awake!"

def run():
    # Render automatically provides a 'PORT' variable. 
    # If it's missing, it uses 10000 as a backup.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
