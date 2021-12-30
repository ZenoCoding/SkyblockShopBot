import discord
import json
from discord.ext.commands import has_permissions
from discord.ext import commands

class LastMessage(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Last Message Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        with open('data.json', 'r') as f:
            data = json.load(f)

        if message == None:
            return

        try:
            messages = data[str(message.guild.id)]["lastmessages"]
        except:
            return

        #If the the message is from the bot
        if message.author.id == self.client.user.id:
            return

        #If the message is in a last message channel
        if str(message.channel.id) in messages:
            try:
                oldmessage = await message.channel.fetch_message(messages[str(message.channel.id)])
            except:
                pass
            embed = oldmessage.embeds[0]
            await oldmessage.delete()
            newmessage = await message.channel.send(embed=embed)

            #Setting the New Message
            data[str(message.guild.id)]["lastmessages"][str(message.channel.id)] = newmessage.id

            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)

    def get_embed(self, ctx, id):
        #Defining Embeds
        adEmbed = discord.Embed(title="Ad Embed",
                                description=f"**We provide a safe, trustable, source of skyblock coins!**\n*Head over to #purchase-coins to buy!*",
                                color=discord.Color.green())
        adEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
        adEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        ree = discord.Embed(title="pog", description="me stupid")
        
        embeds = [adEmbed, ree]
        try:
            return embeds[int(id)]
        except:
            return "error"

    @commands.command()
    @has_permissions(administrator=True)
    async def lastinit(self, ctx, embedid="default"):
        if embedid == "default":
            embedid = "error"
        else:
            if self.get_embed(ctx, embedid) == "error":
                embedid = "error"

        if embedid == "error":
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**Please enter a *valid* embed id. Please refer to the developer for assistance if you are having issues.**",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        lastMessage = self.get_embed(ctx, embedid)

        with open('data.json', 'r') as f:
            data = json.load(f)

        successEmbed = discord.Embed(title="Last Message Initiated :white_check_mark:",
                                     description=f"**The bot will now always have the last message in <#{ctx.channel.id}>.**",
                                     color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.send(embed=successEmbed)

        messageid = await ctx.send(embed=lastMessage)
        messageid = messageid.id

        print(data[str(ctx.guild.id)]["lastmessages"])
        data[str(ctx.guild.id)]["lastmessages"][str(ctx.channel.id)] = messageid

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @has_permissions(administrator=True)
    async def lastoff(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)
        try:
            del data[str(ctx.guild.id)]["lastmessages"][str(ctx.channel.id)]
        except:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**This channel doesn't have a last message, if it does, then an unexpected error has occured.**\n*Please contact the administrator if this issue persists.*",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Last Message Disabled :white_check_mark:",
                                     description=f"**The last message feature has been disabled in <#{ctx.channel.id}>.**",
                                     color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=successEmbed)


def setup(client):
    client.add_cog(LastMessage(client))