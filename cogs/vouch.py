import discord
import json
import datetime
import time
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

            try:
                vouchchannel = ctx.guild.get_channel(channel)
            except:
                vouchchannel = None

            if vouchchannel != None:
                data[str(ctx.guild.id)]["vouch"] = vouchchannel.id
                setEmbed = discord.Embed(title="Vouch channel set!",
                                             description="Vouch channel has been set.")
                await ctx.send(embed=setEmbed)
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return
            else:
                errorEmbed = discord.Embed(title="Invalid channel!", description="You entered an invalid channel! Please try again.", color=discord.Color.red())
                await ctx.send(embed=errorEmbed)


    def isint(self, value):
        try:
            value = int(value)
            return value
        except:
            return False

    async def broadcastvouch(self, vouchdata, guildid):
        with open("data.json", 'r') as f:
            data = json.load(f)

        #Looping through all the guilds the bot is in
        for guild in self.client.guilds:
            if guild.id == guildid:
                return
            guilddata = data[str(guild.id)]
            vouchchannel = guilddata["vouch"]
            # try:
            #Building and Sending the Vouch Embed
            vouchchannel = guild.get_channel(vouchchannel)
            vouchEmbed = discord.Embed(title=f"Vouch!", color=discord.Color.blue(),
                                       description=f"{vouchdata['author']['name']} rated us {vouchdata['score']}.",
                                       timestamp=datetime.datetime.fromisoformat(vouchdata['timestamp']))
            vouchEmbed.add_field(name=f"{vouchdata['rating']}", value=f"\u200b")
            vouchEmbed.set_footer(text=f"Sent By {vouchdata['author']['name']}#{vouchdata['author']['desc']}",
                                  icon_url=vouchdata['author']['avatar'])
            await vouchchannel.send(embed=vouchEmbed)

            with open("vouches.json", 'r') as f:
                vdata = json.load(f)

            #Editing Channel Name to include Vouches
            await vouchchannel.edit(name=f"vouches-{len(vdata['vouch'])}")
            # except:
            #     print(f"Broadcasting vouch failed for server {guild.name}, with an id of {guild.id}. This was likely caused by the vouch channel not being set in that server.")
            #     continue



    @commands.command()
    async def vouch(self, ctx, score="default", *, message="default"):
        with open('data.json', 'r') as f:
            data = json.load(f)

        #Getting the buyer and Vouch Roles

        try:
            buyerrole = ctx.guild.get_role(data[str(ctx.guild.id)]["buyer"])
            vouchchannel = ctx.guild.get_channel(data[str(ctx.guild.id)]["vouch"])
        except:
            await ctx.send("you didn't set a buyer and/or vouch channel lol, remind me to put an error embed here lmao, if you are not an admin ping one")
            return

        if buyerrole not in ctx.message.author.roles:
            notbuyerEmbed = discord.Embed(title="Insufficient Roles", description="You aren't a buyer. Please buy something before leaving a vouch!", color=discord.Color.red())
            await ctx.send(embed=notbuyerEmbed)
            return

        #If there is no vouch channel
        if data[str(ctx.guild.id)]["vouch"] == "unset" or vouchchannel == None:
            unsetEmbed = discord.Embed(title="Vouch Channel Unset",
                                         description="Have an admin setup the vouch channel! Contact the owner for help.",
                                         color=discord.Color.red())
            await ctx.send(embed=unsetEmbed)
            return

        #Not Specifying Score
        if self.isint(score) == False or score == "default" or int(score) < 1 or int(score) > 5:
            missingEmbed = discord.Embed(title="Score Invalid", description="Please specify a score! `!vouch <score> (out of 5)`", color=discord.Color.red())
            await ctx.send(embed=missingEmbed)
        else:
            #message isn't provided as argument
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

            #creating and sending vouch embed
            vouchEmbed = discord.Embed(title=f"Vouch!", color=discord.Color.blue(), description=f"{ctx.message.author.name} rated us {stars}.", timestamp=datetime.datetime.utcnow())
            vouchEmbed.add_field(name=f"{rating}", value=f"\u200b")
            vouchEmbed.set_footer(text=f"Sent By {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.message.author.avatar_url)

            await vouchchannel.send(embed=vouchEmbed)

            #adding vouch information to database
            with open('vouches.json', 'r') as f2:
                vdata = json.load(f2)


            await vouchchannel.edit(name=f"vouches-{len(vdata['vouch'])}")

            vouchdata = {
                "author": {
                    "id": ctx.author.id,
                    "name": ctx.author.name,
                    "desc": ctx.author.discriminator,
                    "avatar": str(ctx.author.avatar_url)
                },
                "score": stars,
                "rating": rating,
                "timestamp": str(datetime.datetime.utcnow())
            }

            vdata['vouch'].append(vouchdata)

            with open("vouches.json", 'w') as f2:
                json.dump(vdata, f2, indent=4)

            # Broadcasting vouch to all servers
            await self.broadcastvouch(vouchdata, ctx.guild.id)

    @commands.command()
    @has_permissions(administrator=True)
    async def restore(self, ctx, channel="default"):
        try:
            channel = ctx.guild.get_channel(int(channel))
        except:
            channel = None
        if channel == "default" or channel == None:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**Please enter a *valid* channel to restore vouches to.\n!restore `channelid`\n!restore 859634782963105842**",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
        else:
            startingEmbed = discord.Embed(title="Restoration Starting :white_check_mark:",
                                       description=f"**Vouch restoration is starting in <#{channel.id}>.**\n*Please be patient, this process can take up to 10 minutes.*",
                                       color=discord.Color.green())
            startingEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/863860424041824257/896942559652368494/Refresh_Green.png")
            startingEmbed.set_footer(icon_url=ctx.guild.icon_url, text=f"Quick and easy delivery provided by {ctx.guild.name}.")

            await ctx.send(embed=startingEmbed)

            #Loading Vouches
            with open('vouches.json', 'r') as f:
                data = json.load(f)

            vouches = data['vouch']

            #Creating and Sending Embeds
            time.sleep(1)

            if len(vouches) == 0:
                #If there are no vouches..
                errorEmbed = discord.Embed(title=":x: Error :x:",
                                           description=f"**Oop! It looks like there are no vouches to restore!**",
                                           color=discord.Color.red())
                errorEmbed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
                errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                      text=f"Quick and easy delivery provided by {ctx.guild.name}.")
                await ctx.send(embed=errorEmbed)
            else:
                #If there are...
                for vouch in vouches:
                    failed = 0
                    try:
                        vouchEmbed = discord.Embed(title=f"Vouch!", color=discord.Color.blue(),
                                                   description=f"{vouch['author']['name']} rated us {vouch['score']}.",
                                                   timestamp=datetime.datetime.fromisoformat(vouch['timestamp']))
                        vouchEmbed.add_field(name=f"{vouch['rating']}", value=f"\u200b")
                        vouchEmbed.set_footer(text=f"Sent By {vouch['author']['name']}#{vouch['author']['desc']}",
                                              icon_url=vouch['author']['avatar'])

                        await channel.send(embed=vouchEmbed)
                    except:
                        print(f"an error occured while restoring vouch number `#{vouches.index(vouch)}`")
                        failed += 1
                        continue

                await channel.edit(name=f"vouches-{len('vouch')}")

                successEmbed = discord.Embed(title="Restoration Completed :white_check_mark:",
                                              description=f"**Restoration completed in <#{channel.id}>.**\n*{failed} vouches failed. {len(vouches)} succeeded. {100-(failed/len(vouches))*100}% success rate.*",
                                              color=discord.Color.green())
                successEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/863860424041824257/896962082422018078/Notepad.png")
                successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                         text=f"Quick and easy delivery provided by {ctx.guild.name}.")
                await ctx.send(embed=successEmbed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Vouch Cog Loaded")

def setup(client):
    client.add_cog(Vouch(client))