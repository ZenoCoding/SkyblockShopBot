import discord
from enum import Enum
import utils

config = utils.db.config
orders = utils.db.orders


class ItemType(Enum):
    COINS = "COINS"
    ISLAND = ""

class Item:
    def __init__(self, item_type: ItemType, amount: int):
        self.item_type = item_type
        self.amount = amount


class Order:
    def __init__(self,
                 user: discord.Member,
                 guild: discord.Guild,
                 ticket,  # :id?
                 item: Item):
        self.user = user
        self.guild = guild
        self.ticket = ticket
        self.item = item


    def data_dict(self):
        # Create post in database and write information
        data = {
            "user": self.user,
            "guild": self.guild,
            "ticket": self.ticket,
            "item": self.item
        }
        return data
