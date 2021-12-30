import os
import json
import traceback
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.default()
intents.members = True


def get_prefix(client, msg):
    if msg is None or msg.guild is None:
        return
    with open('data.json', 'r') as f:
        data = json.load(f)

    return data[str(msg.guild.id)]["prefix"]


client = commands.Bot(command_prefix=get_prefix, help_command=None, intents=intents, case_insensitive=True)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game("Selling Coins at discord.gg/skyblockshop\nGreat Rates And Trustable Staff"))
    print("Bot is ready. Skyblock Shop Bot Up and running.")


@client.event
async def on_guild_join(guild):
    with open('data.json', 'r') as f:
        data = json.load(f)

    data[str(guild.id)] = {
        "prefix": "!",
        "price": 0.3,
        "vouch": "unset",
        "blacklisted": [],
        "ticket": {
            "category": "unset",
            "logging": "unset"
        },
        "tickets": {
        },
        "sellers": {
        },
        "stock": 0,
        "lastmessages": {

        }
    }

    with open("data.json", 'w') as f:
        json.dump(data, f, indent=4)


def set_prefix(guild, prefix):
    with open('data.json', 'r') as f:
        data = json.load(f)

    data[str(guild.id)]["prefix"] = prefix

    with open("data.json", 'w') as f:
        json.dump(data, f, indent=4)


@client.command()
@has_permissions(administrator=True)
async def prefix(ctx, prefix="default"):
    defaultEmbed = discord.Embed(name="Prefix",
                                 description=f"Your prefix is `{get_prefix(client, ctx.message)}`. Type `{get_prefix(client, ctx.message)}prefix <prefix>` to set a new prefix.",
                                 color=discord.Color.blue())
    prefixEmbed = discord.Embed(name="Prefix Set", description=f"Your prefix has been set to `{prefix}`.",
                                color=discord.Color.blue())
    if (prefix == "default"):
        await ctx.send(embed=defaultEmbed)
    else:
        set_prefix(ctx.guild, prefix)
        await ctx.send(embed=prefixEmbed)

@client.event
async def on_message(message):
    if message is None or message.content is None:
        return

    try:
        if message.content.startswith(get_prefix(client, message)):
            with open("data.json", 'r') as f:
                data = json.load(f)

            blacklisted = data[str(message.guild.id)]["blacklisted"]
            if message.channel.id in blacklisted and not message.author.guild_permissions.administrator:
                blacklistedEmbed = discord.Embed(title="Channel Blacklisted", description="Please use the right channels! Please use the #bot-commands channel in your server!", color=discord.Color.red())
                await message.channel.send(embed=blacklistedEmbed)
            else:
                await client.process_commands(message)
    except:
        return


@client.command()
@has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
@has_permissions(administrator=True)
async def reload(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    client.unload_extension(f'cogs.{extension}')


@client.command()
@has_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


# command errors

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        missingArgsEmbed = discord.Embed(title=":x: Error :x:",
                                         description="Please specify a cog to load.", color=discord.Color.red())
        await ctx.send(embed=missingArgsEmbed)


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        missingArgsEmbed = discord.Embed(title=":x: Error :x:",
                                         description="Please specify a cog to unload.", color=discord.Color.red())
        await ctx.send(embed=missingArgsEmbed)


@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        missingArgsEmbed = discord.Embed(title=":x: Error :x:",
                                         description="Please specify a cog to unload.", color=discord.Color.red())
        await ctx.send(embed=missingArgsEmbed)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        errorEmbed = discord.Embed(title=":x: Unknown Command :x:",
                                   description="This isn't a valid command! Try !help for help..", color=discord.Color.red())
        await ctx.send(embed=errorEmbed)
        return
    elif isinstance(error, commands.MissingPermissions):
        errorEmbed = discord.Embed(title=":x: Missing Permissions :x:",
                                   description="You are missing one or more required permissions to use this command.", color=discord.Color.red())
        await ctx.send(embed=errorEmbed)
    else:
        traceback.print_exception(type(error), error, error.__traceback__)
        errorEmbed = discord.Embed(title=":x: An Error Occurred :x:", description="An unexpected error occured. It has been reported to the developers and should  be fixed shortly.", color=discord.Color.red())
        await ctx.send(embed=errorEmbed)


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run("ODU5MTk2MjY5NDY4ODQ0MDUy.YNpK4Q.isM_Wz2FCccxNajWXPUC05SG_L8")