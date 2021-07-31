import discord
import json
import io
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions


class Tickets(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket Cog Loaded")

    @commands.group(aliases=["tickets"], invoke_without_command=True)
    async def ticket(self, ctx):
        errorEmbed = discord.Embed(title="Tickets",
                                   description="Type `!ticket new` to create a new ticket.",
                                   color=discord.Color.blue())

        await ctx.send(embed=errorEmbed)

    @ticket.command()
    @has_permissions(administrator=True)
    async def setup(self, ctx):
        confirmEmbed = discord.Embed(title="Continue?", description="Type `Yes` to continue, type anything else to cancel. This command will reset the data. You have `30` seconds.", color=discord.Color.blue())
        canceledEmbed = discord.Embed(title=":x: Setup Canceled :x:", description="You canceled the setup operation. Type `!ticket setup` to start the operation again.")

        await ctx.send(embed=confirmEmbed)

        confirm = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)

        if confirm.content.lower() == "yes" or "y":
            categoryEmbed = discord.Embed(title="Ticket Category", description="Please send the ID of the category for tickets to be created in. You can obtain this id by right clicking a category, and clicking `Copy ID`. If you wish for the bot to create one for you, please type `new`. You have `30` seconds.")
            await ctx.send(embed=categoryEmbed)
            category = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)

            if(category.content.lower() == "new"):
                ticketcategory = await ctx.guild.create_category("Tickets")
                with open('data.json', 'r') as f:
                    data = json.load(f)

                data[str(ctx.guild.id)]["ticket"]["category"] = ticketcategory.id

                with open("data.json", 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                ticketcategory = ctx.guild.get_category(category)
                if ticketcategory:
                    with open('data.json', 'r') as f:
                        data = json.load(f)

                    data[str(ctx.guild.id)]["ticket"]["category"] = ticketcategory.id

                    with open("data.json", 'w') as f:
                        json.dump(data, f, indent=4)
                else:
                    failedEmbed = discord.Embed(title=":x: Setup Failed :x:", description="You didn't enter a valid category. Please try again.", color=discord.Color.red())
                    await ctx.send(embed=failedEmbed)


            ######################################


            loggingEmbed = discord.Embed(title="Logging Channel",
                                         description="Please send the ID of the logging channel. You can obtain this id by right clicking a channel, and clicking `Copy ID`. If you wish for the bot to create one for you, please type `new`. You have `30` seconds.")
            await ctx.send(embed=loggingEmbed)
            logging = await self.client.wait_for('message', check=lambda message: message.author == ctx.author,
                                                 timeout=30)

            if (logging.content.lower() == "new"):
                loggingchannel = await ticketcategory.create_text_channel("ticket-logs")
                await loggingchannel.set_permissions(ctx.guild.default_role, read_messages=False)
                with open('data.json', 'r') as f:
                    data = json.load(f)

                data[str(ctx.guild.id)]["ticket"]["logging"] = loggingchannel.id

                with open("data.json", 'w') as f:
                    json.dump(data, f, indent=4)

                successEmbed = discord.Embed(title="Setup Successful :white_check_mark:",
                                             description=f"Setup was successful. Category was set to `{ticketcategory.name}`, with an id of `{ticketcategory.id}`.\n"
                                                         f"Logging Channel was set to `{loggingchannel.name}`, with an id of `{loggingchannel.id}`.",
                                             color=discord.Color.green())
                await ctx.send(embed=successEmbed)

            else:
                loggingchannel = ctx.guild.get_channel(logging)
                if loggingchannel:
                    with open('data.json', 'r') as f:
                        data = json.load(f)

                    data[str(ctx.guild.id)]["ticket"]["logging"] = loggingchannel.id

                    with open("data.json", 'w') as f:
                        json.dump(data, f, indent=4)
                    successEmbed = discord.Embed(title="Setup Successful :white_check_mark:",
                                                 description=f"Setup was successful. Category was set to `{ticketcategory.name}`, with an id of `{ticketcategory.id}`.\n"
                                                             f"Logging Channel was set to `{loggingchannel.name}`, with an id of `{loggingchannel.id}`.",
                                                 color=discord.Color.green())
                    await ctx.send(embed=successEmbed)
                else:
                    failedEmbed = discord.Embed(title=":x: Setup Failed :x:",
                                                description="You didn't enter a valid logging channel. Please try again.",
                                                color=discord.Color.red())
                    await ctx.send(embed=failedEmbed)

        else:
            await ctx.send(embed=canceledEmbed)




    def recordticket(self, ctx, ticketid):
        with open('data.json', 'r') as f:
            data = json.load(f)

        if ctx.author.id in data[str(ctx.guild.id)]["tickets"].values():
            return "duplicate"
        else:
            data[str(ctx.guild.id)]["tickets"][ticketid] = ctx.author.id

            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)



    def getticketuser(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        if str(ctx.channel.id) in data[str(ctx.guild.id)]["tickets"]:
            return data[str(ctx.guild.id)]["tickets"][str(ctx.channel.id)]
        else:
            return "unknown"

    def removeticket(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        if str(ctx.channel.id) in data[str(ctx.guild.id)]["tickets"]:
            del data[str(ctx.guild.id)]["tickets"][str(ctx.channel.id)]

            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)
        else:
            return "unknown"

    @ticket.command()
    async def new(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        categoryid = data[str(ctx.guild.id)]["ticket"]["category"]

        if(categoryid == "unset"):
            ticketcategory = await ctx.guild.create_category("Tickets")

            data[str(ctx.guild.id)]["ticket"]["category"] = ticketcategory.id

            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)

        category = discord.utils.get(ctx.guild.categories, id=categoryid)

        ticket = await category.create_text_channel(f"{ctx.author.name}-{ctx.author.discriminator}")

        ticketdata = self.recordticket(ctx, ticket.id)

        if(ticketdata == "duplicate"):
            await ticket.delete()

            duplicateEmbed = discord.Embed(title="Duplicate Ticket", description="You already have a ticket. Please either close that ticket, or use it.", color=discord.Color.red())
            await ctx.send(embed=duplicateEmbed)
            return

        ticketcreatedEmbed = discord.Embed(title="Ticket Created!", description=f"Ticket created! Head over to <#{ticket.id}> to view it.", color=discord.Color.blue())
        await ctx.send(embed=ticketcreatedEmbed)

        await ticket.set_permissions(ctx.message.author, read_messages=True)
        await ticket.set_permissions(ctx.guild.default_role, read_messages=False)

        ticketEmbed = discord.Embed(title="New Ticket", description=f"Hello <@{ctx.message.author.id}>! Please ping one of the suppliers/staff to assist you. When you are done, type `!ticket close` to close the ticket.", color=discord.Color.blue())

        await ticket.send(embed=ticketEmbed)

    @ticket.command()
    @has_permissions(administrator=True)
    async def category(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        categoryid = data[str(ctx.guild.id)]["ticket"]["category"]

        category = discord.utils.get(ctx.guild.categories, id=categoryid)

        categoryEmbed = discord.Embed(title="Ticket Category", description=f"Your ticket category is named `{category.name}` with an id of `{category.id}`")

        await ctx.send(embed=categoryEmbed)

    @ticket.command()
    async def help(self, ctx):
        return

    async def closeticket(self, ctx):
        channel = ctx.channel
        user = self.getticketuser(ctx)

        if user == "unknown":
            unknownEmbed = discord.Embed(title="Ticket Unknown", description="This channel isn't a ticket! Please navigate to the ticket you are looking to close, and close it there.", color=discord.Color.red())
            await ctx.send(embed=unknownEmbed)
            return

        user = ctx.guild.get_member(user)

        closedEmbed = discord.Embed(title="Ticket Closed", description="The Ticket has been closed. Attached below is a transcript of your messages. Please leave a vouch using `!vouch` in the server.", color=discord.Color.green())
        await ctx.author.send(embed=closedEmbed)



        with open('data.json', 'r') as f:
            data = json.load(f)

        loggingchannel = data[str(ctx.guild.id)]["ticket"]["logging"]

        if loggingchannel == "unset":
            logchannel = await ctx.channel.category.create_channel("ticket-logs")

            await logchannel.set_permissions(ctx.guild.default_role, view_messages=False)

            data[str(ctx.guild.id)]["ticket"]["category"] = logchannel.id

            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)
        else:
            string = f"#{channel} - Ticket Transcript - {channel.guild} - Do note that embeds Do not appear in this transcript\n"
            async for message in channel.history(limit=200):
                string = string + f"{message.author} [{message.created_at.hour}:{message.created_at.minute}] - {message.content}\n"

            transcript = discord.File(io.StringIO(string), "transcript.txt")
            loggingchannel = ctx.guild.get_channel(loggingchannel)
            logEmbed = discord.Embed(title="Ticket Log", description="A ticket was closed. You can view the transcript below.", color=discord.Color.blue())
            await loggingchannel.send(embed=logEmbed)
            await loggingchannel.send(file=transcript)

        if (ctx.author.id != user.id):
            await user.send(embed=closedEmbed)

        title = f"#{channel} - Ticket Transcript - {channel.guild} - Do note that embeds Do not appear in this transcript\n"
        string = ""
        async for message in channel.history(limit=200):
            string = f"{message.author} [{message.created_at.hour}:{message.created_at.minute}] - {message.content}\n" + string

        string = title + string

        transcript = discord.File(io.StringIO(string), "transcript.txt")
        await user.send(file=transcript)
        await channel.edit(name=f"{channel.name}-closed")
        await channel.set_permissions(user, view_messages=False)
        self.removeticket(ctx)



    @ticket.command()
    async def close(self, ctx, confirm="default"):

        if confirm.lower() == "yes":
            await self.closeticket(ctx)
            return

        confirmEmbed = discord.Embed(title="Close Ticket?", description="Type `close` to close the ticket.", color=discord.Color.red())
        await ctx.send(embed=confirmEmbed)

        confirm = await self.client.wait_for("message", check=lambda message: message.author == ctx.author, timeout=30)

        if confirm.content.lower() == "close":
            await self.closeticket(ctx)
            return
        else:
            cancelEmbed = discord.Embed(title="Canceled",
                                        description="You didn't confirm. If you still wish to close the ticket, please try again.")
            await ctx.send(embed=cancelEmbed)



def setup(client):
    client.add_cog(Tickets(client))