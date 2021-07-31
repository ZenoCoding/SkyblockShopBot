import discord
from discord.ext import commands

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.group(pass_context=True, invoke_without_command=True)
    async def help(self, ctx):
        helpEmbed = discord.Embed(title="Help",
                                  description="Try !help <command>")
        helpEmbed.add_field(name="Availible Commands", value="`!price`, `!joke`, `!vouch`")
        await ctx.send(embed=helpEmbed)


    @help.command(aliases=["prices"])
    async def price(self, ctx):
        helpEmbed = discord.Embed(title="Price Help", description="Tells you how much a certain amount of coins is worth, or how many coins an amount of money can buy..")
        helpEmbed.add_field(name="Usage", value="`!price 230m`\n`!price 10usd`")
        await ctx.send(embed=helpEmbed)

    @help.command()
    async def joke(self, ctx):
        helpEmbed = discord.Embed(title="Joke Help", description="Tells you a joke.")
        helpEmbed.add_field(name="Usage", value="`!joke`")
        await ctx.send(embed=helpEmbed)

    @help.command()
    async def vouch(self, ctx):
        helpEmbed = discord.Embed(title="Vouch Help", description="Submits a vouch. Must have buyer role")
        helpEmbed.add_field(name="Usage", value="`!vouch <score> <message>`")
        await ctx.send(embed=helpEmbed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Cog Loaded")

def setup(client):
    client.add_cog(Help(client))