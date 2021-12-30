import discord
import json
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Stock(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.prices = 0.3

    @commands.Cog.listener()
    async def on_ready(self):
        print("Stock Cog Loaded")

    @staticmethod
    def isfloat(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def parseString(self, string):
        multiplier = 1

        if string.lower().endswith("b"):
            string = string[:-1]
            multiplier = 1000
        elif string.lower().endswith("m"):
            string = string[:-1]
        elif self.isfloat(string):
            return float(string)

        if self.isfloat(string):
            return float(string) * multiplier

        return -1

    @commands.group(pass_context=True, invoke_without_command=True)
    async def stock(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        stock = data[str(ctx.guild.id)]["stock"]

        stockEmbed = discord.Embed(title="Stock :moneybag:",
                                   description=f"**There are currently `{stock}M` coins in stock.**\n*Head over to #purchase-coins to buy!*",
                                   color=discord.Color.green())
        stockEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
        stockEmbed.add_field(name="Stock Value", value=f"This is worth `${round(stock*self.prices, 2)} USD` (assuming there is no discount)")
        stockEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.send(embed=stockEmbed)

    @stock.command()
    @has_permissions(administrator=True)
    async def set(self, ctx, amount="default"):
        with open('data.json', 'r') as f:
            data = json.load(f)

        stock = data[str(ctx.guild.id)]["stock"]

        amount = self.parseString(amount)

        #Error Embed
        errorEmbed = discord.Embed(title=":x: Error :x:",
                                   description=f"**Please enter a *valid* amount to set the stock to.\n!stock set 100\n!stock set 535m**",
                                   color=discord.Color.red())
        errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
        errorEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        #Success Embed
        stockEmbed = discord.Embed(title="Stock Updated :white_check_mark:",
                                   description=f"**The stock has been updated from `{stock}M` to `{float(amount)}M`.**",
                                   color=discord.Color.green())
        stockEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
        stockEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        if amount == "default" or amount == -1:
            await ctx.send(embed=errorEmbed)
        else:
            await ctx.send(embed=stockEmbed)

            data[str(ctx.guild.id)]["stock"] = float(amount)
            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)

    @stock.command()
    @has_permissions(administrator=True)
    async def broadcast(self, ctx, channel="default"):
        try:
            channel = ctx.guild.get_channel(int(channel))
        except:
            channel = None
        if channel == "default" or channel == None:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**Please enter a *valid* channel to broadcast to.\n!stock broadcast `channelid`\n!stock broadcast 859634782963105842**",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
        else:

            with open('data.json', 'r') as f:
                data = json.load(f)

            stock = data[str(ctx.guild.id)]["stock"]

            stockEmbed = discord.Embed(title="Stock :moneybag:",
                                       description=f"**There are currently `{stock}M` coins in stock.**\n*Head over to #purchase-coins to buy!*",
                                       color=discord.Color.green())
            stockEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
            stockEmbed.add_field(name="Stock Value", value=f"This is worth `${round(stock * self.prices, 2)} USD` (assuming there is no discount)")
            stockEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

            successEmbed = discord.Embed(title="Stock Broadcasted :white_check_mark:",
                                       description=f"**The stock has been broadcasted in <#{channel.id}>.**",
                                       color=discord.Color.green())
            successEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
            successEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

            await channel.send("||@everyone||")
            await channel.send(embed=stockEmbed)
            await ctx.send(embed=successEmbed)







def setup(client):
    client.add_cog(Stock(client))