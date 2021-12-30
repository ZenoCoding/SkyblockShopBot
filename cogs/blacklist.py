import discord
import json
from discord.ext import commands
from discord.ext.commands import has_permissions

class BlackList(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("BlackList Cog Loaded")\


    @commands.group(invoke_without_command=True)
    @has_permissions(administrator=True)
    async def blacklist(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklistedlist = data[str(ctx.guild.id)]["blacklisted"]
        blacklistedstring = ""

        for channel in blacklistedlist:
            blacklistedstring = blacklistedstring + f"<#{channel}>\n"

        blacklistEmbed = discord.Embed(title="Blacklisted Channels",
                                       description=f"These are the channels that are blacklisted, and users cannot use commands inside them.\n\n**Blacklisted Channels Are**\n{blacklistedstring}")

        await ctx.send(embed=blacklistEmbed)

    @blacklist.command(name="add")
    @has_permissions(administrator=True)
    async def blacklistadd(self, ctx, channel="default"):
        if channel == "default":
            channel = ctx.channel.id
        else:
            try:
                channel = int(channel)
            except:
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="You entered an invalid channel! Please try again.")
                await ctx.send(embed=errorEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklisted = ctx.guild.get_channel(channel)

        if blacklisted != None:
            if blacklisted.id in data[str(ctx.guild.id)]["blacklisted"]:

                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="This channel is already blacklisted!")
                await ctx.send(embed=errorEmbed)
                return
            else:
                data[str(ctx.guild.id)]["blacklisted"].append(blacklisted.id)

            setEmbed = discord.Embed(title="Blacklist Channel Added",
                                     description=f"Channel has been blacklisted. Players can no longer use commands in that channel. Channel Blacklisted: <#{blacklisted.id}>")
            await ctx.send(embed=setEmbed)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            errorEmbed = discord.Embed(title="Invalid channel!",
                                       description="You entered an invalid channel! Please try again.")
            await ctx.send(embed=errorEmbed)

    @blacklist.command()
    @has_permissions(administrator=True)
    async def remove(self, ctx, channel="default"):
        if channel == "default":
            channel = ctx.channel.id
        else:
            try:
                channel = int(channel)
                print("welcome")
            except:
                print("hello")
                print(channel)
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="You entered an invalid channel! Please try again.")
                await ctx.send(embed=errorEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklisted = ctx.guild.get_channel(channel)

        if blacklisted != None:
            try:
                data[str(ctx.guild.id)]["blacklisted"].remove(blacklisted.id)
            except:
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="This channel is not blacklisted!")
                await ctx.send(embed=errorEmbed)
                return

            setEmbed = discord.Embed(title="Blacklist Channel Removed",
                                     description=f"Channel has been removed from blacklist. Players can now use bot commands in this channel. Channel Removeda: <#{blacklisted.id}>")
            await ctx.send(embed=setEmbed)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            errorEmbed = discord.Embed(title="Invalid channel!",
                                       description="You entered an invalid channel! Please try again.")
            await ctx.send(embed=errorEmbed)

def setup(client):
    client.add_cog(BlackList(client))