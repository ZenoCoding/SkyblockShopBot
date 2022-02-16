# import discord
# import utils
# from discord.ext import commands
# from discord.commands import slash_command
#
# config = utils.db.config
#
#
# class ChannelDropdown(discord.ui.Select):
#     def __init__(self, guild):
#
#         options = []
#         for channel in guild.channels:
#             if not isinstance(channel, discord.CategoryChannel) and not isinstance(channel, discord.VoiceChannel):
#                 isselected = channel.id in config.find_one({"_id": guild.id})['blacklisted']
#                 options.append(discord.SelectOption(f"#{channel.name}", value=str(channel.id), default=isselected))
#
#         super().__init__(
#             placeholder="Select your Blacklist Channels",
#             options=options
#         )
#
#     async def callback(self, interaction: discord.Interaction):
#         config.update_one({"_id": interaction.guild_id}, {"$set": {"blacklisted": self.values}})
#
#         blacklistEmbed = utils.embed(title="Manage Blacklisted Channels  :no_entry_sign:",
#                                      description=f"Users cannot use bot commands in blacklisted channels. Please "
#                                                  f"select or deselect which channels you would like to be blacklisted.")
#         blacklisted = "none"
#         for channel in self.values:
#             if blacklisted == "none": blacklisted = ""
#             blacklisted = blacklisted + f"{interaction.guild.get_channel(channel).mention}\n"
#         blacklistEmbed.add_field(name="Blacklisted Channels",
#                                  value=blacklisted)
#
#         await interaction.edit_original_message(embed=blacklistEmbed, view=BlacklistView(self.guild)) # also edit the component dropdown
#
# class BlacklistView(discord.ui.View):
#     def __init__(self, guild):
#         super().__init__()
#
#         self.add_item(ChannelDropdown(guild))
#
#
# class Blacklist(commands.Cog):
#
#     def __init__(self, client):
#         self.client = client
#
#     @commands.Cog.listener()
#     async def on_ready(self):
#         print("BlackList Cog Loaded")\
#
#     @slash_command(
#         name="blacklist",
#         description="Manage the command blacklist feature of the bot."
#     )
#     # @cog_ext.permission(permissions=[discord.Permissions.administrator])
#     async def blacklist(self, ctx):
#
#         blacklistEmbed = utils.embed(title="Manage Blacklisted Channels  :no_entry_sign:",
#                                         description=f"Users cannot use bot commands in blacklisted channels. Please select or deselect which channels you would like to be blacklisted.")
#         blacklisted = "none"
#         for channel in config.find_one({"_id": ctx.guild.id})['blacklisted']:
#             if blacklisted == "none": blacklisted == ""
#             blacklisted = blacklisted + f"{ctx.guild.get_channel(channel).mention}\n"
#         blacklistEmbed.add_field(name="Blacklisted Channels",
#                                  value=blacklisted)
#
#         await ctx.respond(embed=blacklistEmbed, view=BlacklistView(ctx.guild), ephemeral=True)
#
#     @commands.Cog.listener()
#     # TODO: What event represents the on_slash_command event?
#     async def on_slash_command(self, interaction):
#         print("yae")
#
# def setup(client):
#     client.add_cog(Blacklist(client))