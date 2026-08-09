import discord
from discord import app_commands
import os, base64, requests, aiohttp, io

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
        raw = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/main/{filename}"
        embed = discord.Embed(description=f'loadstring(game:HttpGet("{raw}"))()', color=0x000000)
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("Upload failed!")

@bot.tree.command(name="convert", description="Convert content from a link to a file")
@app_commands.describe(link="The raw URL to fetch", name="Filename e.g. script.lua")
async def convert(interaction: discord.Interaction, link: str, name: str = "script.lua"):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as s:
        async with s.get(link) as r:
            if r.status != 200:
                await interaction.followup.send("Failed to fetch the link!")
                return
            content = await r.read()
    file = discord.File(io.BytesIO(content), filename=name)
    await interaction.followup.send(file=file)

bot.run(TOKEN)
