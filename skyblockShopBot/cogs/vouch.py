import discord
import json
import datetime
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Vouch(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @has_permissions(administrator=True)
    async def setvouch(self, ctx, channel="default"):
        if channel == "default":
            defaultEmbed = discord.Embed(title="Vouch Channel", description="Type `!setvouch <channel id>` to set the channel.")
            await ctx.send(embed=defaultEmbed)
        else:
            with open('data.json', 'r') as f:
                data = json.load(f)

            if channel == "new":
                channel = await ctx.guild.create_text_channel("vouches")
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                createdEmbed = discord.Embed(title="Vouch channel created!", description="Vouch channel has been created.")
                await ctx.send(embed=createdEmbed)
                data[str(ctx.guild.id)]["vouch"] = channel.id
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return


            vouchchannel = ctx.guild.get_channel(channel)

            if vouchchannel != None:
                data[str(ctx.guild.id)]["vouch"] = vouchchannel.id
                setEmbed = discord.Embed(title="Vouch channel set!",
                                             description="Vouch channel has been set.")
                await ctx.send(embed=setEmbed)
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return
            else:
                errorEmbed = discord.Embed(title="Invalid channel!", description="You entered an invalid channel! Please try again.")
                await ctx.send(embed=errorEmbed)


    def isint(self, value):
        try:
            value = int(value)
            return value
        except:
            return False

    @commands.command()
    async def vouch(self, ctx, score="default", message="default"):
        with open('data.json', 'r') as f:
            data = json.load(f)

        buyerrole = ctx.guild.get_role(data[str(ctx.guild.id)]["buyer"])
        vouchchannel = ctx.guild.get_channel(data[str(ctx.guild.id)]["vouch"])

        if buyerrole not in ctx.message.author.roles:
            notbuyerEmbed = discord.Embed(title="Insufficient Roles", description="You aren't a buyer. Please buy something before leaving a vouch!", color=discord.Color.red())
            await ctx.send(embed=notbuyerEmbed)
            return

        if data[str(ctx.guild.id)]["vouch"] == "unset" or vouchchannel == None:
            unsetEmbed = discord.Embed(title="Vouch Channel Unset",
                                         description="Have an admin setup the vouch channel! Contact the owner for help.",
                                         color=discord.Color.red())
            await ctx.send(embed=unsetEmbed)
            return


        if self.isint(score) == False or score == "default" or int(score) < 1 or int(score) > 5:
            missingEmbed = discord.Embed(title="Score Invalid", description="Please specify a score! `!vouch <score> (out of 5)`", color=discord.Color.red())
            await ctx.send(embed=missingEmbed)
        else:
            if message == "default":
                ratingEmbed = discord.Embed(title="Rating", description="Please leave a rating explaining your score. You have `60` seconds.", color=discord.Color.blue())
                await ctx.send(embed=ratingEmbed)

                rating = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                rating = rating.content
            else:
                rating = message

            successEmbed = discord.Embed(title="Success! :white_check_mark:", description=f"Your rating of `{score}` stars! has been submitted.")
            await ctx.send(embed=successEmbed)

            stars = ""

            for i in range(int(score)):
                stars = stars + ":star:"

            vouchEmbed = discord.Embed(title=f"Vouch!", color=discord.Color.blue(), description=f"<@{ctx.message.author.id}> rated us {stars}.", timestamp=datetime.datetime.utcnow())
            vouchEmbed.add_field(name=f"{rating}", value=f"\u200b")
            vouchEmbed.set_footer(text=f"Sent By {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.message.author.avatar_url)

            await vouchchannel.send(embed=vouchEmbed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Vouch Cog Loaded")

def setup(client):
    client.add_cog(Vouch(client))