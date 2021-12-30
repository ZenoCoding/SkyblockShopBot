import discord
import random
import asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions


class Giveaway(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Giveaway Cog Loaded")

    def convert(self, time):
        pos = ["s", "m", "h", "d"]

        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

        unit = time[-1]

        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2

        return val * time_dict[unit]

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def giveaway(self, ctx):
        giveawayEmbed = discord.Embed(title="Lets get this giveaway started! :tada:",
                                      description=f"**Answer the questions within 15 seconds!**",
                                      color=discord.Color.green())
        giveawayEmbed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/860656459507171368/899519000130748446/partypopper.png")
        giveawayEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                 text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=giveawayEmbed)

        questions = ["Which channel should it be hosted in?", "What should be the duration of the giveaway? (s|m|h|d)",
                     "What is the prize of the giveaway?"]

        answers = []

        for i in questions:
            questionEmbed = discord.Embed(title="Giveaway Questions :tada:",
                                         description=f"**{i}**",
                                         color=discord.Color.green())
            questionEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/860656459507171368/899519000130748446/partypopper.png")
            questionEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                    text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=questionEmbed)

            try:
                print("waiting")
                msg = await self.client.wait_for('message', timeout=15.0, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
                print("waited")
            except asyncio.TimeoutError:
                errorEmbed = discord.Embed(title=":x: Timeout Error :x:",
                                           description=f"**You ran out of time! Please try to be faster next time.**",
                                           color=discord.Color.red())
                errorEmbed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
                errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                      text=f"Quick and easy delivery provided by {ctx.guild.name}.")
                await ctx.send(embed=errorEmbed)
                return
            else:
                answers.append(msg.content)

        try:
            channel_id = int(answers[0][2:-1])
        except:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time.",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        channel = self.client.get_channel(channel_id)

        time = self.convert(answers[1])
        if time == -1:
            errorEmbed = discord.Embed(title=":x: Unit Error :x:",
                                       description=f"You didn't answer with a proper unit. Use (s|m|h|d) next time!",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return
        elif time == -2:
            errorEmbed = discord.Embed(title=":x: Unit Error :x:",
                                       description=f"The time must be an integer, please specify an integer next time.",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        prize = answers[2]

        giveawayEmbed = discord.Embed(title="Giveaway started! :tada:",
                                      description=f"The giveaway will be in {channel.mention} and will last {answers[1]} seconds!",
                                      color=discord.Color.green())
        giveawayEmbed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/860656459507171368/899519000130748446/partypopper.png")
        giveawayEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                 text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=giveawayEmbed)

        #GIVEAWAY EMBED FOR WOVL TO EDIT
        embed = discord.Embed(title="Giveaway!", description=f"{prize}", color=discord.Color.blue())
        embed.add_field(name="Hosted by:", value=ctx.author.mention)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/860656459507171368/899519000130748446/partypopper.png")
        embed.set_footer(text=f"Ends {answers[1]} from now!")

        my_msg = await channel.send(embed=embed)

        await my_msg.add_reaction("🎉")

        await asyncio.sleep(time)

        new_msg = await channel.fetch_message(my_msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        #Winner Embed
        winnerEmbed = discord.Embed(title="Giveaway Ended! :tada:",
                                      description=f"The giveaway for **{prize}** has ended.",
                                      color=discord.Color.green())
        winnerEmbed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/898715995995267072/899506636085948456/party-popper_1f389.png")
        winnerEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                 text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await channel.send(content=f"Congratulations! {winner.mention} won the prize: {prize}!", embed=winnerEmbed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def reroll(self, ctx, channel: discord.TextChannel, id_: int = "default"):
        try:
            new_msg = await channel.fetch_message(id_)
        except:
            errorEmbed = discord.Embed(title=":x: ID Error :x:",
                                       description=f"Please enter a valid message id.",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)

        await channel.send(f"Congratulations, the new winner is: {winner.mention}!")

    @reroll.errore
    async def reroll_error(self, ctx, e):
        if isinstance(e, commands.errors.ChannelNotFound):
            errorEmbed = discord.Embed(title=":x: ID Error :x:",
                                       description=f"Please enter a valid message id.",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)


def setup(client):
    client.add_cog(Giveaway(client))