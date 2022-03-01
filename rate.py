# import discord
# from discord.commands import slash_command, Option, SlashCommandGroup
# from discord.ext import commands
# from discord.ext.commands import has_permissions
#
# from enum import Enum
#
# import utils
#
# config = utils.db.config
#
#
# # Properties that pertain to a user (how much they've sold, how much they are owed, etc.)
# class Property(Enum):
#     OWED = "owed"
#     SOLD = "sold"
#
#
# class Rate(discord.Cog):
#     def __init__(self, client):
#         self.client = client
#
#     def edit(self,
#              user: discord.Member,
#              guild: discord.Guild,
#              property: Property,
#              amount: int):
#         pass
#
#     rate = SlashCommandGroup(name="rate", description="Commands pertaining to seller's rates.")
#
#     @rate.command(name="global", description="Set/view the global rate for all sellers.")
#     async def edit_global(self,
#                           function: Option(name="function", choices=["view", "starting"])):
#         pass
#
# def setup(client):
#     client.add_cog(Rate(client))
