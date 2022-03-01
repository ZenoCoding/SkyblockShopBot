import datetime
from enum import Enum

import discord
import pymongo
import requests

# Pymongo
conn_str = "mongodb+srv://shopbot:admin@skyblockshopdata.t0jjh.mongodb.net/test"

mongo = pymongo.MongoClient(conn_str)
db = mongo['data']
PRICES = [0.35, 0.3]


class Image(Enum):
    SUCCESS = 'https://cdn.discordapp.com/attachments/860656459507171368/930999513743765574/checkmark.png'
    ERROR = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500626399232/error.png'
    RELOAD = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500148265001/Refresh_Green.png'
    COIN = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500387332156/wholepurse.png'
    CALENDAR = 'https://cdn.discordapp.com/attachments/860656459507171368/930998500852903996/Notepad.png'


class RealTimeCurrencyConverter():
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['data']

    def convert(self, amount, from_currency, to_currency):
        initial_amount = amount
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]

        amount = round(amount, 2)
        return amount


def embed(
        title: str = "\u200b",
        description: str = "\u200b",
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
