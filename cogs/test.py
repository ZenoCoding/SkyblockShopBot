from discord.ext import commands


class Template(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Test Cog Loaded - USED FOR DEVELOPMENT PURPOSES ONLY")


def setup(client):
    client.add_cog(Template(client))
