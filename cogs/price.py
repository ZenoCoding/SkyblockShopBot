import math

import discord
from discord.commands import slash_command, Option
from discord.ext.commands import has_permissions
from discord.ext import commands
import threading

import utils

config = utils.db.config
api_str = 'https://freecurrencyapi.net/api/v2/latest?apikey=226a89b0-94d5-11ec-ad50-55b0fbca66dc'
cr = utils.RealTimeCurrencyConverter(api_str)


def initiateCurrencyConverter():
    global cr
    threading.Timer(1440.0, initiateCurrencyConverter).start()
    cr = utils.RealTimeCurrencyConverter(api_str)


# Price constants
CURRENCIES = ['USD', 'GBP', 'EUR', 'CAD', 'AUD']
CURRENCY_SYMBOL = ['$', '£', '€', 'C$', 'A$']
MAX_COINS = 3000  # Million Coins (3b)
LEAST_DOLLARS = 10  # Dollars
DISCOUNT_THRESHOLD = 150  # Million
PRICES = [0.35, 0.3]


class Price(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        initiateCurrencyConverter()
        print("Info Cog Loaded")

    def isfloat(self, string):
        try:
            float(string)
            return True
        except:
            return False

    def parseStringCurrency(self, string):
        rate = None
        currency = 0
        for i in range(len(CURRENCY_SYMBOL)):
            if string.lower().endswith(CURRENCIES[i].lower()):
                if self.isfloat(string[:-3]):
                    rate = cr.convert(float(string[:-3]), CURRENCIES[i], 'USD')
                    currency = i
            elif string.lower().endswith(CURRENCY_SYMBOL[i].lower()):
                if self.isfloat(string[:-1]):
                    rate = cr.convert(float(string[:-1]), CURRENCIES[i], 'USD')
                    currency = i
            elif string.lower().startswith(CURRENCY_SYMBOL[i].lower()):
                if self.isfloat(string[1:]):
                    rate = cr.convert(float(string[1:]), CURRENCIES[i], 'USD')
                    currency = i
        if rate is not None:
            return round(rate, 2), currency
        return rate, currency

    def parseString(self, string):
        form = "error"
        multiplier = 1
        currency = None

        if string.lower().endswith("b"):
            string = string[:-1]
            form = "coins"
            multiplier = 1000
        elif string.lower().endswith("m"):
            string = string[:-1]
            form = "coins"
        elif self.isfloat(string):
            return float(string), "coins"
        else:
            converted = self.parseStringCurrency(string)
            string = converted[0]
            currency = converted[1]
            form = 'usd'

        if self.isfloat(string):
            if currency is not None:
                return float(string), form, currency
            return float(string) * multiplier, form

        return -1, "error"

    def calculateDiscountedcoin(self, price: int, guild):
        discount = config.find_one({'_id': guild.id})['discount']
        if price >= DISCOUNT_THRESHOLD * PRICES[1]:
            if discount is not None and price >= discount[1] * PRICES[0]:
                coins = round(math.ceil(price / (PRICES[1] - (discount[0] / 100 * PRICES[0])) * 100) / 100)
            else:
                coins = round(math.ceil(price / PRICES[1] * 100) / 100)
        else:
            if discount is not None and price >= discount[1] * PRICES[0]:
                coins = round(math.ceil(price / (PRICES[0] - (discount[0] / 100 * PRICES[0])) * 100) / 100)
            else:
                coins = round(math.ceil(price / PRICES[0] * 100) / 100)
        return coins

    def getEmbed(self, embed, discounted: bool = False, num: int = 0, stock: int = 0, currency: str = 'usd',
                 guild=None):
        discount = config.find_one({'_id': guild.id})['discount']

        if discounted:
            discounted = 1
        elif not discounted:
            discounted = 0
        else:
            raise ValueError

        if embed == "default":
            main_embed = utils.embed(title="Prices",
                                     description=f"1m coins is ${PRICES[0]}. Orders over 150m are discounted to ${PRICES[1]}\n\nSome Price Reference Points (use /price for specific prices)",
                                     color=discord.Color.orange(),
                                     thumbnail=utils.Image.COIN.value)
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(10, guild)} Million", value="10$")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(17.5, guild)} Million", value="17.5$")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(35, guild)} Million", value="35$")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(45, guild)} Million",
                                 value="45$ **Most Popular!**")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(90, guild)} Million", value="90$ **15% off!**")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(150, guild)} Million", value="150$ **15% off!**")
            main_embed.add_field(name=f"{self.calculateDiscountedcoin(300, guild)} Million",
                                 value="300$ **Best Value!**")
            main_embed.add_field(name="ㅤ\nCurrent Stock",
                                 value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins "
                                       f"to buy!*",
                                 inline=False)
            return main_embed
        elif embed == "coins":
            if discount is not None and num >= discount[1]:
                price_embed = utils.embed(title=f"Prices for {num}M",
                                          description=f"`{num}M` coins is equal to `{round(num * (PRICES[discounted] - PRICES[discounted] * (discount['discount'][0] / 100)))} USD`\n",
                                          color=discord.Color.orange(),
                                          thumbnail=utils.Image.COIN.value)
            else:
                price_embed = utils.embed(title=f"Prices for {num}M",
                                          description=f"`{num}M` coins is equal to `{round(num * PRICES[discounted], 2)} USD`\n",
                                          color=discord.Color.orange(),
                                          thumbnail=utils.Image.COIN.value)

            price_embed.add_field(name="Current Stock",
                                  value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins "
                                        f"to buy!*")
            return price_embed
        elif embed == 'usd':
            amount = int(cr.convert(num, 'USD', CURRENCIES[currency]))
            converted_amount = f'{CURRENCY_SYMBOL[currency]}{amount}'
            price_embed = utils.embed(title=f"Prices For {converted_amount}",
                                      description=f"`{converted_amount}` " +
                                                  f"is equal to `{self.calculateDiscountedcoin(num, guild)}M` coins.\n",
                                      color=discord.Color.orange(),
                                      thumbnail=utils.Image.COIN.value)
            price_embed.add_field(name="Current Stock",
                                  value=f"We currently have `{stock}M` coins in stock.\n*Head over to #purchase-coins "
                                        f"to buy!*")
            return price_embed
        elif embed == "invalid":
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="You put in an invalid amount! Please submit a valid amount of "
                                                  "coins/currency!",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            error_embed.add_field(name="Examples", value="`/price 30m`\n"
                                                         "`/price 20`\n"
                                                         "`/price 100usd`\n"
                                                         "`/price 100$`\n")
            return error_embed
        elif embed == "toolow":
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="Invalid amount. You cannot create orders in amounts under 30m (10 "
                                                  "USD!)\n `!help price` for more info!",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            error_embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            return error_embed
        elif embed == "toohigh":
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="Invalid amount. You cannot check the prices for that many coins! "
                                                  "Check with the owner for orders of this magnitude.\n `!help "
                                                  "price` for more info!",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            return error_embed
        else:
            raise ValueError

    @slash_command(
        name="discount",
        description="Set discount for coins"
    )
    @has_permissions(administrator=True)
    async def discount(self,
                       ctx,
                       todo: Option(str, "Choose: set / clear", default="set", required=True),
                       percent: Option(str, "Amount of discount (from 100%)", required=False),
                       threshold: Option(int, "Enter the threshold. Example: 100", required=False)):
        if todo == 'set':
            if percent is None or threshold is None:
                await ctx.respond("Please enter a percentage/threshold before using this command", ephemeral=True)
                return

            if percent.endswith('%'):
                off = int(percent[:-1:])
            else:
                off = int(percent)

            config.find_one_and_update({'_id': ctx.guild.id}, {'$set': {'ticket.discount': [off, threshold]}})
            await ctx.respond("Successfully done!", ephemeral=True)
            await ctx.respond("Successfully set the new discount!", ephemeral=True)
            return
        if todo == 'clear':
            config.find_one_and_update({'_id': ctx.guild.id}, {'$set': {'ticket.discount': [0, 0]}})
            await ctx.respond("Successfully done!", ephemeral=True)

    @slash_command(
        name="price",
        description="Convert coins to dollars, and vice versa."
    )
    async def price(self,
                    ctx,
                    amount: Option(str, "Amount in Coins or Dollars", default="default", required=False)):

        stock = config.find_one({"_id": ctx.guild.id})['stock']

        if amount == "default":
            await ctx.respond(embed=self.getEmbed("default", ctx, stock=stock, guild=ctx.guild))
        else:
            parsedString = self.parseString(amount)
            num = parsedString[0]
            form = parsedString[1]
            currency = parsedString[2] if len(parsedString) == 3 else 0
            discounted = False

            if form == "error":
                await ctx.respond(embed=self.getEmbed("invalid", ctx, guild=ctx.guild), ephemeral=True)
                return

            if form == "usd":
                if num > 1000:
                    await ctx.respond(embed=self.getEmbed("toohigh", ctx, guild=ctx.guild), ephemeral=True)
                    return
                if num >= DISCOUNT_THRESHOLD * PRICES[0]:
                    discounted = True
                elif num < LEAST_DOLLARS:
                    await ctx.respond(embed=self.getEmbed("toolow", ctx, guild=ctx.guild), ephemeral=True)
                    return
                if num > MAX_COINS * PRICES[0]:
                    await ctx.respond(embed=self.getEmbed("toohigh", ctx, guild=ctx.guild), ephemeral=True)
                    return
            elif form == "coins":
                if num > MAX_COINS:
                    await ctx.respond(embed=self.getEmbed("toohigh", ctx, guild=ctx.guild), ephemeral=True)
                    return
                if num >= DISCOUNT_THRESHOLD:
                    discounted = True
                elif num < LEAST_DOLLARS * PRICES[0]:
                    await ctx.respond(embed=self.getEmbed("toolow", ctx, guild=ctx.guild), ephemeral=True)
                    return

            await ctx.respond(embed=self.getEmbed(embed=form, discounted=discounted, num=num, stock=stock,
                                                  currency=currency, guild=ctx.guild))


def setup(client):
    client.add_cog(Price(client))
