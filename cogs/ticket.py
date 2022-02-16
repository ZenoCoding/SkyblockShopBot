import math
from datetime import datetime
from io import BytesIO
from bson.objectid import ObjectId

import discord
from discord.commands import Option, slash_command, SlashCommandGroup
from discord.ext import commands

import utils

active_tickets = utils.db.tickets
config = utils.db.config

# Ticket constants
MAIN_TICKET_EMBED = utils.embed(title="Tickets",
                                description="Click on a button to open a ticket!",
                                thumbnail=utils.Image.CALENDAR.value)

# EDIT THIS
TICKET_CREATION_MESSAGE_EMBED = utils.embed(description='Ticket Created')


class Ticket(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket cog loaded.")
        self.bot.add_view(TicketMessage())
        self.bot.add_view(ManageTicket())
        self.bot.add_view(DeleteTicket())

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.content == '!close':
    #         channel = active_tickets.find_one({'channel_id': message.channel.id})
    #         if channel:
    #             await message.delete()
    #             await manage_support_ticket(message, 'close', 'command')

    ticket = SlashCommandGroup("ticket", "Manages the tickets associated with the server.")

    # Send the ticket message
    @ticket.command(description="Send the ticket message to a specified channel.")
    async def message(self, ctx: discord.ApplicationContext,
                      channel: Option(discord.TextChannel, "Select ticket channel")):
        # Sending main ticket message to chosen channel
        await channel.send(embed=MAIN_TICKET_EMBED, view=TicketMessage())

        # Sending success embed as respond
        success_embed = utils.embed(title="Message Sent :white_check_mark:",
                                    description="The main ticket message has been sent",
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Set the ticket log channel
    @ticket.command(description="Set the ticket log channel to a specified channel.")
    async def set_logging(self, ctx: discord.ApplicationContext,
                          channel: Option(discord.TextChannel, "Select ticket log channel")):
        # Fetching and updating the ticket log
        config.update_one({'_id': ctx.guild.id}, {'$set': {'ticket.logging': channel.id}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Channel Set :white_check_mark:",
                                    description="Ticket log channel has been changed successfully.",
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Set the new ticket channels category
    @ticket.command(description="Set new tickets category")
    async def set_category(self, ctx: discord.ApplicationContext,
                           category: Option(discord.CategoryChannel, "Select category")):
        # Fetching and updating the ticket category
        config.update_one({'_id': ctx.guild.id}, {'$set': {'ticket.category': category.id}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Success :white_check_mark:",
                                    description="Ticket category has been changed successfully.",
                                    thumbnail=utils.Image.SUCCESS.value)
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Sends the paginated thingy
    @ticket.command(description="See the paginated thingy")
    async def list(self, ctx):
        # Fetching all the guild closed tickets
        tickets = active_tickets.find({'guild': ctx.guild.id, 'status': 'closed'})

        # Generating a description for them as start
        desc = makeDescription(tickets, 0)
        embed = utils.embed(title=f"Ticket Log\n[Subject] | [User ID]-[Ticket ID] | [Close date]", description=desc)
        page = f"Page: 1/{math.ceil(active_tickets.count_documents({'status': 'closed'}) / 10)}"
        embed.set_footer(text=page)
        await ctx.respond(embed=embed, view=PaginatedLogs(tickets))

    @slash_command(description="Get the selected log")
    async def get_log(self, ctx: discord.ApplicationContext,
                      ticket_id: Option(str, "32-bit Ticket ID")):
        # Checking if ticket id is correct
        try:
            ticket_object = ObjectId(ticket_id)
        except:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This ticket id is in invalid format.",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Finding a ticket with the given id and check if it exists
        ticket = active_tickets.find_one({'_id': ticket_object})
        if not ticket:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="No ticket found with this id.",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Getting the log from fetched ticket and checking if it has got a log
        log = ticket.get('log', None)
        if not log:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This ticket does not have a log attached to it yet.",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Generating the file for fetched log from database and sending the log as respond
        f = BytesIO(bytes(log, encoding="utf-8"))
        file = discord.File(fp=f, filename="log.txt")

        # Generating embed for the asked log
        ticket_date = ticket['date']
        ticket_subject = ticket['subject']
        user = ticket['user']
        embed = utils.embed(title=f"Here is the ticket log you asked for",
                            description=f"Ticket made by: <@!{user}>\nTicket subject: {ticket_subject}" +
                                        f"\nTicket creation date: {ticket_date}")

        await ctx.respond(embed=embed, file=file)

    # As the description says...
    @ticket.command(name="support_add", description='Adding support role to the tickets')
    async def support_add(self, ctx: discord.ApplicationContext,
                          role: Option(discord.Role, "Select new support role")):
        # Fetching guild supports
        supports = config.find_one({'_id': ctx.guild.id})['ticket']['supports']

        # Checking if role is not already submitted
        if role.id in supports:
            # Sending error embed as respond
            success_embed = utils.embed(title="Error :red_circle:",
                                        description="Role is already in ticket supports")
            await ctx.respond(embed=success_embed, ephemeral=True)
        # Adding new role id to supports and updating database
        supports.append(role.id)
        config.update_one({'_id': ctx.guild.id}, {'$set': {'ticket.supports': supports}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Role Added :white_check_mark:",
                                    description="Role has successfully been added to ticket support roles.",
                                    thumbnail=utils.Image.SUCCESS,
                                    color=discord.Color.green())
        await ctx.respond(embed=success_embed, ephemeral=True)

    @ticket.command(name="support_remove", description='Removing support role from the tickets')
    async def support_remove(self, ctx: discord.ApplicationContext,
                             role: Option(discord.Role, "Select new support role")):
        # Fetching guild supports
        supports = config.find_one({'_id': ctx.guild.id})['ticket']['supports']

        # Checking if role is not submitted
        if role.id not in supports:
            # Sending error embed as respond
            success_embed = utils.embed(title="Error :red_circle:",
                                        description="Role is not in ticket supports")
            await ctx.respond(embed=success_embed, ephemeral=True)
            return

        # Removing role id from supports and updating database
        supports.remove(role.id)
        config.update_one({'_id': ctx.guild.id}, {'$set': {'ticket.supports': supports}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Done :white_check_mark:",
                                    description="Role has successfully removed from ticket support roles.")
        await ctx.respond(embed=success_embed, ephemeral=True)


# Bot views

class TicketMessage(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.ticket_num = 0

    @discord.ui.button(label='Buy coin', style=discord.ButtonStyle.green, row=1, custom_id="persistent_view:buy_coin")
    async def buy_coin_callback(self, _, interaction):
        await createTicket(interaction, subject='Buy Coin')

    @discord.ui.button(label='Buy island', style=discord.ButtonStyle.green, row=1,
                       custom_id="persistent_view:buy_island")
    async def buy_island_callback(self, _, interaction):
        await createTicket(interaction, subject='Buy Island')

    @discord.ui.button(label='Buy minion', style=discord.ButtonStyle.green, row=2,
                       custom_id="persistent_view:buy_minion")
    async def buy_minion_callback(self, _, interaction):
        await createTicket(interaction, subject='Buy Minion')

    @discord.ui.button(label='Need support', style=discord.ButtonStyle.secondary, row=2,
                       custom_id="persistent_view:need_support")
    async def support_callback(self, _, interaction):
        await createTicket(interaction, subject='Support')


class ManageTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close ticket', style=discord.ButtonStyle.red, custom_id="persistent_view:manage_ticket")
    async def callback(self, _, interaction):
        await Ticket.closeTicket(interaction)


class DeleteTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Delete ticket', style=discord.ButtonStyle.red, custom_id="persistent_view:delete_ticket")
    async def callback(self, _, interaction):
        await interaction.channel.delete()


class PaginatedLogs(discord.ui.View):
    def __init__(self, tickets):
        super().__init__(timeout=900000)
        self.tickets = [x for x in tickets]
        self.ticket_count = active_tickets.count_documents({'status': 'closed'})
        self.starting = 0

    def generateEmbed(self, desc):
        embed = utils.embed(title=f"[User ID]-[Ticket ID]-[Log status]", description=desc)
        page = f"Page: {int(self.starting / 10 + 1)}/{math.ceil(self.ticket_count / 10)}"
        embed.set_footer(text=page)
        return embed

    async def changingPage(self, interaction, where: str):
        # Checking if we are at start or at and of pages
        if (self.starting == 0 and where == 'previous') or \
                (active_tickets.count_documents({'status': 'closed'}) < self.starting + 10 and where == 'next'):
            await interaction.response.send_message('Your request cannot be processed since ' +
                                                    'we are at start/end of pages', ephemeral=True)
            return

        # Change the start point based on function
        if where == 'previous':
            self.starting -= 10
        elif where == 'next':
            self.starting += 10

        desc = makeDescription(self.tickets, self.starting)
        embed = self.generateEmbed(desc)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label='Previous Page', style=discord.ButtonStyle.red)
    async def previous_page(self, _, interaction):
        await self.changingPage(interaction, 'previous')

    @discord.ui.button(label='Next Page', style=discord.ButtonStyle.red)
    async def next_page(self, _, interaction):
        await self.changingPage(interaction, 'next')


# Methods

# Create channel method
async def createChannel(guild, name, overwrites=None, category=None):
    if overwrites is None:
        overwrites = {}
    if category == 'unset':
        return

    # Get ticket category channel
    cat = guild.get_channel(category)

    # Checking if category exists, if not, set the ticket category to unset
    if cat is None:

        # Fetching and updating the ticket category
        config.update_one({'_id': guild.id}, {'$set': {'ticket.category': 'unset'}})

        # Create channel and return it
        return await guild.create_text_channel(name, overwrites=overwrites)

    # Create channel and return it
    return await guild.create_text_channel(name, overwrites=overwrites, category=cat)


# Generate string function for ticket number
# Example: 0001-name
def generateNumber(num):
    if num < 10:
        return f'000{num}'
    elif num < 100:
        return f'00{num}'
    elif num < 1000:
        return f'0{num}'
    elif num < 10000:
        return f'{num}'
    else:
        return f'{num}'


async def createTicket(self, interaction, subject="Support"):
    # Trying to find a document where user has an active ticket,
    # so we don't create multiple tickets for one user in a guild
    user_ticket = active_tickets.find_one({'guild': interaction.guild.id,
                                           'user': interaction.user.id,
                                           'status': 'open'})

    already_created_ticket = False
    if user_ticket:
        channel = interaction.guild.get_channel(user_ticket['channel_id'])

        # Changing the ticket to close status if ticket channel doesn't exist
        if not channel:
            active_tickets.update_one({'guild': interaction.guild.id,
                                       'user': interaction.user.id, 'status': 'open'},
                                      {'$set': {'status': 'closed'}})
            already_created_ticket = False
        else:
            already_created_ticket = True

    if not already_created_ticket:
        # Channel overwrites
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }

        # Fetching guild supports
        supports = config.find_one({'_id': interaction.guild.id})['ticket']['supports']

        # Adding all support roles to overwrites
        for support in supports.copy():
            role = interaction.guild.get_role(support)

            # Checking if role exists, if not, remove from supports
            if role is None:
                # Removing role id from supports and updating database
                supports.remove(support)
                continue

            overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        # Updating database for support changes from loop above
        config.update_one({'_id': interaction.guild.id}, {'$set': {'ticket.supports': supports}})

        # Fetching ticket category
        ticket_category = config.find_one({'_id': interaction.guild.id})['ticket']['category']

        # Creating ticket channel
        channel = await createChannel(interaction.guild,
                                      f'{self.generateNumber(active_tickets.count_documents({}))}-' +
                                      f'{interaction.user.name}',
                                      overwrites, ticket_category)

        # Message that gets send after ticket gets created
        await channel.send(embed=TICKET_CREATION_MESSAGE_EMBED, view=ManageTicket())

        # Inserting ticket data into database
        active_tickets.insert_one({'guild': interaction.guild.id,
                                   'channel_id': channel.id,
                                   'user': interaction.user.id,
                                   'status': 'open',
                                   'subject': subject})

        # Sending ticket creation response
        await interaction.response.send_message(f"Successfully done! <#{channel.id}> was made", ephemeral=True)

    elif already_created_ticket:
        await interaction.response.send_message("You already have created 1 ticket", ephemeral=True)


async def closeTicket(interaction):
    # Fetching the log channel from database
    logging_channel = config.find_one({'_id': interaction.guild.id}).get('ticket').get('logging', 'unset')

    # Generating messages log to send/save
    messages = await interaction.channel.history().flatten()
    numbers = "\n".join(
        [f"{message.author} [{message.created_at.hour}:{message.created_at.minute}]: {message.clean_content}"
         for
         message in messages[::-1]])
    f = BytesIO(bytes(numbers, encoding="utf-8"))
    file = discord.File(fp=f, filename="log.txt")

    # Fetching the user with active ticket, so we change the satus to closed
    user = active_tickets.find_one({'guild': interaction.guild.id,
                                    'channel_id': interaction.channel.id,
                                    'status': 'open'})

    # If there is no user that means ticket is already close, so we just send the delete option
    if user is None:
        embed = utils.embed(title='Delete the ticket', description='')
        await interaction.response.send_message(embed=embed, view=DeleteTicket())
        return

    # Closing the ticket as well as putting the log in database
    active_tickets.update_one({'channel_id': interaction.channel.id, 'status': 'open'},
                              {'$set': {'status': 'closed', 'log': numbers, 'date': datetime.now()}})

    # If there is a log channel set, send the log to that channel
    if logging_channel != 'unset':
        # Getting log channel
        channel = interaction.guild.get_channel(logging_channel)

        # Checking if log channel doesn't exist, if not, set it to unset
        if channel is None:
            # Fetching and updating the ticket logging
            config.update_one({'_id': interaction.guild.id}, {'$set': {'ticket.logging': 'unset'}})
        else:
            embed = utils.embed(title=f"{interaction.channel.name}",
                                description="Ticket was closed. Log is below.")
            await channel.send(file=file, embed=embed)

    # Setting the permission for the fetched user
    fetched_user = await interaction.guild.fetch_member(user['user'])
    await interaction.channel.set_permissions(fetched_user,
                                              overwrite=discord.PermissionOverwrite(read_messages=False))

    # Sending delete ticket option to the channel
    embed = utils.embed(title='Delete the ticket', description='')
    await interaction.response.send_message(embed=embed, view=DeleteTicket())


# Making description for paginated logs embed
def makeDescription(tickets, starting):
    description = ''
    for ticket in tickets[starting:starting + 10:]:
        ticket_id = ticket['_id']
        ticket_subject = ticket['subject']
        ticket_date = ticket.get('date') if ticket.get('log', None) else 'doesnt have log'
        user = ticket['user']
        description += f"\n{ticket_subject} | <@!{user}>-{ticket_id} | {ticket_date}\n"

    return description


def setup(bot):
    bot.add_cog(Ticket(bot))
