import random
import utils

from discord.commands import slash_command
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun Cog Loaded")

    @slash_command(
        name="joke",
        description="Humor via lazerbeams.")
    async def joke(self, ctx):
        jokelist =[
            ("Why did the chicken cross the road?", "To get to the other side!"),
            ("Why did you start using reddit?", "Seriously though. Why?"),
            ("Once upon a time..", "There was a small princess.. and she wandered around the large castle that she "
                                   "lived in, to see if anyone was home. But despite looking for over 5 minutes, "
                                   "she didn't find anyone. Later that day, she ran into a armor stand holding it's "
                                   "sword out and chopped her head off."),
            ("you f*cking idiot!", "- the2tree4"),
            ("sodiumsodiumsodiumsodiumsodiumsodiumsodiumsodiumsodiumsodiumsodium Batman!", "science nerds..")
        ]
        choice = random.choice(jokelist)
        jokeEmbed = utils.embed(title=choice[0], description=choice[1])
        await ctx.respond(embed=jokeEmbed)


def setup(client):
    client.add_cog(Fun(client))