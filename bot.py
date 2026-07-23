import discord
from discord import app_commands
import os, base64, requests, aiohttp

TOKEN = os.environ.get("DISCORD_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
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

@bot.tree.command(name="upload", description="Upload file to GitHub and get raw link")
@app_commands.describe(file="Pick your file", name="Custom filename e.g. myscript.lua")
async def upload(interaction: discord.Interaction, file: discord.Attachment, name: str = None):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as s:
        async with s.get(file.url) as r:
            content = await r.read()
    filename = name if name else file.filename
    encoded = base64.b64encode(content).decode()
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    check = requests.get(f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{filename}", headers=headers)
    data = {"message": f"upload {filename}", "content": encoded}
    if check.status_code == 200:
        data["sha"] = check.json()["sha"]
    r = requests.put(f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{filename}", headers=headers, json=data)
    if r.status_code in [200, 201]:
        await interaction.followup.send(f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/{filename}")
    else:
        await interaction.followup.send("Upload failed!")

bot.run(TOKEN)
