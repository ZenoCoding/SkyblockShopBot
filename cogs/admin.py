import discord
import json
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin Cog Loaded")

    @commands.command()
    @has_permissions(administrator=True)
    async def setbuyer(self, ctx, role="default"):
        if role == "default":
            defaultEmbed = discord.Embed(title="Buyer role",
                                         description="Type `!setbuyer <role id>` to set the role.")
            await ctx.send(embed=defaultEmbed)
        else:
            with open('data.json', 'r') as f:
                data = json.load(f)

            if role == "new":
                role = await ctx.guild.create_role(name="Buyer")
                createdEmbed = discord.Embed(title="Buyer role created!",
                                             description="Buyer role has been created.")
                await ctx.send(embed=createdEmbed)
                data[str(ctx.guild.id)]["buyer"] = role.id
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return

            try:
                int(role)
                buyerrole = ctx.guild.get_role(int(role))
            except:
                buyerrole = None

            if buyerrole != None:
                data[str(ctx.guild.id)]["buyer"] = buyerrole.id
                setEmbed = discord.Embed(title="Buyer role set!",
                                         description="Buyer role has been set.")
                await ctx.send(embed=setEmbed)
                with open('data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                return
            else:
                errorEmbed = discord.Embed(title="Invalid role!",
                                           description="You entered an invalid role! Please try again.")
                await ctx.send(embed=errorEmbed)

    @commands.command()
    @has_permissions(administrator=True)
    async def selleradd(self, ctx, user="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        successEmbed = discord.Embed(title="Seller Added", description=f"Seller <@{user.id}> has been added.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

            data[str(ctx.guild.id)]["sellers"][str(user.id)] = 0

        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @has_permissions(administrator=True)
    async def sellerremove(self, ctx, user="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        successEmbed = discord.Embed(title="Seller Added", description=f"Seller <@{user.id}> has been added.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

            del data[str(ctx.guild.id)]["sellers"][str(user.id)]

        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @has_permissions(administrator=True)
    async def sellers(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        sellers = data[str(ctx.guild.id)]["sellers"].keys()
        rates = data[str(ctx.guild.id)]["sellers"]

        sellerssorted = []

        for seller in sellers:
            if len(sellerssorted) == 0:
                sellerssorted.append(seller)
                continue
            else:
                for i in sellerssorted:
                    if sellerssorted.index(i) == len(sellerssorted):
                        if rates[seller] > rates[i]:
                            sellerssorted.insert(sellerssorted.index(i))
                            break
                        else:
                            sellerssorted.append(seller)
                            break
                    if rates[seller] > rates[i]:
                        sellerssorted.insert(sellerssorted.index(i))
                        break

        sellerslist = ""

        for seller in sellerssorted:
            sellerid = seller
            seller = ctx.guild.get_member(int(seller))
            sellerslist = sellerslist + f"\n{sellerssorted.index(sellerid)+1}. `{seller.name}#{seller.discriminator}` with `{rates[sellerid]}M` coins sold."


        successEmbed = discord.Embed(title="Top Sellers", description=f"Top Sellers Sorted By Rate:\n{sellerslist}",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

    @commands.group(invoke_without_command=True)
    @has_permissions(administrator=True)
    async def rate(self, ctx):
        embed = discord.Embed(title="Rate Help", description="Rate commands are for keeping track of how much sellers have sold.")
        embed.add_field(name="!rate add <user> <amount>", value="Adds a specified amount to a seller's rate.")
        embed.add_field(name="!rate remove <user> <amount>", value="Removes a specified amount to a seller's rate.")
        embed.add_field(name="!rate set <user> <amount>", value="Sets a seller's rate to a specified value.")
        await ctx.send(embed=embed)

    @rate.command()
    @has_permissions(administrator=True)
    async def add(self, ctx, user="default", amount="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        try:
            amount = int(amount)
        except:
            errorEmbed = discord.Embed(title="Invalid Amount", description="Please specify an valid amount.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        with open('data.json', 'r') as f:
            data = json.load(f)

        rate = data[str(ctx.guild.id)]["sellers"][str(user.id)]

        rate += amount
        print(rate)
        print(amount)

        data[str(ctx.guild.id)]["sellers"][str(user.id)] = rate

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Rate Increased", description=f"Seller <@{user.id}>'s rate has been increased by `{amount}M`, and is now `{rate}M`.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

    @rate.command()
    @has_permissions(administrator=True)
    async def subtract(self, ctx, user="default", amount="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        try:
            amount = int(amount)
        except:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid amount.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        with open('data.json', 'r') as f:
            data = json.load(f)

        rate = data[str(ctx.guild.id)]["sellers"][str(user.id)]

        data[str(ctx.guild.id)]["sellers"][str(user.id)] = rate - amount

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Rate Decreased",
                                     description=f"Seller <@{user.id}>'s rate has been decreased by `{amount}M`, and is now `{rate}M`.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

    @rate.command()
    @has_permissions(administrator=True)
    async def set(self, ctx, user="default", amount="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        try:
            amount = int(amount)
        except:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid amount.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        with open('data.json', 'r') as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["sellers"][str(user.id)] = amount

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Rate Set",
                                     description=f"Seller <@{user.id}>'s rate has been set to `{amount}M`.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

    @rate.command()
    @has_permissions(administrator=True)
    async def get(self, ctx, user="default"):
        try:
            user = ctx.guild.get_member(int(user))
        except:
            user = None

        if user == None:
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid user.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        with open('data.json', 'r') as f:
            data = json.load(f)

        rate = data[str(ctx.guild.id)]["sellers"][str(user.id)]

        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)

        successEmbed = discord.Embed(title="Rate Increased",
                                     description=f"Seller <@{user.id}>'s rate is currently `{rate}M`.",
                                     color=discord.Color.green())
        await ctx.send(embed=successEmbed)

    @commands.command()
    @has_permissions(administrator=True)
    async def rulesembed(self, ctx, channel=None):
        try:
            channel = ctx.guild.get_channel(int(channel))
        except:
            channel = None

        if channel == None:
            errorEmbed = discord.Embed(title="Invalid Channel", description="Please specify an valid channel to send the message in.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        rulesEmbed = discord.Embed(title="**RULES:**", description="In order to be a member of this server, You must agree to the following:"
                                                                   "\n1. Follow Discord TOS. (https://discord.com/terms)."
                                                                   "\n2. No form of DM Advertising.\n"
                                                                   "3. Please keep your conversations in the correct channels, stay on topic."
                                                                   "\n4. No form of Hate Speech or being genuinely offensive or annoying."
                                                                   "\n5. No Gory, Sexual, or scary content - Screamer links, nudity, death."
                                                                   "\n6. Please keep personal issues out of the server and in DMs."
                                                                   "\n7. No publishing of personal information (including real names, addresses, emails, passwords, bank account and credit card information, etc.)."
                                                                   "\n8. Please be respectful to all users and staff members.", color=discord.Color.purple())
        rulesEmbed.add_field(name="**TERMS OF SERVICE:**",
                                   value="If you wish to purchase anything from this server, You must agree that:"
                                               "\n1. You will not chargeback, and refunds will not be given."
                                               "\n2. You will not leak our in-game name to anyone else."
                                               "\n3. You will not do anything that would hurt our server."
                                               "\n4. You can not purchase anything if you are in Hypixel staff team."
                                               "\n5. You must have permission to use the funding source you are paying with."
                                               "\n6. You are not allowed to use any cracked funding source."
                                               "\n7. We have the right to change the TOS anytime for any reason."
                                               "\n8. You understand that there is a chance of getting Banned, and our service is not responsible for it"
                                               "\n9. We do not take responsibility for what happens after you buy coins.\n\nWe reserve the right to __**Update the TOS and RULES at any time!**__\n\n**Please react with a checkmark to accept the rules and tos!**")

        rulesEmbed.set_footer(text=f"This server is owned by {ctx.guild.owner.name}#{ctx.guild.owner.discriminator}", icon_url=ctx.guild.owner.avatar_url)
        await channel.send(embed=rulesEmbed)

    @commands.command()
    @has_permissions(administrator=True)
    async def roles(self, ctx, channel=None):
        try:
            channel = ctx.guild.get_channel(int(channel))
        except:
            channel = None

        if channel == None:
            errorEmbed = discord.Embed(title="Invalid Channel",
                                       description="Please specify an valid channel to send the message in.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        rolesEmbed = discord.Embed(title="**ROLES:**",
                                   description="React with the corresponding reaction to get the role:"
                                               "\nReact with the party hat for giveaway pings."
                                               "\nReact with the toolkit for special offer pings."
                                               "\nReact with the newspaper for discount pings.",
                                   color=discord.Color.purple())
        await channel.send(embed=rolesEmbed)

    @commands.command()
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 5):

        await ctx.channel.purge(limit=amount)
        successEmbed = discord.Embed(title="Messages Purged :white_check_mark:",
                                     description=f"**`{amount}` messages have been purged.**",
                                     color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.send(embed=successEmbed)

    @commands.command()
    @has_permissions(administrator=True)
    async def announce(self, ctx, embedid:int ="default"):
        #Defining the Embeds
        embeds = []
        #Embed 1
        aEmbed = discord.Embed(title="Announcement! :loudspeaker:",
                                     description=f"**Something Exciting Happened!**",
                                     color=discord.Color.green())
        aEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        embeds.append(aEmbed)
        #Embed 2
        a2Embed = discord.Embed(title="Announcement 2! :loudspeaker:",
                                     description=f"**Something Exciting Didn't happen.**",
                                     color=discord.Color.green())
        a2Embed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        embeds.append(a2Embed)

        #Embed 3 .. etc

        membersnum = 0

        try:
            for member in ctx.guild.members:
                if member.bot == False:

                    try:
                        await member.send(embed=embeds[embedid-1])
                    except commands.errors.CommandInvokeError and commands.CommandInvokeError and discord.errors.Forbidden:
                        continue
                    membersnum += 1
        except IndexError:
            errorEmbed = discord.Embed(title=":x: Error :x:",
                                       description=f"**Please enter a valid index! If this issue persists, contact a developer for assistance.**",
                                       color=discord.Color.red())
            errorEmbed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/860656459507171368/896878163873919007/error.png")
            errorEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                  text=f"Quick and easy delivery provided by {ctx.guild.name}.")
            await ctx.send(embed=errorEmbed)
            return

        successEmbed = discord.Embed(title="Success! :white_check_mark:",
                                description=f"**Message successfully broadcasted to `{membersnum} members.`**",
                                color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                           text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.send(embed=successEmbed)





def setup(client):
    client.add_cog(Admin(client))
