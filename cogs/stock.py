import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import has_permissions

import utils

config = utils.db.config
PRICES = utils.PRICES


class Stock(commands.Cog):

    def __init__(self, client):
        self.client = client

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

    def parse_string(self, string):
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

    stock = SlashCommandGroup("stock", "Manages the current stock of the server")

    @stock.command(name="view",
                   description="View the stock of the current server."
                   )
    async def view(self, ctx):
        stock = config.find_one({"_id": ctx.guild.id})['stock']

        stockEmbed = utils.embed(title="Stock :moneybag:",
                                 description=f"**There are currently `{stock}M` coins in stock.**\n*Head over to #purchase-coins to buy!*",
                                 color=discord.Color.green())
        stockEmbed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/860656459507171368/896818647270588426/wholepurse.png")
        stockEmbed.add_field(name="Stock Value",
                             value=f"This is worth `${round(stock * PRICES[0], 2)} USD` (assuming there is no discount)")

        await ctx.respond(embed=stockEmbed)

    @stock.command(name="set",
                   description="Set the stock of the current server.")
    @has_permissions(administrator=True)
    async def set(self, ctx, amount="default"):
        stock = config.find_one({"_id": ctx.guild.id})['stock']

        amount = self.parse_string(amount)

        # Error Embed
        error_embed = utils.embed(title=":x: Error :x:",
                                  description=f"**Please enter a *valid* amount to set the stock to.\n/stock set 100\n/stock set 535m**",
                                  color=discord.Color.red(),
                                  thumbnail=utils.Image.ERROR.value)

        # Success Embed
        stock_embed = utils.embed(title="Stock Updated :white_check_mark:",
                                  description=f"**The stock has been updated from `{stock}M` to `{float(amount)}M`.**",
                                  color=discord.Color.green(),
                                  thumbnail=utils.Image.SUCCESS.value)

        if amount == "default" or amount == -1:
            await ctx.respond(embed=error_embed, ephemeral=True)
        else:
            await ctx.respond(embed=stock_embed, ephemeral=True)

            config.update_one({"_id": ctx.guild.id}, {"$set": {"stock": float(amount)}})

    @stock.command(name="broadcast",
                   description="Create an announcement of the stock in the current server.")
    @has_permissions(administrator=True)
    async def broadcast(self, ctx):

        stock = config.find_one({"_id": ctx.guild.id})["stock"]

        stock_embed = utils.embed(title="Stock :moneybag:",
                                  description=f"**There are currently `{stock}M` coins in stock.**\n*Head over to #purchase-coins to buy!*",
                                  color=discord.Color.green(),
                                  thumbnail=utils.Image.COIN.value)
        stock_embed.add_field(name="Stock Value",
                              value=f"This is worth `${round(stock * PRICES[0], 2)} USD` (assuming there is no discount)")

        success_embed = utils.embed(title="Stock Broadcasted :white_check_mark:",
                                    description=f"**The stock has been broadcasted.**",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.send("||@everyone||")
        await ctx.send(embed=stock_embed)
        await ctx.respond(embed=success_embed, ephemeral=True)


def setup(client):
    client.add_cog(Stock(client))
