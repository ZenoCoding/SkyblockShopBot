import datetime
import math
from functools import partial

import discord
from discord.commands import Option, SlashCommandGroup
from discord.ext import pages
from discord.ext.commands import has_permissions, slash_command
from pymongo.errors import DuplicateKeyError

import utils
import image

config = utils.db.config
suppliers = utils.db.suppliers

# Constants
INCREMENT = 0.01

calc_xp = lambda l: 250 * 1.5 ** (l - 1)


class Rate(discord.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    def get_guild_global(guild: discord.Guild):
        return config.find_one({"_id": guild.id})['rate']

    @staticmethod
    def add_user(user: discord.Member):
        start_data = {
            "user": user.id,
            "guild": user.guild.id,
            "rate": Rate.get_guild_global(user.guild)['starting'],
            "owed": 0,
            "xp": 0,
            "level": 1,
            "sold": 0,
            "paid": 0,
            "tickets": 0,
            "bonus": 0,
            "date": datetime.datetime.now(),
            "retired": False
        }
        suppliers.insert_one(start_data)

    @staticmethod
    def retire_user(user: discord.Member):
        suppliers.update_one({"user": user.id, "guild": user.guild.id}, {"$set": {f"retired": True}})

    @staticmethod
    def get_user(user: discord.Member):
        return suppliers.find_one({"user": user.id, "guild": user.guild.id})

    @staticmethod
    def user_is_supplier(user: discord.Member):
        if suppliers.find_one({"user": user.id, "guild": user.guild.id}) is not None:
            return True
        return False

    @staticmethod
    async def send_levelup(user: discord.Member):
        user_data = suppliers.find_one({'user': user.id, 'guild': user.guild.id})
        guild_rate = Rate.get_guild_global(user.guild)
        levelup_embed = utils.embed(title="Level Up! :partying_face:",
                                    description=f"You have reached level `{user_data['level']}` on {user.guild.name}!\n"
                                                f"This means that you now have a rate of `{min((user_data['level'] - 1) * INCREMENT + guild_rate['starting'], guild_rate['cap'])}`",
                                    color=discord.Color.orange())
        await user.send(embed=levelup_embed)

    @staticmethod
    async def add_ticket(user: discord.Member,  # Supplier who handled the ticket
                   amount: float):  # Amount the ticket is worth
        if not Rate.user_is_supplier(user):
            raise ValueError("User passed must be a supplier")  # If you don't pass a supplier

        guild_rate = Rate.get_guild_global(user.guild)
        user_data = Rate.get_user(user)
        level = user_data['level']
        # Leveling
        if amount + user_data['xp'] >= calc_xp(level):
            overflow = (amount + user_data['xp']) - calc_xp(level)
            level = user_data['level'] + 1
            # If there is still more overflow after the level is reached
            while overflow >= calc_xp(level):
                overflow = (overflow) - calc_xp(level)
                level += 1
            suppliers.update_one({"user": user.id, "guild": user.guild.id}, {"$set": {"xp": overflow, "level": level}})
            await Rate.send_levelup(user)
        else:
            suppliers.update_one({"user": user.id, "guild": user.guild.id}, {"$inc": {"xp": amount}})

        rate = round(min((level - 1) * INCREMENT + guild_rate['starting'], guild_rate['cap']), 2)
        bonus = user_data['bonus'] + 1  # we add one because bonus is based around 0

        suppliers.update_one({"user": user.id, "guild": user.guild.id},
                             {"$inc": {"tickets": 1, "owed": rate * amount * bonus, "sold": amount},
                              "$set": {"rate": rate}})

    supplier = SlashCommandGroup("supplier", "Commands pertaining to suppliers.")

    # Test command for devs or admin
    @has_permissions(administrator=True)
    @slash_command(name="simulate_ticket", description="Dev tool for simulating a ticket completion.")
    async def simulate_ticket(self, ctx: discord.ApplicationContext,
                              user: Option(discord.Member, name="user"),
                              amount: Option(int, name="amount",
                                             description="Amount the ticket to be simulated is worth.")):

        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the"
                                                  " `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        await Rate.add_ticket(user, amount)
        success_embed = utils.embed(title="Ticket Simulated :white_check_mark:",
                                    description=f"A ticket with a worth of `{amount}M` has been simulated for the user {user.mention}")
        await ctx.respond(embed=success_embed)

    @has_permissions(administrator=True)
    @supplier.command(name="global_rate", description="Set/view the global rate for all sellers.")
    async def edit_global(self, ctx: discord.ApplicationContext,
                          func: Option(str, name="function", choices=["view", "starting", "cap"]),
                          amount: Option(str, name="amount", description="The amount you wish to set to",
                                         required=False)):
        if (func == "starting" or func == "cap") and not utils.is_num(amount):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="When using functions `starting` and `cap` you must specify a valid amount of the type `float`",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        if func == "view":
            view_embed = utils.embed(title="Global Rates",
                                     thumbnail=utils.Image.BAR_GRAPH.value)
            view_embed.add_field(name="Starting Value",
                                 value=f"The starting global rate is `${Rate.get_guild_global(ctx.guild)['starting']}`")
            view_embed.add_field(name="Cap Value",
                                 value=f"The global cap rate is `${Rate.get_guild_global(ctx.guild)['cap']}`")
            await ctx.respond(embed=view_embed)
        elif func == "starting":
            config.update_one({"_id": ctx.guild.id}, {"$set": {"rate.starting": float(amount)}})
            success_embed = utils.embed(title="Edit Successful :white_check_mark:",
                                        description=f"The starting global rate has been changed to `${amount}/M`",
                                        thumbnail=utils.Image.SUCCESS.value,
                                        color=discord.Color.green())
            await ctx.respond(embed=success_embed)
        elif func == "cap":
            config.update_one({"_id": ctx.guild.id}, {"$set": {"rate.cap": float(amount)}})
            success_embed = utils.embed(title="Edit Successful :white_check_mark:",
                                        description=f"The global cap rate has been changed to `${amount}/M`",
                                        thumbnail=utils.Image.SUCCESS.value,
                                        color=discord.Color.green())
            await ctx.respond(embed=success_embed)

    @supplier.command(name="role", description="Set the buyer role of your server.")
    @has_permissions(administrator=True)
    async def set_supplier_role(self, ctx,
                                role: Option(discord.Role, "Pick a role in the server.")):
        embed = utils.embed(title="Set Supplier Role  :white_check_mark:",
                            description=f"The supplier role has been set to {ctx.guild.get_role(role.id).mention}",
                            color=discord.Color.blue())
        await ctx.respond(embed=embed, ephemeral=True)

        config.update_one({"_id": ctx.guild.id}, {"$set": {"supplier": int(role.id)}})

    @supplier.command(name="list", description="List all suppliers in the current guild")
    async def list(self, ctx: discord.ApplicationContext):
        supplier_list = suppliers.find({"guild": ctx.guild.id})
        supplier_list = sorted(supplier_list, key=lambda i: (i['level'], i['xp']), reverse=True)

        pages_list = []

        page_num = 0
        modulo = 0
        if len(supplier_list) < 1:
            nan_embed = utils.embed(title="Whoops! No sellers found!",
                                    description="**It looks like there's no one here. Try using `/supplier add` to add some people!**",
                                    color=discord.Color.red(),
                                    thumbnail=utils.Image.ERROR.value)
            pages_list = [nan_embed]
        else:
            for supplier in supplier_list:
                modulo += 1
                modulo = modulo % 10

                # New page
                if modulo == 1:
                    page_num += 1
                    page_embed = utils.embed(
                        title=f"Supplier Leaderboard | Page {page_num}/{math.ceil(len(supplier_list) / 10)}",
                        description=f"Leaderboard of suppliers ranked by `xp`\n",
                        thumbnail=utils.Image.BAR_GRAPH.value,
                        footer="Use /supplier stats to access specific supplier stats.")
                    pages_list.append(page_embed)

                try:
                    supplier_name = ctx.guild.get_member(supplier["user"]).mention
                except:
                    supplier_name = "[Not In Server]"

                if supplier_name is None:
                    supplier_name = "[Not In Server]"

                # Supplier Data
                pages_list[page_num - 1].description = \
                    pages_list[page_num - 1].description + \
                    f"\n**{supplier_list.index(supplier) + 1}.** {supplier_name} |" \
                    f" Amount Sold: `{supplier['sold']}` |" \
                    f" Level: `{supplier['level']}` |" \
                    f" Hired: `{supplier['date'].strftime('%b %d %Y')}` |" \
                    f" Tickets Filled: `{supplier['tickets']}` |" \

        paginator = pages.Paginator(pages=pages_list)

        await paginator.respond(ctx.interaction)

    @supplier.command(name="add", description="Add a new supplier to the current guild")
    @has_permissions(administrator=True)
    async def user_add(self, ctx: discord.ApplicationContext,
                       seller: Option(discord.Member, name="user")):
        if Rate.user_is_supplier(seller):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This user is already a supplier!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed)
            return
        Rate.add_user(seller)

        success_embed = utils.embed(title="Addition Successful :white_check_mark:",
                                    description=f"User {seller.mention} has been added as a supplier.",
                                    thumbnail=utils.Image.SUCCESS.value,
                                    color=discord.Color.green())
        await ctx.respond(embed=success_embed)

    @supplier.command(name="retire", description="Retires an supplier from the current guild.")
    @has_permissions(administrator=True)
    async def user_remove(self, ctx: discord.ApplicationContext,
                          seller: Option(discord.Member, name="user")):
        if not Rate.user_is_supplier(seller):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="This user isn't a supplier!\n Add them via `/supplier add`",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)

        Rate.retire_user(seller)

        success_embed = utils.embed(title="Removing Successful :white_check_mark:",
                                    description=f"User {seller.mention} has been marked as retired.\n **The data will still be kept in the database.**",
                                    thumbnail=utils.Image.SUCCESS.value,
                                    color=discord.Color.green())
        await ctx.respond(embed=success_embed)

    @supplier.command(name="stats", description="Allows you to view the stats of a supplier.")
    async def user_view(self, ctx: discord.ApplicationContext,
                        user: Option(discord.Member, name="supplier")):
        # Errors
        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        user_data = Rate.get_user(user)

        # Logic and other information
        time_since = datetime.datetime.now() - user_data['date']
        duration_in_s = time_since.total_seconds()

        years = round(divmod(duration_in_s, 31536000)[0])
        days = time_since.days

        time_since = f"{years} years and {days} days"

        info_embed = utils.embed(title=f"Supplier Stats for {user.name}#{user.discriminator}   :information_source:",
                                 thumbnail=user.display_avatar.url)

        # Fields containing Info
        if user_data['retired']:
            info_embed.add_field(name=":warning: Retired", value=f"**This supplier is currently *retired***")

        info_embed.add_field(name="Amount Sold  :coin:", value=f"`{user_data['sold']}M`")
        info_embed.add_field(name="Level | XP :tada:", value=f"`{user_data['level']} | {user_data['xp']}`")
        info_embed.add_field(name="Rate `$/M`  :coin:", value=f"`${user_data['rate']}`/1M")
        info_embed.add_field(name="Supplier Age :calendar:", value=f"It has been `{time_since}` since {user.mention}"
                                                                   f" was hired, and they were hired on "
                                                                   f"`{user_data['date'].strftime('%b %d %Y')}`")
        info_embed.add_field(name="Amount Owed  :dollar:", value=f"`${user_data['owed']}`")
        info_embed.add_field(name="Amount Paid  :dollar:", value=f"`${user_data['paid']}`")
        info_embed.add_field(name="Tickets Filled :ticket:", value=f"`{user_data['tickets']}`")
        info_embed.add_field(name="Current Bonus :100:", value=f"`{user_data['bonus'] * 100}%`")

        await ctx.respond(embed=info_embed)

    @slash_command(name="level", description="Shows a fancy image card of the level of a supplier")
    async def show_level(self, ctx: discord.ApplicationContext,
                         user: Option(discord.Member, default="self", required=False)):
        if user == "self":
            user = ctx.author

        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        user_data = Rate.get_user(user)
        rank_list = sorted(suppliers.find({}), key=lambda i: (i['level'], i['xp']), reverse=True)
        rank = 0
        for supplier in rank_list:
            if supplier["user"] == user.id and supplier['guild'] == ctx.guild.id:
                rank = rank_list.index(supplier) + 1

        guild_rate = Rate.get_guild_global(user.guild)

        maxed = (user_data['level'] - 1) * INCREMENT + guild_rate['starting'] >= guild_rate['cap']

        draw_rank = partial(image.draw_rank, user_data['level'], user_data['xp'], rank, user_data['sold'], maxed, user, await user.display_avatar.read())
        show_rank = await self.client.loop.run_in_executor(None, draw_rank)

        await ctx.respond(file=discord.File(fp=show_rank, filename='showrank.png'))

    @supplier.command(name="owe", description="Manages the amount that a supplier is owed.")
    @has_permissions(administrator=True)
    async def owe_edit(self, ctx: discord.ApplicationContext,
                       user: Option(discord.Member, name="user"),
                       func: Option(str, name="function", choices=["set", "add", "subtract"]),
                       amount: Option(str, name="amount", description="The amount you wish to set to")
                       ):
        # If the amount provided is NOT an number
        if not utils.is_num(amount):
            error_embed = utils.embed(title=":x: Invalid Argument :x:",
                                      description="Please specify a valid type `float` for the argument `amount`",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Convert amount to an float
        amount = float(amount)

        # If the user isn't a supplier
        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        operator = "$inc"
        if func == "set":
            operator = "$set"
        elif func == "subtract":
            amount = amount * -1

        old_owed = Rate.get_user(user)['owed']

        suppliers.update_one({"user": user.id, "guild": user.guild.id}, {operator: {"owed": amount}})

        # Success!

        success_embed = utils.embed(title="Update Successful :white_check_mark:",
                                    description=f"{user.mention}'s owed amount has been updated successfully!\n"
                                                f"Their owed amount has been changed from `{old_owed}` to `{amount}`",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.respond(embed=success_embed)

    @supplier.command(name="bonus", description="Manages the supplier's bonus.")
    @has_permissions(administrator=True)
    async def bonus_edit(self, ctx: discord.ApplicationContext,
                         user: Option(discord.Member, name="user"),
                         func: Option(str, name="function", choices=["set", "add", "subtract"]),
                         amount: Option(str, name="amount",
                                        description="The amount you wish to set the bonus to -1000% to 1000%")
                         ):

        if amount.endswith("%"):
            amount = amount[:-1]

        # If the amount provided is NOT an number
        if not utils.is_num(amount):
            error_embed = utils.embed(title=":x: Invalid Argument :x:",
                                      description="Please specify a valid type `percentage` or `float` for the argument `amount`\n"
                                                  "i.e. ",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Convert amount to an float
        amount = float(amount)
        amount = amount / 100

        # If the user isn't a supplier
        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the"
                                                  " `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        operator = "$inc"
        if func == "set":
            operator = "$set"
        elif func == "subtract":
            amount = amount * -1

        old_bonus = Rate.get_user(user)['owed']

        suppliers.update_one({"user": user.id, "guild": user.guild.id}, {operator: {"bonus": amount}})

        # Success!

        success_embed = utils.embed(title="Update Successful :white_check_mark:",
                                    description=f"{user.mention}'s bonus has been updated successfully!\n"
                                                f"Their bonus has been changed from `{old_bonus * 100}%` to `{amount * 100}%`",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.respond(embed=success_embed)

    @supplier.command(name="paid", description="Removes an amount from a user's owe, marking that amount as paid.")
    @has_permissions(administrator=True)
    async def paid(self, ctx: discord.ApplicationContext,
                   user: Option(discord.Member, name="user"),
                   amount: Option(int, name="amount", description="How much the user was paid")):
        # If the amount provided is NOT an number
        if not utils.is_num(amount):
            error_embed = utils.embed(title=":x: Invalid Argument :x:",
                                      description="Please specify a valid type `float` for the argument `amount`",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        # Convert amount to an float
        amount = float(amount)

        # If the user isn't a supplier
        if not Rate.user_is_supplier(user):
            error_embed = utils.embed(title=":x: Error :x:",
                                      description="**This user isn't a supplier!** You can make them a supplier via the `/supplier add` command!",
                                      thumbnail=utils.Image.ERROR.value,
                                      color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        old_owed = Rate.get_user(user)['owed']
        old_paid = Rate.get_user(user)['paid']

        suppliers.update_one({"user": user.id, "guild": user.guild.id}, {"$inc": {"owed": amount * -1, "paid": amount}})

        # Success!

        success_embed = utils.embed(title="Update Successful :white_check_mark:",
                                    description=f"{user.mention}'s paid amount has been updated successfully!\n"
                                                f"Their paid amount has been changed from `{old_paid}` to `{old_paid + amount}`"
                                                f"Their owed amount has been changed from `{old_owed}` to `{old_owed - amount}`\n",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.respond(embed=success_embed)


def setup(client):
    client.add_cog(Rate(client))
