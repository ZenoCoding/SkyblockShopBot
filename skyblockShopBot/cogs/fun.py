import discord
from discord.ext import commands

class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def joke(self, ctx):
        jokeEmbed = discord.Embed(name="A Joke", description=f"Why did the skyblock player cross the roads of discord? To get to **discord.gg/skyblockshop** to buy skyblock coins!", color=discord.Color.blue())
        await ctx.send(embed=jokeEmbed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun Cog Loaded")

def setup(client):
    client.add_cog(Fun(client))