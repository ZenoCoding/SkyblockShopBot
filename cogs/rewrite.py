import discord
from discord.commands import message_command
from discord.ext import commands, tasks

import utils

rewrite = utils.db.rewrite

# Constants
REWRITE_COOLDOWN = 60  # In Minutes


class Rewriter(commands.Cog):

    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=REWRITE_COOLDOWN)
    async def purge_messages(self):
        if rewrite.count_documents({}) == 0:
            return

        for message in rewrite.find({}):
            guild = self.client.get_guild(message["guild"])
            channel = guild.get_channel(message["channel"])
            old_message = await channel.fetch_message(message["_id"])
            embed = None
            if len(old_message.embeds) > 0:
                embed = old_message.embeds[0]
            new_message = await channel.send(content=old_message.content, embed=embed)
            await old_message.delete()


            # Setting the New Message
            rewrite.delete_one({"_id": message['_id']})
            rewrite.insert_one({"_id": new_message.id, "channel": channel.id, "guild": guild.id})

    @commands.Cog.listener()
    async def on_ready(self):
        print("Purge Cog Loaded")
        try:
            self.purge_messages.start()
        except RuntimeError:
            print("Rewrite task already running, cancelling start...")


    @message_command(name="Mark as Rewrite")
    async def rewrite_mark(self, ctx, message: discord.Message):
        # If message has no content/embeds
        if message.content is None and message.embeds[0] is None:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This message does not have content, and cannot be marked for rewriting!",
                                      color=discord.Color.red(),
                                      thumnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return
        elif rewrite.find_one({"_id": message.id}) is not None:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This message has already been marked for rewriting!",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Otherwise, mark it
        message_data = {
            "_id": message.id,
            "channel": message.channel.id,
            "guild": message.guild.id
        }

        rewrite.insert_one(message_data)

        success_embed = utils.embed(title="Message Marked",
                                    description="Message has been marked for rewriting, every hour it will be reposted.",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

    @message_command(name="Unmark as Rewrite")
    async def rewrite_unmark(self, ctx, message: discord.Message):
        # If message has no content/embeds
        if rewrite.find_one({"_id": message.id}) is None:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This message has not been marked for rewriting!",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Otherwise, unmark it
        rewrite.delete_one({"_id": message.id})

        success_embed = utils.embed(title="Message Marked",
                                    description="Message has been unmarked for rewriting.",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)


def setup(client):
    client.add_cog(Rewriter(client))
