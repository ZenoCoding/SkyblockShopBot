import logging
import os

import discord
from discord.ext import commands

import utils

TOKEN = "ODU5MTk2MjY5NDY4ODQ0MDUy.YNpK4Q.isM_Wz2FCccxNajWXPUC05SG_L8"

# List of "Guilds"
GUILDS = [859201687264690206, 945903743319293992] # Put in here

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s: %(levelname)s]: [%(name)s]: %(message)s'))
logger.addHandler(handler)

config = utils.db.config

intents = discord.Intents.default()
intents.members = True

def GUILD_DATA_DEFAULT(guild):
    return {
        "_id": guild.id,
        "vouch": None,
        "ticket": {
            "category": None,
            "channel": None,
            "logging": None,
        },
        "buyer": None,
        "supplier": None,
        "rate": {
            "starting": 0.06,
            "cap": 0.15
        },
        "stock": 0,
        "pinned_messages": {
        },
        "supports": [],
        "discount": [0, 0]

    }


# Remove debug_guilds if you wish to not use this
client = discord.Bot(help_command=None, intents=intents, debug_guilds=GUILDS)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Game(
                                     "Selling Coins at discord.gg/skyblockshop\nGreat Rates And Trustable Staff\nThe place to sell AND buy all things skyblock!"))
    print("Bot is ready. Skyblock Shop Bot up and running.")
    logging.info("Bot is ready. Skyblock Shop Bot up and running.")


@client.event
async def on_guild_join(guild):
    guild_data = GUILD_DATA_DEFAULT(guild)

    config.insert_one(guild_data)


# Command errors

@client.event
async def on_application_command_error(ctx, error):
    if config.find_one({"_id": ctx.guild.id}) is None:
        fix_embed = utils.embed(title="Hmm... :thinking:",
                                description="Something isn't right! It seems that the config has been **wiped** in this server!\n"
                                            "Hang tight while I **restore the default configuration!**")
        guild_data = GUILD_DATA_DEFAULT(ctx.guild)

        config.insert_one(guild_data)
        await ctx.respond(embed=fix_embed)
        return

    if isinstance(error, commands.CommandNotFound):
        error_embed = utils.embed(title=":x: Unknown Command :x:",
                                  description="This isn't a valid command! Try /help for help..",
                                  thumbnail=utils.Image.ERROR.value,
                                  color=discord.Color.red())
        await ctx.respond(embed=error_embed, ephemeral=True)
        return
    elif isinstance(error, commands.errors.MissingPermissions):
        error_embed = utils.embed(title=":x: Missing Permissions :x:",
                                  description="You are missing one or more required permissions to use this command.",
                                  thumbnail=utils.Image.ERROR.value,
                                  color=discord.Color.red())
        await ctx.respond(embed=error_embed, ephemeral=True)
    else:
        error_embed = utils.embed(title=":x: Unexpected Error :x:",
                                  description="Woah! An unexpected error occurred... Contact an administrator if the"
                                              " issue persists.",
                                  thumbnail=utils.Image.ERROR.value,
                                  color=discord.Color.red())
        await ctx.respond(embed=error_embed, ephemeral=True)
        logging.error("An unexpected error occurred, logging to console.\n")
        raise error


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN)
