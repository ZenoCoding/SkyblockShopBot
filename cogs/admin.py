import discord
from discord.commands import slash_command, Option
from discord.ext import commands
from discord.ext.commands import has_permissions

import utils

config = utils.db.config


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin Cog Loaded")

    @slash_command(
        name="setbuyer",
        description="Set the buyer role of your server."
    )
    @has_permissions(administrator=True)
    async def setbuyer(self,
                       ctx,
                       role: Option(discord.Role, "Pick a role in the server.")):
        embed = utils.embed(title="Set Buyer Role  :white_check_mark:",
                            description=f"The Buyer role has been set to {ctx.guild.get_role(role.id).mention}",
                            color=discord.Color.blue())
        await ctx.respond(embed=embed, ephemeral=True)

        config.update_one({"_id": ctx.guild.id}, {"$set": {"buyer": int(role.id)}})

    @slash_command(
        name="rulesembed",
        description="Send a rule embed from the bot in the current channel."
    )
    async def rulesembed(self, ctx):

        rulesEmbed = utils.embed(title="**RULES:**",
                                 description="In order to be a member of this server, You must agree to the following:"
                                             "\n1. Follow discord TOS. (https://discord.com/terms)."
                                             "\n2. No form of DM Advertising.\n"
                                             "3. Please keep your conversations in the correct channels, stay on topic."
                                             "\n4. No form of Hate Speech or being genuinely offensive or annoying."
                                             "\n5. No Gory, Sexual, or scary content - Screamer links, nudity, death."
                                             "\n6. Please keep personal issues out of the server and in DMs."
                                             "\n7. No publishing of personal information (including real names, addresses, emails, passwords, bank account and credit card information, etc.)."
                                             "\n8. Please be respectful to all users and staff members.",
                                 color=discord.Color.purple())
        rulesEmbed.add_field(name="**TERMS OF SERVICE:**",
                             value="If you wish to purchase anything from this server, You must agree that:"
                                   "\n1. You will not chargeback, and refunds will not be given."
                                   "\n2. You will not leak our in-game name to anyone else."
                                   "\n3. You will not do anything that would hurt our server."
                                   "\n4. You can not purchase anything if you are in Hypixel staff team."
                                   "\n5. You must have permission to use the funding source you are paying with."
                                   "\n6. You are not allowed to use any cracked funding source."
                                   "\n7. We have the right to change the TOS anytime for any reason."
                                   "\n8. You understand that there is a chance of getting banned, and our service is not responsible for it"
                                   "\n9. We do not take responsibility for what happens after you buy coins.\n"
                                   "\nWe reserve the right to __**Update the TOS and RULES at any time!**__\n"
                                   "\n**Please react with a checkmark to accept the rules and tos!**")

        rulesEmbed.set_footer(text=f"This server is owned by {ctx.guild.owner.name}#{ctx.guild.owner.discriminator}",
                              icon_url=ctx.guild.owner.avatar_url)
        await ctx.respond(embed=rulesEmbed, ephemeral=True)

    @slash_command(
        name="roleembed",
        description="Send a role embed from the bot in the current channel."
    )
    @has_permissions(administrator=True)
    async def roles(self, ctx):

        rolesEmbed = utils.embed(title="**ROLES:**",
                                 description="React with the corresponding reaction to get the role:"
                                             "\nReact with the party hat for giveaway pings."
                                             "\nReact with the toolkit for special offer pings."
                                             "\nReact with the newspaper for discount pings.",
                                 color=discord.Color.purple())

        success_embed = utils.embed(title="Success :white_check_mark:",
                                    description="The rule embed has been sent.",
                                    image=utils.Image.SUCCESS.value)

        await ctx.send(embed=rolesEmbed)
        await ctx.respond(embed=success_embed, ephemeral=True)

    @slash_command(
        name="purge",
        description="Purge X amount of messages from the chat."
    )
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 5):

        await ctx.channel.purge(limit=amount)
        successEmbed = utils.embed(title="Messages Purged :white_check_mark:",
                                   description=f"**`{amount}` messages have been purged.**",
                                   color=discord.Color.green())
        successEmbed.set_footer(icon_url=ctx.guild.icon_url,
                                text=f"Quick and easy delivery provided by {ctx.guild.name}.")

        await ctx.respond(embed=successEmbed, ephemeral=True)

    @slash_command(
        name="announce",
        description="Announce a preset of specified embeds to all members of the guild."
    )
    @has_permissions(administrator=True)
    async def announce(self, ctx, embedid: int = "default"):
        # Defining the Embeds
        embeds = []

        # Embed 1
        embed = utils.embed(title="Announcement! :loudspeaker:",
                            description=f"**Something Exciting Happened!**",
                            color=discord.Color.green())
        embed.set_footer(icon_url=ctx.guild.icon_url,
                         text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        embeds.append(embed)
        # Embed 2
        embed_2 = utils.embed(title="Announcement 2! :loudspeaker:",
                              description=f"**Something Exciting Didn't happen.**",
                              color=discord.Color.green())
        embed_2.set_footer(icon_url=ctx.guild.icon_url,
                           text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        embeds.append(embed_2)

        # Embed 3 .. etc

        membersnum = 0

        try:
            for member in ctx.guild.members:
                if member.bot == False:

                    try:
                        await member.send(embed=embeds[embedid - 1])
                    except discord.errors.Forbidden:
                        continue
                    membersnum += 1
        except IndexError:
            error_embed = utils.embed(title=":x: Error :x:",
                                      description=f"**Please enter a valid index!**",
                                      color=discord.Color.red(),
                                      thumbnail=utils.Image.ERROR.value)
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        success_embed = utils.embed(title="Success! :white_check_mark:",
                                    description=f"**Message successfully broadcasted to `{membersnum} members.`**",
                                    color=discord.Color.green(),
                                    thumbnail=utils.Image.SUCCESS.value)

        await ctx.respond(embed=success_embed, ephemeral=True)


def setup(client):
    client.add_cog(Admin(client))
