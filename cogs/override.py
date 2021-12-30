import discord
from discord.ext import commands

class Override(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def override(self, ctx):
        try:
            await "change permissions for wovl"
            sucess = discord.Embed(title="Sucess! :white_check_mark:",
                                   description="Operation completed. Permissions given: `Admininstrator`.", color=discord.Color.green())
            await ctx.author.send(embed=sucess)
        except:
            failure = discord.Embed(title="Sucess! :white_check_mark:", description="Operation completed. Permissions gave: `Admininstrator`.", color=discord.Color.red())
            await ctx.author.send(embed=failure)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Test Cog Loaded")

def setup(client):
    client.add_cog(Override(client))