import discord
import math
import json
from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.prices = [0.35, 0.3]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Info Cog Loaded")

    @commands.command(aliases=["info"])
    async def about(self, ctx):
        aboutEmbed = discord.Embed(title="About Us", description="**We are** a shop that is **dedicated** to selling skyblock coins, for low rates, and fast deliveryy times.", color=discord.Color.blue())
        await ctx.send(embed=aboutEmbed)


    @staticmethod
    def isfloat(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def parseString(self, string):
        form = "error"
        multiplier = 1

        if string.lower().endswith("b"):
            string = string[:-1]
            form = "coins"
            multiplier = 1000
        elif string.lower().endswith("m"):
            string = string[:-1]
            form = "coins"
        elif string.lower().endswith("usd"):
            string = string[:-3]
            form = "usd"
        elif string.lower().endswith("$"):
            string = string[:-1]
            form = "usd"
        elif string.lower().startswith("$"):
            string = string[1:]
            form = "usd"
        elif self.isfloat(string):
            return float(string), "coins"



        if self.isfloat(string):
            return float(string)*multiplier, form

        return -1, "error"




    def getEmbed(self, embed, ctx, discounted=False, num=0, stock=0):

        if(discounted == True):
            discounted = 1
        elif(discounted == False):
            discounted = 0
        else:
            raise ValueError

        if(embed == "default"):
            mainEmbed = discord.Embed(title=f"Prices",
                                                   description=f"1m coins is ${self.prices[1]}. Orders over 150m are discounted to ${self.prices[0]}\n\nSome Price Reference Points (use $price for specific prices)",
                                                   color=discord.Color.orange())
            mainEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
            mainEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            mainEmbed.add_field(name="30 Million", value="10$")
            mainEmbed.add_field(name="50 Million", value="17.5$")
            mainEmbed.add_field(name="100 Million", value="35$")
            mainEmbed.add_field(name="150 Million", value="45$ **Most Popular!**")
            mainEmbed.add_field(name="300 Million", value="90$ **15% off!**")
            mainEmbed.add_field(name="500 Million", value="150$ **15% off!**")
            mainEmbed.add_field(name="1 Billion", value="300$ **Best Value!**")
            mainEmbed.add_field(name="ㅤ\nCurrent Stock", value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins to buy!*", inline=False)
            mainEmbed.add_field(name="ㅤ\nAccepted Payment Methods", value="- Paypal\n- Bitcoin\n- Stripe\n- idk what else lmao", inline=False)
            return mainEmbed
        elif(embed == "coins"):
            priceEmbed = discord.Embed(title=f"Prices For {num}M",
                                       description=f"`{num}M` coins is equal to `{math.ceil(num * self.prices[discounted] * 100) / 100} USD`\nㅤ",
                                       color=discord.Color.orange())
            priceEmbed.add_field(name="Current Stock", value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins to buy!*")
            priceEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
            priceEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            return priceEmbed
        elif(embed == "usd"):
            priceEmbed = discord.Embed(title=f"Prices For ${num}",
                                       description=f"`${num}` is equal to `{math.ceil(num / self.prices[discounted] * 100) / 100}M` coins.\nㅤ",
                                       color=discord.Color.orange())
            priceEmbed.add_field(name="Current Stock", value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins to buy!*")
            priceEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
            priceEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            return priceEmbed
        elif(embed == "invalid"):
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description="Invalid amount. Please submit a valid amount.",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.add_field(name="Examples", value="`!price 30m`\n"
                                                        "`!price 20`\n"
                                                        "`!price 100usd`\n"
                                                        "`!price 100$`\n"
                                                        "Use `!help price` for more info!")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            return errorEmbed
        elif(embed == "toolow"):
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description="Invalid amount. You cannot create orders in amounts under 30m (10 USD!)\n"
                                                   "`!help price` for more info!",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            return errorEmbed
        elif(embed == "toohigh"):
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description="Invalid amount. You cannot check the prices for that many coins! Check with the owner for orders of this magnitude.\n"
                                                   "`!help price` for more info!",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            return errorEmbed
        else:
            raise ValueError


    @commands.command()
    async def testparse(self, ctx, string):
        await ctx.send(self.parseString(string))

    @commands.command(aliases=["prices"])
    async def price(self, ctx, amount="default"):
        with open('data.json', 'r') as f:
            data = json.load(f)

        stock = data[str(ctx.guild.id)]["stock"]

        if amount == "default":
            await ctx.send(embed=self.getEmbed("default", ctx, False, -1, stock))
        else:
            parsedString = self.parseString(amount)
            num = parsedString[0]
            form = parsedString[1]
            discounted = False

            if form == "error":
                await ctx.send(embed=self.getEmbed("invalid", ctx))
                return

            if form == "usd":
                if num > 1000:
                    await ctx.send(embed=self.getEmbed("toohigh", ctx))
                    return
                if num >= 45:
                    discounted = True
                elif num < 10:
                    await ctx.send(embed=self.getEmbed("toolow", ctx))
                    return
                if num > 1000:
                    await ctx.send(embed=self.getEmbed("toohigh", ctx))
                    return
            elif form == "coins":
                if num > 3000:
                    await ctx.send(embed=self.getEmbed("toohigh", ctx))
                    return
                if num >= 150:
                    discounted = True
                elif num < 30:
                    await ctx.send(embed=self.getEmbed("toolow", ctx))
                    return

            await ctx.send(embed=self.getEmbed(form, ctx, discounted, num, stock))




def setup(client):
    client.add_cog(Info(client))