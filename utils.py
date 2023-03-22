import datetime
from enum import Enum

import discord
import pymongo
import requests

# Pymongo
conn_str = "mongodb token"

mongo = pymongo.MongoClient(conn_str)
db = mongo['data']
PRICES = [0.35, 0.3]
INVISIBLE_CHAR = '\u200b'


class RealTimeCurrencyConverter():
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['data']
        self.currencies['USD'] = 1

    def convert(self, amount, from_currency, to_currency):
        initial_amount = amount
        # first convert it into USD if it is not in USD.
        # because our base currency is USD
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]

        if from_currency == 'USD':
            amount = amount * self.currencies[to_currency]

            # limiting the precision to 4 decimal places
        amount = round(amount, 2)
        return amount


class CustomError(Exception):
    def __init__(self, message, title=":x: Something happened! :x:",
                 color=discord.Color.red()):
        self.message = message
        self.title = title
        self.color = color
        super().__init__(message)


class CustomView(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        if isinstance(error, CustomError):
            error_embed = embed(title=error.title,
                                description=error.message,
                                color=error.color)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        else:
            error_embed = embed(title=":x: Unexpected Error :x:",
                                description="Woah! An unexpected error occurred... Contact an administrator if the"
                                            " issue persists.",
                                thumbnail=Image.ERROR.value,
                                color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            print("An unexpected error occurred, logging to console.")
            raise error


class Image(Enum):
    SUCCESS = 'https://cdn.discordapp.com/attachments/860656459507171368/930999513743765574/checkmark.png'
    ERROR = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500626399232/error.png'
    RELOAD = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500148265001/Refresh_Green.png'
    COIN = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500387332156/wholepurse.png'
    CALENDAR = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500852903996/Notepad.png'
    BAR_GRAPH = 'https://cdn.discordapp.com/attachments/860656459507171368/948804502511816714/pict-bar-chart-cloud-clipart-vector-stencils-library.png'


def is_num(value) -> bool:
    try:
        value = float(value)
        return True
    except:
        return False


def embed(
        title: str = INVISIBLE_CHAR,
        description: str = INVISIBLE_CHAR,
        thumbnail: str = None,
        footer: str = "Quick and fast delivery provided by skyblockmarket.com ",
        footer_icon: str = Image.COIN.value,
        color: discord.Color = discord.Color.blue(),
        timestamp: datetime.datetime = "now"):
    if timestamp == "now":
        timestamp = datetime.datetime.now()

    return_embed = discord.Embed(title=title, description=description, timestamp=timestamp, color=color)
    if thumbnail is not None:
        return_embed.set_thumbnail(url=thumbnail)

    return_embed.set_footer(text=footer, icon_url=footer_icon)

    return return_embed
