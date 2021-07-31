import discord
from discord.ext import commands

class Order(commands.Cog):

    def __init__(self, client):
        self.client = client



    @commands.Cog.listener()
    async def on_ready(self):
        print("Order Cog Loaded")

    @commands.command()
    async def order(self, ctx):
        response = await self.client.wait_for('message', lambda message : message.author == ctx.message.author)


def setup(client):
    client.add_cog(Order(client))