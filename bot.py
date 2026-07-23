import discord
from discord import app_commands
import os

TOKEN = os.environ.get("DISCORD_TOKEN", "YOUR_TOKEN_HERE")
USERNAME = "MainTreeUhh"
REPO = "FreeUGCLimited"

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Commands synced!")

    async def on_ready(self):
        print(f"Bot online as {self.user}")

bot = MyBot()

@bot.tree.command(name="raw", description="Get raw GitHub link")
@app_commands.describe(filename="Filename e.g. script.lua")
async def raw(interaction: discord.Interaction, filename: str):
    url = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/{filename}"
    await interaction.response.send_message(url)

bot.run(TOKEN)
