import re
from datetime import datetime
from enum import Enum
from io import BytesIO

import chat_exporter
import discord
from bson.objectid import ObjectId
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands, pages
from discord.ui import Modal, InputText

import utils

# sys.tracebacklimit = 0

active_tickets = utils.db.tickets
suppliers = utils.db.suppliers
config = utils.db.config

#active_tickets.delete_many({})

# suppliers.update_one({'guild': 859201687264690206,
#                       '_id': 535388059634499587},
#                      {'$set': {'status': 'Available'}})

# Ticket constants
MAIN_TICKET_EMBED = utils.embed(title="Tickets",
                                description="Click on a button to open a ticket!",
                                thumbnail=utils.Image.CALENDAR.value)

# EDIT THIS
TICKET_CREATION_MESSAGE_EMBED = utils.embed(title='', description='')


class TicketStatuses(Enum):
    OPEN = 'Open'
    CONFIRMED = 'Confirmed'
    LISTED = 'Listed'
    DELIVERED = 'Delivered'
    CLOSED = 'Closed'


PAYMENT_METHODS = {
    "Paypal": "We accept only FRIENDS AND FAMILY payments, you get exact amount",
    "Crypto Coins": "We accept your Crypto payments, also you get 10% DISCOUNT",
    "Debit & Credit Card": "We accept your card payments, you get exact amount",
    "Venmo": "We accept your Venmo Payments, you need to pay 10% MORE",
    "Cashapp": "We accept your Cashapp Payments, you need to pay 10% MORE",
    "Physical Amazon ($) Gift cards": "You must to send photo" +
                                      " of physical gift card), you get 50% of its value",
    "Turkey Gift cards": "Amazon.com.tr or something else in Turkey as Payment, you get exact amount",
    "Steam Gift cards": "We accept Steam Gift cards, you get 70% of its value",
    "Paysafe": "We accept Paysafe gift cards, we'll tell you the amount you will get",
    "Other Gift cards": "We accept all other gift cards, we'll tell you the amount you will get"}


class Ticket(commands.Cog):
    def __init__(self, bot: discord.Bot):
        super().__init__()
        self.bot: discord.Bot = bot
        self.rate = bot.get_cog('Rate')

    @staticmethod
    def updateDocument(collection, update_query: dict, updated_fields: dict) -> None:
        collection.update_one(update_query, {'$set': updated_fields})

    @staticmethod
    def checkShareticket(ctx: [discord.ApplicationContext, discord.Interaction]) -> None:
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket:
            return

        supplier_role = ctx.guild.get_role(config.find_one({'_id': ctx.guild.id}).get('supplier', 0))
        if not supplier_role:
            raise utils.CustomError("There is no supplier role set")

        if buyingTicketCheck(ctx.channel_id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        if ticket['subject'] != 'coin':
            raise utils.CustomError("Ticket is not a `coin` selling one")

        if ticket['status'] != TicketStatuses.CONFIRMED.value:
            raise utils.CustomError("Ticket is not in confirmed state")

        if ticket['payment_status'] != 'Paid':
            raise utils.CustomError("Ticket is not paid, first you have to confirm the payment!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket cog loaded.")
        self.bot.add_view(TicketMessage())
        self.bot.add_view(ManageTicket())
        self.bot.add_view(DeleteTicket())
        self.bot.add_view(CloseTicket())
        self.bot.add_view(ClaimTicket(self.rate))
        self.bot.add_view(SelectPaymentMethod())
        self.bot.add_view(ShareTicket(self.rate))
        self.bot.add_view(ConfirmPayment())
        self.bot.add_view(Delivered(self.rate))
        self.bot.add_view(Claimed(self.rate.add_ticket))

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     await askQuestion(message)

    # Send the ticket message
    @slash_command(name="send_ticket_message", description="Send the support message")
    @commands.has_permissions(kick_members=True)
    async def send_ticket_message(self, ctx: discord.ApplicationContext,
                                  channel: Option(discord.TextChannel, "Select ticket channel")):
        # Sending main ticket message to chosen channel
        await channel.send(embed=MAIN_TICKET_EMBED, view=TicketMessage())

        # Sending success embed as respond
        success_embed = utils.embed(title="Message Sent :white_check_mark:",
                                    description="The main ticket message has been sent")
        await ctx.respond(embed=success_embed, ephemeral=True)

    # # Set the ticket log channel
    # @slash_command(name="set_ticket_log", description="Set ticket log channel")
    # @commands.has_permissions(kick_members=True)
    # async def set_ticket_log(self, ctx: discord.ApplicationContext,
    #                          channel: Option(discord.TextChannel, "Select ticket log channel")):
    #     # Fetching and updating the ticket log
    #     self.updateDocument()({'_id': ctx.guild.id}, {'$set': {'ticket.logging': channel.id}})
    #
    #     # Sending success embed as respond
    #     success_embed = utils.embed(title="Done :white_check_mark:",
    #                                 description="Ticket log channel has been changed successfully")
    #     await ctx.respond(embed=success_embed, ephemeral=True)

    # Set the new ticket channels category
    @slash_command(name="set_ticket_category", description="Set new tickets category")
    @commands.has_permissions(kick_members=True)
    async def set_ticket_category(self, ctx: discord.ApplicationContext,
                                  category: Option(discord.CategoryChannel, "Select category")):
        # Fetching and updating the ticket category
        config.find_one_and_update({'_id': ctx.guild.id}, {'$set': {'ticket.category': category.id}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Done :white_check_mark:",
                                    description="Ticket category has been changed successfully")
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Set the ticket listing channel
    @slash_command(name="set_ticket_listing", description="Set ticket log channel")
    @commands.has_permissions(kick_members=True)
    async def set_ticket_listing(self, ctx: discord.ApplicationContext,
                                 channel: Option(discord.TextChannel, "Select ticket log channel")):
        # Fetching and updating the ticket log
        self.updateDocument(config, {'_id': ctx.guild.id}, {'ticket.listing': channel.id})

        # Sending success embed as respond
        success_embed = utils.embed(title="Done :white_check_mark:",
                                    description="Ticket listing channel has been changed successfully")
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Sends the paginated thingy
    @slash_command(name="send_paginated_thingy", description="See the paginated thingy")
    @commands.has_permissions(kick_members=True)
    async def send_paginated_thingy(self, ctx: discord.ApplicationContext):

        # Fetching all the guild closed tickets
        tickets = [f'<@{ticket["user"]}> | Subject: `{ticket["subject"]}` | Date: `{ticket["date"]}` | ' +
                   f'ID: `{ticket["_id"]}`' for ticket in active_tickets.find({'guild': ctx.guild.id,
                                                                               'status': TicketStatuses.CLOSED.value}).sort(
            "_id", -1)]

        if len(tickets) == 0:
            raise utils.CustomError("There is no closed tickets in this guild!")

        # Generating a description for them as start
        list_of_responds_in_10 = [utils.embed(title="This is a list of all closed tickets",
                                              description='\n'.join(tickets[i:i + 10])) for i in
                                  range(0, len(tickets), 10)]
        paginator = pages.Paginator(pages=list_of_responds_in_10)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @slash_command(name="get_log", description="Get the selected log")
    @commands.has_permissions(kick_members=True)
    async def get_log(self, ctx: discord.ApplicationContext,
                      ticket_id: Option(str, "Enter ticket id")):
        # Checking if ticket id is correct
        try:
            ticket_object = ObjectId(ticket_id)
        except:
            raise utils.CustomError('You have entered a wrong ticket id')

        # Finding a ticket with the given id and check if it exists
        ticket = active_tickets.find_one({'_id': ticket_object})
        if not ticket:
            raise utils.CustomError("No ticket found with that id")

        # Getting the log from fetched ticket and checking if it has got a log
        log = ticket.get('log', None)
        if not log:
            raise utils.CustomError("This ticket doesnt have a saved log")

        # Generating the file for fetched log from database and sending the log as respond
        f = BytesIO(bytes(log, encoding="utf-8"))
        file = discord.File(fp=f, filename="log.html")

        # Generating embed for the asked log
        ticket_date = ticket['date']
        ticket_subject = ticket['subject']
        user = ticket['user']
        embed = utils.embed(title=f"Here is the ticket log you asked for",
                            description=f"Ticket made by: <@!{user}>\nTicket subject: {ticket_subject}" +
                                        f"\nTicket creation date: {ticket_date}")

        await ctx.respond(embed=embed, file=file)

    # As the description says...
    @slash_command(name="support-add", description='Adding support role to the tickets')
    @commands.has_permissions(kick_members=True)
    async def support_add(self, ctx: discord.ApplicationContext,
                          role: Option(discord.Role, "Select new support role")):
        # Fetching guild supports
        supports = config.find_one({'_id': ctx.guild.id})['supports']

        # Checking if role is not already submitted
        if role.id in supports:
            # Sending error embed as respond
            raise utils.CustomError("Role is already in ticket supports")

        # Adding new role id to supports and updating database
        supports.append(role.id)
        config.find_one_and_update({'_id': ctx.guild.id}, {'$set': {'supports': supports}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Done :white_check_mark:",
                                    description="Role has successfully added to ticket supports")
        await ctx.respond(embed=success_embed, ephemeral=True)

    @slash_command(name="support-remove", description='Removing support role from the tickets')
    @commands.has_permissions(kick_members=True)
    async def support_remove(self, ctx: discord.ApplicationContext,
                             role: Option(discord.Role, "Select new support role")):
        # Fetching guild supports
        supports = config.find_one({'_id': ctx.guild.id})['supports']

        # Checking if role is not submitted
        if role.id not in supports:
            # Sending error embed as respond
            success_embed = utils.embed(title="Error :red_circle:",
                                        description="Role is not in ticket supports")
            await ctx.respond(embed=success_embed, ephemeral=True)
            return

        # Removing role id from supports and updating database
        supports.remove(role.id)
        config.find_one_and_update({'_id': ctx.guild.id}, {'$set': {'supports': supports}})

        # Sending success embed as respond
        success_embed = utils.embed(title="Done :white_check_mark:",
                                    description="Role has successfully removed from ticket supports")
        await ctx.respond(embed=success_embed, ephemeral=True)

    # Get ticket info (If it is about products)
    @slash_command(name="info", description='Get info of the ticket')
    @commands.has_permissions(kick_members=True)
    async def info(self, ctx: discord.ApplicationContext):
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket:
            return
        if buyingTicketCheck(ctx.channel_id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        await ctx.respond(embed=generateInfo(ctx.channel_id))

    # Edit ticket info (If it is about products)
    @slash_command(name="edit", description='Change product information of ticket')
    @commands.has_permissions(kick_members=True)
    async def edit(self, ctx: discord.ApplicationContext):
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket:
            return
        if buyingTicketCheck(ctx.channel_id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        await ctx.response.send_modal(modal=createModal(ticket['subject'], ticket)(title="Change product info:"))

    valid_payment_methods = [discord.OptionChoice(name=name) for i, (name, _) in enumerate(PAYMENT_METHODS.items())]

    # Confirm ticket info and set it as paid (If it is about products)
    @slash_command(name="confirmpayment", description='Confirm the ticket for the listing')
    @commands.has_permissions(kick_members=True)
    async def confirmpayment(self, ctx: discord.ApplicationContext,
                             paymentmethod: Option(str,
                                                   "Customer's payment method (Required if has not been selected)",
                                                   required=False, choices=valid_payment_methods)):
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket:
            return

        if buyingTicketCheck(ctx.channel_id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        if (not ticket.get('payment_method', None)) & (not paymentmethod):
            raise utils.CustomError("Ticket does not have payment method, you have to select one")

        if ticket['payment_status'] == 'Paid':
            raise utils.CustomError("You cannot re-confirm a confirmed ticket")

        if paymentmethod:
            self.updateDocument(active_tickets, {'channel': ctx.channel.id}, {'status': TicketStatuses.CONFIRMED.value,
                                                                              'payment_status': 'Paid',
                                                                              'payment_method': paymentmethod})
        else:
            self.updateDocument(active_tickets, {'channel': ctx.channel.id}, {'status': TicketStatuses.CONFIRMED.value,
                                                                              'payment_status': 'Paid'})

        embed = utils.embed(title="Ticket successfully confirmed!", description="")
        await ctx.response.send_message(embed=embed, ephemeral=True)

        message: discord.Message = await ctx.channel.fetch_message(ticket['message'])
        await message.edit(embed=generateInfo(ctx.channel.id))

    @slash_command(name="resetpayment", description='Reset payment status')
    @commands.has_permissions(kick_members=True)
    async def resetpayment(self, ctx: discord.ApplicationContext):
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket:
            return

        if buyingTicketCheck(ctx.channel_id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        if ticket['status'] not in [TicketStatuses.CONFIRMED.value, TicketStatuses.OPEN.value]:
            raise utils.CustomError("You cannot reset a not confirmed ticket!")

        self.updateDocument(active_tickets, {'channel': ctx.channel.id}, {'status': TicketStatuses.OPEN.value,
                                                                          'payment_status': 'Waiting payment'})

        message: discord.Message = await ctx.channel.fetch_message(ticket['message'])
        await message.edit(embed=generateInfo(ctx.channel.id))

        await ctx.respond(embed=utils.embed(title="Successfully reset the payment status!",
                                            description=''), ephemeral=True)

    @slash_command(name="shareticket", description='Share ticket in listing channel')
    @commands.has_permissions(kick_members=True)
    async def shareticket(self, ctx: discord.ApplicationContext):
        self.checkShareticket(ctx)

        await ctx.respond("**Please confirm the data first!**", embed=generateInfo(ctx.channel_id),
                          view=ShareTicket(self.rate),
                          ephemeral=True)

    # Send the ticket message
    @slash_command(description="Lists all of the payment in whatever condition")
    @commands.has_permissions(kick_members=True)
    async def payment_list(self, ctx: discord.ApplicationContext,
                           condition: Option(str,
                                             "The condition of ticket",
                                             choices=[discord.OptionChoice(name="Checking payment"),
                                                      discord.OptionChoice(name="Paid")])):
        tickets = active_tickets.find({'$or': [{'status': TicketStatuses.CONFIRMED.value,
                                                'guild': ctx.guild.id,
                                                'payment_status': condition},
                                               {'status': TicketStatuses.OPEN.value,
                                                'guild': ctx.guild.id,
                                                'payment_status': condition}]})

        tickets_count = active_tickets.count_documents({'$or': [{'status': TicketStatuses.CONFIRMED.value,
                                                                 'guild': ctx.guild.id,
                                                                 'payment_status': condition},
                                                                {'status': TicketStatuses.OPEN.value,
                                                                 'guild': ctx.guild.id,
                                                                 'payment_status': condition}]})

        if tickets_count == 0:
            raise utils.CustomError("No tickets in this status")

        # Defining paginator
        if condition == 'Paid':
            respond_pages = [f"<#{ticket['channel']}> | Check" +
                             f" ticket details and use `/shareticket`" for ticket in tickets]
        else:
            respond_pages = [f"<#{ticket['channel']}> | Check" +
                             f" payment and when confirmed: `/confirmpayment`" for ticket in tickets]

        list_of_responds_in_10 = [utils.embed(title="Payments waiting for actions",
                                              description='\n'.join(respond_pages[i:i + 10])) for i in
                                  range(0, len(respond_pages), 10)]
        paginator = pages.Paginator(pages=list_of_responds_in_10)

        # Sending ticket payment list message
        await paginator.respond(ctx.interaction, ephemeral=False)

    @slash_command(name="delivered", description='When supplier delivered the ticket')
    @commands.has_permissions(kick_members=True)
    async def delivered(self, ctx: discord.ApplicationContext):
        ticket = active_tickets.find_one({'channel': ctx.channel.id})
        if not ticket or ticket['status'] == TicketStatuses.DELIVERED.value:
            return

        supplier = suppliers.find_one({'guild': ctx.guild.id,
                                       '_id': ctx.user.id})
        if ticket.get('supplier', None) and (supplier['_id'] != ticket.get('supplier', None)):
            raise utils.CustomError('You are not this ticket\'s supplier!')

        if buyingTicketCheck(ctx.channel.id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        await ctx.respond(ctx.guild.get_member(ticket['user']).mention,
                          embed=utils.embed(
                              title="Did you got your product?",
                              description="If you did please press the button below to proceed"
                          ),
                          view=Claimed(self.rate.add_ticket)
                          )


# Bot views
def createModal(subject, ticket=None):
    class BuyModal(Modal):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            # Adding field to modal based on subject
            if subject == 'coin':
                self.add_item(InputText(label="Coin amount", placeholder="Example: 100m",
                                        value=ticket['product'] if ticket is not None else None))

            if subject == 'island':
                self.add_item(InputText(label="Island number", placeholder="Example: 87",
                                        value=ticket['product'] if ticket is not None else None))

            if subject == 'minion':
                self.add_item(InputText(label="Minion:", placeholder="Example: 10x Snow",
                                        value=ticket['product'] if ticket is not None else None))

            # if not ticket:
            self.add_item(InputText(label="IGN", placeholder="Your in game name",
                                    value=ticket['ign'] if ticket is not None else None))

        async def callback(self, interaction: discord.Interaction):
            product = self.children[0].value
            if subject == 'coin':
                if not re.match("^[\d.]*[mMbB]$", product):
                    return await interaction.response.send_message(
                        embed=utils.embed(title="Invalid amount of coins",
                                          description="Please follow this format:\n100m\n1b\n1000M"), ephemeral=True)

                if product.lower().endswith('b'):
                    product = f'{int(float(product[:-1]) * 1000)}m'

            if not ticket:
                await createTicket(interaction,
                                   subject=subject,
                                   product=[subject, product],
                                   ign=self.children[1].value)
            else:
                submitData(interaction.channel.id, [subject, product])
                await interaction.response.send_message(embed=generateInfo(interaction.channel.id), ephemeral=True)
                message: discord.Message = await interaction.channel.fetch_message(ticket['message'])
                await message.edit(embed=generateInfo(interaction.channel.id))

    return BuyModal


class Claimed(utils.CustomView):
    def __init__(self, add_ticket):
        super().__init__(timeout=None)
        self.add_ticket = add_ticket

    @discord.ui.button(label='Yes, I got it!', style=discord.ButtonStyle.primary,
                       custom_id="persistent_view:claim_ticket")
    async def callback(self, _, interaction: discord.Interaction):
        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        if not ticket or ticket['status'] == TicketStatuses.DELIVERED.value:
            return await interaction.message.delete()

        supplier = ticket.get('supplier', None)
        if supplier and interaction.user.id == ticket['supplier'] and ticket['user'] != ticket['supplier'] \
                and not interaction.user.guild_permissions.kick_members:
            raise utils.CustomError("You cannot mark this ticket as claimed!")

        await interaction.response.send_message(
            embed=utils.embed(
                title="Transfer successfully completed!",
                description="""
                Thank you for choosing us for buying coins and also
                thank you for supporting my education. I hope you enjoy
                with your coins in skyblock!

                **Please leave you review message by typing !vouch in
                chat**

                **Please use vouch command like below**:

                ```!vouch <score> (out of 5) <message>```

                **Example**: !vouch 5 I got my +120M thank you so much.
                """
            )
        )

        if supplier:
            Ticket.updateDocument(suppliers,
                                  {'guild': interaction.guild.id, '_id': supplier},
                                  {'status': 'Available'})
            self.add_ticket(interaction.guild.get_member(supplier), int(ticket['product'][:-1]))
            await interaction.channel.set_permissions(interaction.guild.get_member(supplier), read_messages=False,
                                                      send_messages=False)

        Ticket.updateDocument(active_tickets, {'channel': interaction.channel.id},
                              {'status': TicketStatuses.DELIVERED.value})

        await interaction.message.delete()

        # Call supplier method


class ShareTicket(utils.CustomView):
    def __init__(self, rate):
        super().__init__(timeout=None)
        self.rate = rate

    @discord.ui.button(label='Share Ticket', style=discord.ButtonStyle.primary,
                       custom_id="persistent_view:share_ticket")
    async def share(self, _, interaction: discord.Interaction):
        try:
            Ticket.checkShareticket(interaction)
        except Exception as e:
            raise e

        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        if ticket['status'] == TicketStatuses.DELIVERED.value:
            return await interaction.message.delete()

        Ticket.updateDocument(active_tickets, {'channel': interaction.channel.id},
                              {'status': TicketStatuses.LISTED.value})

        embed = utils.embed(title="New ticket just got listed!", description="")
        embed.add_field(name="Product", value=f"{ticket['product']} {ticket['subject']}")
        await interaction.response.send_message(embed=utils.embed(title="Ticket successfully listed!", description=""),
                                                ephemeral=True)

        # await interaction.message.delete()
        role: discord.Role = interaction.guild.get_role(config.find_one({'_id': interaction.guild.id})['supplier'])
        await interaction.channel.set_permissions(
            role,
            overwrite=discord.PermissionOverwrite(send_messages=False, read_messages=True))

        await interaction.channel.send(embed=embed, view=ClaimTicket(self.rate))

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary,
                       custom_id="persistent_view:cancel")
    async def cancel(self, _, interaction: discord.Interaction):
        await interaction.message.delete()


class Delivered(utils.CustomView):
    def __init__(self, rate):
        super().__init__(timeout=None)
        self.rate = rate

    @discord.ui.button(label="Delivered", style=discord.ButtonStyle.primary,
                       custom_id="persistent_view:delivered_ticket")
    async def callback(self, _, interaction: discord.Interaction):
        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        if not ticket or ticket['status'] == TicketStatuses.DELIVERED.value:
            return
        if not ticket.get('supplier', None):
            raise utils.CustomError("Wierd! This ticket doesnt have a supplier!")

        if interaction.user.id != ticket['supplier']:
            raise utils.CustomError('You are not this ticket\'s supplier!')

        if buyingTicketCheck(interaction.channel.id)[0]:
            raise utils.CustomError("Ticket doesn't have any products")

        await interaction.response.send_message(interaction.guild.get_member(ticket['user']).mention,
                                                embed=utils.embed(
                                                    title="Did you got your product?",
                                                    description="If you did please press the button below to proceed"
                                                ),
                                                view=Claimed(self.rate.add_ticket)
                                                )


class ClaimTicket(utils.CustomView):
    def __init__(self, rate):
        super().__init__(timeout=None)
        self.rate = rate

    @discord.ui.button(label='Claim Ticket', style=discord.ButtonStyle.primary,
                       custom_id="persistent_view:supplier_claim_ticket")
    async def callback(self, _, interaction: discord.Interaction):
        supplier = suppliers.find_one({'guild': interaction.guild.id,
                                       '_id': interaction.user.id})
        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        print(ticket)
        if not supplier:
            raise utils.CustomError("You are not a supplier!")

        if supplier['status'] == 'Busy':
            raise utils.CustomError("You already have claimed 1 ticket!")

        if ticket.get('supplier', None):
            raise utils.CustomError("Ticket already has a supplier!")

        if ticket['status'] == TicketStatuses.LISTED.value:
            await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

            await interaction.channel.set_permissions(
                interaction.guild.get_role(config.find_one({'_id': interaction.guild.id})['supplier']),
                read_messages=False,
                send_messages=False)

            await interaction.response.send_message(f"{interaction.user.mention}",
                                                    embed=generateInfo(interaction.channel.id),
                                                    ephemeral=True)

            embed = utils.embed(title='',
                                thumbnail=interaction.user.avatar, description='')
            embed.set_author(name=f"{interaction.user.name} Accepted your ticket", icon_url=interaction.user.avatar.url)
            embed.add_field(name=":star: Level", value=f"{supplier['level']}")
            embed.add_field(name=":shopping_cart: Sold", value=f"{supplier['tickets']}")

            await interaction.message.delete()

            Ticket.updateDocument(active_tickets, {'channel': interaction.channel.id}, {'status': 'claimed',
                                                                                        'supplier': supplier['_id']})
            Ticket.updateDocument(suppliers,
                                  {'guild': interaction.guild.id, '_id': interaction.user.id},
                                  {'status': 'Busy'})

            await interaction.channel.send(embed=embed, view=Delivered(self.rate))

        else:
            await interaction.message.delete()


class TicketMessage(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)
        self.ticket_num = 0

    @discord.ui.button(label='Buy coin', style=discord.ButtonStyle.green, row=1, custom_id="persistent_view:buy_coin")
    async def buy_coin_callback(self, _, interaction):
        await interaction.response.send_modal(createModal('coin')(title="Coin purchase form"))

    @discord.ui.button(label='Buy island', style=discord.ButtonStyle.green, row=1,
                       custom_id="persistent_view:buy_island")
    async def buy_island_callback(self, _, interaction):
        await interaction.response.send_modal(createModal('island')(title="Island purchase form"))

    @discord.ui.button(label='Buy minion', style=discord.ButtonStyle.green, row=2,
                       custom_id="persistent_view:buy_minion")
    async def buy_minion_callback(self, _, interaction):
        await interaction.response.send_modal(createModal('minion')(title="Minion purchase form"))

    @discord.ui.button(label='Need support', style=discord.ButtonStyle.secondary, row=2,
                       custom_id="persistent_view:need_support")
    async def support_callback(self, _, interaction):
        await createTicket(interaction, subject='Support')


class SelectPaymentMethodDropDown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=label, description=description) for i, (label, description) in
                   enumerate(PAYMENT_METHODS.items())]

        super().__init__(custom_id="persistent_view:payment_dropdown",
                         placeholder="Choose your payment method",
                         min_values=1,
                         max_values=1,
                         options=options,
                         )

    async def callback(self, interaction: discord.Interaction):
        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        if ticket and \
                (ticket.get('payment_status', None) != "Waiting payment" or ticket['user'] != interaction.user.id):
            raise utils.CustomError("You cannot change payment method!")

        Ticket.updateDocument(active_tickets,
                              {'channel': interaction.channel.id},
                              {'payment_method': self.values[0]})

        message: discord.Message = await interaction.channel.fetch_message(ticket['message'])
        await message.edit(embed=generateInfo(interaction.channel.id))

        await interaction.response.send_message(
            f"{interaction.user.mention}",
            embed=utils.embed(
                title=f"Payment method has been successfully set/changed to {self.values[0]}",
                description=f'**{self.values[0]} description**:\n{PAYMENT_METHODS[self.values[0]]}' +
                            f'\n**Press the button below, after you made the payment**'), view=ConfirmPayment())


class SelectPaymentMethod(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)

        # Adds the dropdown to our view object.
        self.add_item(SelectPaymentMethodDropDown())


class ConfirmPayment(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="I paid", style=discord.ButtonStyle.primary, custom_id="persistent_view:confirm_payment")
    async def callback(self, _, interaction: discord.Interaction):
        ticket = active_tickets.find_one({'channel': interaction.channel.id})
        if ticket and ticket.get('payment_status', None) != 'Waiting payment':
            raise utils.CustomError("You cannot confirm payment now!")

        if ticket['user'] != interaction.user.id:
            raise utils.CustomError("You cannot click on I paid!")

        Ticket.updateDocument(active_tickets,
                              {'channel': interaction.channel.id},
                              {'payment_status': 'Checking payment'})

        await interaction.response.send_message(
            embed=utils.embed(title="Successfully done :white_check_mark: ",
                              description="Thank you for your payment, please be patient, Staff team will soon" +
                                          " respond.\n"))

        message: discord.Message = await interaction.channel.fetch_message(ticket['message'])
        await message.edit(embed=generateInfo(interaction.channel.id))


class ManageTicket(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Close ticket', style=discord.ButtonStyle.red, custom_id="persistent_view:manage_ticket")
    async def callback(self, _, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.kick_members:
            raise utils.CustomError('You dont have permission to use this button')

        ticket = active_tickets.find_one({'channel': interaction.channel.id})

        if ticket and ticket.get('payment_status'):
            if (ticket['payment_status'] == 'Paid' or ticket['payment_status'] == 'Checking payment') and \
                    ticket['status'] != TicketStatuses.DELIVERED.value:
                raise utils.CustomError("You cannot do that since its Paid and not Delivered!")

        embed = utils.embed(
            title="",
            description=f"""Hello {interaction.guild.get_member(ticket['user']).mention if ticket else ''}
            *A staff has evaluated the ticket to be completed and proposes closing the ticket.*

            If you do not have any further questions and your problems are solved, please close the """ +
                        "ticket below by pressing the close button")

        embed.set_author(name=f"{interaction.guild.name} | SUPPORT", icon_url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed, view=CloseTicket())


class CloseTicket(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='✔ Close', style=discord.ButtonStyle.red, custom_id="persistent_view:close_ticket")
    async def yes(self, _, interaction):
        # transcript_file = discord.File(fp=BytesIO(bytes(transcript[222::], encoding="utf-8")),
        #                                filename=f"{interaction.channel.name}.html")

        # Fetching the user with active ticket, so we change the satus to closed
        user = active_tickets.find_one({'channel': interaction.channel.id,
                                        'status': {'$ne': TicketStatuses.CLOSED.value}})

        # Setting the permission for the fetched user
        if user:
            fetched_user = interaction.guild.get_member(user['user'])
            await interaction.channel.set_permissions(fetched_user,
                                                      overwrite=discord.PermissionOverwrite(read_messages=False))

        # Sending delete ticket option to the channel
        embed = utils.embed(title='Ticket closed, Do you want to delete the ticket?', description='')
        await interaction.response.send_message(embed=embed, view=DeleteTicket())

        # If there is no user that means ticket is already close, so we just send the delete option
        if user is None:
            return

        # Fetching the log channel from database
        logging_channel = config.find_one({'_id': interaction.guild.id}).get('ticket').get('logging', None)

        # Getting channel history
        messages = await interaction.channel.history().flatten()
        # Extracting log to .txt
        numbers = "\n".join(
            [f"{message.author} [{message.created_at.hour}:{message.created_at.minute}]: {message.clean_content}" for
             message in messages[::-1]])
        f = BytesIO(bytes(numbers, encoding="utf-8"))
        file = discord.File(fp=f, filename="log.txt")

        # Extracting log to .html
        transcript = await chat_exporter.export(interaction.channel)

        # Closing the ticket as well as putting the log in database
        Ticket.updateDocument(active_tickets,
                              {'channel': interaction.channel.id, 'status': {'$ne': TicketStatuses.CLOSED.value}},
                              {'status': TicketStatuses.CLOSED.value, 'log': numbers, 'html_log': transcript[222::]})

        # If there is a log channel set, send the log to that channel
        if logging_channel:

            # Getting log channel
            channel = interaction.guild.get_channel(logging_channel)

            # Checking if log channel doesn't exist, if not, set it to unset
            if channel is None:
                # Fetching and updating the ticket logging
                config.find_one_and_update({'_id': interaction.guild.id}, {'$set': {'ticket.logging': None}})
            else:
                embed = utils.embed(title=f"{interaction.channel.name}",
                                    description=f"Ticket was closed. Log is above." +
                                                (f"\n**Buyer IGN**: {user['ign']}\n**Product**: {user['product']}"
                                                 if user.get('product', None) else ''))
            await channel.send(embed=embed, file=file)

    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.secondary,
                       custom_id="persistent_view:close_ticket_delete")
    async def no(self, _, interaction):
        await interaction.message.delete()


class DeleteTicket(utils.CustomView):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red, custom_id="persistent_view:delete_ticket")
    async def callback(self, _, interaction):
        if not interaction.user.guild_permissions.kick_members:
            raise utils.CustomError('You dont have permission to use this button')

        await interaction.channel.delete()


# Methods


def buyingTicketCheck(channel_id):
    ticket = active_tickets.find_one({'channel': channel_id})
    if not ticket.get('product', None):
        embed = utils.embed(title="Error!", description='')
        embed.description = "It appears there is no specific info about this ticket"
        return True, embed
    return False, ''


# Generate info for product tickets
def generateInfo(channel_id) -> discord.Embed:
    ticket = active_tickets.find_one({'channel': channel_id})

    embed = utils.embed(title="Ticket information", description='')
    embed.add_field(name="In Game Name", value=f"{ticket['ign']}")
    embed.add_field(name="Product", value=f"{ticket['product']} {ticket['subject']}")
    embed.add_field(name="Payment status", value=f"{ticket['payment_status']}")
    embed.add_field(name="Payment method",
                    value=f"{'Not selected' if not ticket.get('payment_method', None) else ticket['payment_method']}")
    return embed


# Create channel method
async def createChannel(guild, name, overwrites=None, category=None) -> discord.TextChannel:
    if overwrites is None:
        overwrites = {}
    # if category == 'unset':
    #     return

    # Get ticket category channel
    cat = guild.get_channel(category)

    # Checking if category exists, if not, set the ticket category to unset
    if cat is None:
        # Fetching and updating the ticket category
        config.find_one_and_update({'_id': guild.id}, {'$set': {'ticket.category': None}})

        # Create channel and return it
        return await guild.create_text_channel(name, overwrites=overwrites)

    # Create channel and return it
    return await guild.create_text_channel(name, overwrites=overwrites, category=cat)


# Generate string function for ticket number
# Example: 0001-name
def generateNumber(num) -> str:
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


def submitData(channel_id, product) -> None:
    if active_tickets.find_one({'channel': channel_id}).get('payment_status', None):
        return Ticket.updateDocument(active_tickets, {'channel': channel_id}, {'product': product[1]})
    Ticket.updateDocument(active_tickets,
                          {'channel': channel_id},
                          {'payment_status': 'Waiting payment', 'product': product[1]})


async def createTicket(interaction, ign=None, product=None, subject="Support") -> None:
    # Trying to find a document where user has an active ticket,
    # so we don't create multiple tickets for one user in a guild
    user_ticket = active_tickets.find_one({'guild': interaction.guild.id,
                                           'user': interaction.user.id,
                                           'status': {'$ne': TicketStatuses.CLOSED.value}
                                           })

    already_created_ticket = False
    if user_ticket:
        channel = interaction.guild.get_channel(user_ticket['channel'])

        # Changing the ticket to close status if ticket channel doesn't exist
        if not channel:
            Ticket.updateDocument(active_tickets,
                                  {'guild': interaction.guild.id,
                                   'user': interaction.user.id,
                                   'status': {'$ne': TicketStatuses.CLOSED.value}},
                                  {'status': TicketStatuses.CLOSED.value})
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
        supports = config.find_one({'_id': interaction.guild.id})['supports']

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
        config.find_one_and_update({'_id': interaction.guild.id}, {'$set': {'supports': supports}})

        # Fetching ticket category
        ticket_category = config.find_one({'_id': interaction.guild.id})['ticket']['category']

        # Creating ticket channel
        channel = await createChannel(interaction.guild,
                                      f'{generateNumber(active_tickets.count_documents({}))}-' +
                                      f'{interaction.user.name}',
                                      overwrites, ticket_category)
        try:
            # Sending ticket creation response
            await interaction.response.send_message(f"Successfully done! <#{channel.id}> was made", ephemeral=True)
        except Exception:
            if channel:
                return await channel.delete()
            raise utils.CustomError("Something happened when creating ticket, please try again later!")

        # Message that gets send after ticket gets created
        await channel.send(embed=TICKET_CREATION_MESSAGE_EMBED, view=ManageTicket())

        # Inserting ticket data into database
        active_tickets.insert_one({'guild': interaction.guild.id,
                                   'channel': channel.id,
                                   'user': interaction.user.id,
                                   'status': TicketStatuses.OPEN.value,
                                   'subject': subject,
                                   'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                                   'ign': ign})
        if product:
            # Inserting product data
            submitData(channel.id, product)

            message: discord.Message = await channel.send(embed=generateInfo(channel.id))

            Ticket.updateDocument(active_tickets, {'channel': channel.id}, {'message': message.id})
            await channel.send(view=SelectPaymentMethod())

            await message.pin()

    else:
        raise utils.CustomError("You already have created 1 ticket")


# Making description for paginated logs embed
def makeDescription(tickets, starting) -> str:
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