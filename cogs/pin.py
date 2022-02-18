import logging

import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from discord.ext.commands import has_permissions

import utils

config = utils.db.config

# Defining all the embeds that can be used as pinned messages
adEmbed = utils.embed(title="Ad Embed",
                      description=f"**We provide a safe, trustable, source of skyblock coins!**\n*Head over to #purchase-coins to buy!*",
                      color=discord.Color.green(),
                      thumbnail=utils.Image.COIN.value)

ree = utils.embed(title="pog", description="me stupid")

pinnable_embeds = [adEmbed, ree]


class PinMessage(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Pin Message Cog Loaded")

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message is None:
            return

        pin_msgs = config.find_one({"_id": message.guild.id})["pinned_messages"]
        pin_msg_channels = pin_msgs.keys()

        # If the the message is from the bot
        if message.author.id == self.client.user.id:
            return

        # If the message is in a last message channel
        if str(message.channel.id) in pin_msg_channels:
            try:
                old_message = await message.channel.fetch_message(pin_msgs[str(message.channel.id)][0])
                await old_message.delete()
            except Exception as e:
                config.update_one({"_id": message.guild.id},
                                  {"$unset": {f"pinned_messages.{message.channel.id}": ""}})
                logging.log(f"Unable to update pinned message in channel {message.channel.id}, deleting database entry.")
                raise e
            new_message = await message.channel.send(embed=pinnable_embeds[pin_msgs[str(message.channel.id)][1]])

            # Setting the New Message
            config.update_one({"_id": message.guild.id},
                              {"$set": {f"pinned_messages.{message.channel.id}.0": new_message.id}})

    @slash_command(
        name="pin",
        description="Pin a message to the bottom of the channel, forcing it to stay there."
    )
    @has_permissions(administrator=True)
    async def pin(self,
                  ctx,
                  embed: Option(int, "Pick an embed in the list.", minvalue=1, max_value=len(pinnable_embeds))):
        pinned_embed = pinnable_embeds[embed]

        success_embed = utils.embed(title="Last Message Initiated :white_check_mark:",
                                    description=f"**The bot will now always have the last message in <#{ctx.channel.id}>.**",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.respond(embed=success_embed, ephemeral=True)

        message = await ctx.send(embed=pinned_embed)

        # Setting the Message
        config.update_one({"_id": ctx.guild.id},
                          {"$set": {f"pinned_messages.{str(ctx.channel.id)}": (message.id, embed)}})

    @slash_command(
        name="unpin",
        description="Unpin a message from the channel.")
    @has_permissions(administrator=True)
    async def unpin(self, ctx):
        if str(ctx.channel.id) not in config.find_one({f"_id": ctx.guild.id})["pinned_messages"]:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description=f"**This channel doesn't have a pinned message! Try using `/pin` to create one!**",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        message = await ctx.channel.fetch_message(
            config.find_one({f"_id": ctx.guild.id})["pinned_messages"][ctx.channel.id][0])
        message.delete()

        config.update_one({"_id": ctx.guild.id},
                          {"$unset": {f"pinned_messages.{ctx.channel.id}": ""}})

        success_embed = utils.embed(title="Message Unpinned :white_check_mark:",
                                    description=f"**The message in <#{ctx.channel.id}> has been removed and unpinned.**",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)


def setup(client):
    client.add_cog(PinMessage(client))
