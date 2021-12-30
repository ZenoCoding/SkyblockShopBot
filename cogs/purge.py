import discord
import json
from discord.ext.commands import has_permissions
from discord.ext import commands
from discord.ext import tasks


class Purge(commands.Cog):

    def __init__(self, client):
        self.client = client

    @tasks.loop(hours=1)
    async def purgemessages(self):
        with open('purge.json', 'r') as f:
            data = json.load(f)

        messages = data["purge"]

        if len(messages) == 0:
            return

        for message in messages:
            try:
                guild = self.client.get_guild(message["guild"])
                channel = guild.get_channel(message["channel"])
                oldmessage = await channel.fetch_message(message["id"])
                embed = oldmessage.embeds[0]
                text = oldmessage.content
                await oldmessage.delete()
                newmessage = await channel.send(content=text, embed=embed)

                # Setting the New Message
                data["purge"][messages.index(message)]["id"] = str(newmessage.id)
            except:
                print(f"Error: Message with id of {message['id']} was not able to be rewritten.")

        with open('purge.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Purge Cog Loaded")
        self.purgemessages.start()


    @commands.group(invoke_without_command=True, pass_context=True)
    @has_permissions(administrator=True)
    async def rewrite(self, ctx):
        infoEmbed = discord.Embed(title="Rewrite Command",
                                     description=f"The **rewrite** command will delete and resend marked messages on an interval. \nTry running `!rewrite mark <messageid>` or `!rewrite unmark <messageid>`\n*Note: Messages will be purged and resent in the order that they are marked.\n If you want them in an order, then mark them in that order.*",
                                     color=discord.Color.green())
        infoEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        #TODO: Create an info icon
        await ctx.send(embed=infoEmbed)



    @rewrite.command()
    @has_permissions(administrator=True)
    async def mark(self, ctx, message="default"):
        # Check if the message is a REAL message
        try:
            message = int(message)
            message = await ctx.fetch_message(int(message))
        except:
            message = None

        #check if the message has content
        try:
            if message.content is None and message.embeds[0] is None:
                message = None
        except:
            message = None

        # if it isn't, return an error
        if message is None or message == "default":
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**Please enter a *valid* message id. If this does not work, then try moving to the channel that the message was sent in.**\n*Note: Messages will be purged and resent in the order that they are marked.\n If you want them in an order, then mark them in that order.*",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        # Open the data
        with open('purge.json', 'r') as f:
            data = json.load(f)

        # Write the Data
        messagedata = {
            "id": message.id,
            "channel": message.channel.id,
            "guild": message.guild.id
        }

        if messagedata in data["purge"]:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**This message is already marked!**\n*Note: Messages will be purged and resent in the order that they are marked.\n If you want them in an order, then mark them in that order.*",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        data["purge"].append(messagedata)

        # Define and Send the success embed
        successEmbed = discord.Embed(title="Rewrite Message Marked :white_check_mark:",
                                     description=f"**This message will now be deleted and resent every hour. **\n*Note: Messages will be purged and resent in the order that they are marked.\n If you want them in an order, then mark them in that order.*",
                                     color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.send(embed=successEmbed)

        with open("purge.json", 'w') as f:
            json.dump(data, f, indent=4)

    @rewrite.command()
    @has_permissions(administrator=True)
    async def unmark(self, ctx, message="default"):
        with open('purge.json', 'r') as f:
            data = json.load(f)
        try:
            message = await ctx.channel.fetch_message(message)
            for messagedata in data["purge"]:
                if str(messagedata["id"]) == str(message.id):
                    messageindex = data["purge"].index(messagedata)
                    data["purge"].remove(data["purge"][messageindex])
        except:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**This message isn't a purge message!**\n*If you want to mark it as one, try `!rewrite mark <messageid>`!\nPlease contact the administrator if this issue persists.*",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctax.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        with open("purge.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Rewrite Message Unmarked :white_check_mark:",
                                     description=f"**This message has been unmarked, and will not be purged.**",
                                     color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=successEmbed)


def setup(client):
    client.add_cog(Purge(client))
