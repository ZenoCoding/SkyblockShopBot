import asyncio
import datetime
import json
import logging

import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from discord.ext.commands import has_permissions

import utils

config = utils.db.config
vouches = utils.db.vouch


class Vouch(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Vouch Cog Loaded")

    @slash_command(name="set_vouch_channel",
                   description="Set the channel for vouches to appear in.")
    @has_permissions(administrator=True)
    async def set_vouch_channel(self, ctx,
                                channel: Option(discord.TextChannel, "Channel")):
        config.update_one({"_id": ctx.guild.id}, {"$set": {"vouch": channel.id}})

        success_embed = utils.embed(title="Vouch Channel Set! :white_check_mark:",
                                    description=f"The vouch channel has been set to {channel.mention}",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

    @staticmethod
    async def broadcast_vouch(vouch_data, guild_id, guilds):
        # Looping through all the guilds the bot is in
        for guild in guilds:
            if guild.id == guild_id:
                return
            guild_data = config.find_one({"_id": guild.id})

            # Is the channel valid?
            vouch_channel = guild.get_channel(guild_data["vouch"])
            if vouch_channel is None:
                logging.info(f"Vouch unable to be broadcast in server {guild.name} because the vouch channel set there"
                             f"is invalid.")
                continue

            # Building and Sending the Vouch Embed
            vouch_embed = utils.embed(title=f"Vouch!", color=discord.Color.blue(),
                                      description=f"{vouch_data['author']['user'][-5:]} rated us {vouch_data['score']}.",
                                      timestamp=datetime.datetime.fromisoformat(vouch_data['timestamp'],
                                                                                footer=f"Sent By {vouch_data['author']['user']}",
                                                                                footer_icon=vouch_data['author'][
                                                                                    'avatar']))
            vouch_embed.add_field(name=f"{vouch_data['rating']}", value=f"\u200b")
            await vouch_channel.send(embed=vouch_embed)

            # Editing Channel Name to include Vouches
            await vouch_channel.edit(name=f"vouches-{vouches.count_documents({})}")

    @slash_command(name="vouch", description="Leave a rating of the server you are in.")
    async def vouch(self, ctx,
                    score: Option(int, "Enter a score out of 5.", min_value=1, max_value=5),
                    message: Option(str, "Leave a message explaining your rating."),
                    anonymous: Option(str, "Would you like to be anonymous while leaving your vouch?",
                                      choices=["Yes", "No"])):

        # Getting the buyer and Vouch Roles
        buyer_role = ctx.guild.get_role(config.find_one({"_id": ctx.guild.id})["buyer"])
        vouch_channel = ctx.guild.get_channel(config.find_one({"_id": ctx.guild.id})["vouch"])

        # Errors
        if buyer_role not in ctx.author.roles:
            await ctx.respond("no buyer role!")
            not_buyer_embed = utils.embed(title="Insufficient Roles",
                                          description="You aren't a buyer. Please buy something before leaving a vouch!",
                                          color=discord.Color.red(),
                                          thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=not_buyer_embed, ephemeral=True)
            return

        # If there is no vouch channel
        if vouch_channel is None:
            unset_embed = utils.embed(title="Vouch Channel Unset",
                                      description="This command is disabled! The server admin has not setup a vouch"
                                                  " channel.",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=unset_embed, ephemeral=True)
            return

        vouch_channel = ctx.guild.get_channel(config.find_one({"_id": ctx.guild.id})["vouch"])
        user = f"{ctx.author.name}#{ctx.author.discriminator}"
        anonymous_text = ""

        if anonymous == "Yes":
            anonymous_text = "anonymous"
            user = f"anonymous#xxxx"

        success_embed = utils.embed(title="Success! :white_check_mark:",
                                    description=f"Your {anonymous_text} rating of `{score}` stars! has been submitted.",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

        stars = ""

        for i in range(int(score)):
            stars = stars + ":star:"

        # it is breaking here for some reason
        # Creating and sending vouch embed
        vouch_embed = utils.embed(title=f"Buyer Vouch!",
                                  color=discord.Color.blue(),
                                  description=f"{user} rated us {stars}.",
                                  footer=f"Sent By {user}",
                                  footer_icon=ctx.author.display_avatar)
        vouch_embed.add_field(name=f"{message}", value=f"\u200b")

        await vouch_channel.send(embed=vouch_embed)

        # Adding vouch information to database

        await vouch_channel.edit(name=f"vouches-{vouches.count_documents({})}")

        vouch_data = {
            "author": {
                "id": ctx.author.id,
                "user": user,
                "avatar": str(ctx.author.display_avatar)
            },
            "score": stars,
            "rating": message,
            "timestamp": str(datetime.datetime.now()),
            "anon": anonymous
        }

        vouches.insert_one(vouch_data)

        # Broadcasting vouch to all servers
        await self.broadcast_vouch(vouch_data, ctx.guild.id, self.client.guilds)

    @slash_command(description="Restore vouches to the vouch channel.")
    @has_permissions(administrator=True)
    async def restore_vouches(self, ctx: discord.ApplicationContext):
        vouch_channel = ctx.guild.get_channel(config.find_one({"_id": ctx.guild.id}))
        if vouch_channel is None:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description=f"**There is no vouch channel set in this server! Use "
                                                  f"`/set_vouch_channel` to set the vouch channel of this server!**",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        starting_embed = utils.embed(title="Restoration Starting :white_check_mark:",
                                     description=f"**Vouch restoration is starting in <#{vouch_channel.id}>."
                                                 f"**\n*Please be patient, this process can take up to 10 minutes.*",
                                     color=discord.Color.green(),
                                     thumbnail=utils.Image.RELOAD.value)

        await ctx.respond(embed=starting_embed, ephemeral=True)

        # Creating and Sending Embeds
        await asyncio.sleep(1)

        if vouches.count_documents({}) == 0:
            # If there are no vouches..
            error_embed = utils.embed(title=":x: Error :x:",
                                      description=f"**Oops! It looks like there are no vouches to restore!**",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        failed = 0

        # If there are...
        for vouch in vouches.find({}):
            try:
                vouch_embed = utils.embed(title=f"Vouch!", color=discord.Color.blue(),
                                          description=f"{vouch['author']['user'][-5:]} rated us {vouch['score']}.",
                                          timestamp=datetime.datetime.fromisoformat(vouch['timestamp'],
                                                                                    footer=f"Sent By {vouch['author']['user']}",
                                                                                    footer_icon=vouch['author'][
                                                                                        'avatar']))
                vouch_embed.add_field(name=f"{vouch['rating']}", value=f"\u200b")
                await vouch_channel.send(embed=vouch_embed)
            except Exception:
                logging.warning(f"Error occurred when restoring vouch. id:`#{vouches.index(vouch)}`")
                failed += 1
                continue

        await vouch_channel.edit(name=f"vouches-{vouches.count_documents({})}")

        success_embed = utils.embed(title="Restoration Completed :white_check_mark:",
                                    description=f"**Restoration completed in <#{vouch_channel.id}>.**\n*{failed} vouches failed to be restored. {len(vouches)} succeeded. {100 - (failed / len(vouches)) * 100}% success rate.*",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.CALENDAR.value)
        await ctx.respond(embed=success_embed)

    @slash_command(description="Converts vouches from JSON to MongoDB")
    async def convert_vouches(self, ctx):
        with open("vouches.json", "r") as f:
            data = json.load(f)

        if len(data["vouches"]):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description=f"**Oops! It looks like there are no vouches to convert!**",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        failed = 0

        for vouch in data["vouches"]:
            try:
                vouches.insert_one(vouch)
            except Exception:
                logging.warning(f"Error occurred when restoring vouch. id:`#{vouches.index(vouch)}`")
                failed += 1
                continue

        success_embed = utils.embed(title="Conversion Completed :white_check_mark:",
                                    description=f"**Converted {len(data['vouches']) - failed}."
                                                f" **\n*{failed} vouches failed to be converted."
                                                f" {100 - (failed / len(vouches)) * 100}% success rate.*",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.CALENDAR.value)
        await ctx.respond(embed=success_embed)


def setup(client):
    client.add_cog(Vouch(client))
