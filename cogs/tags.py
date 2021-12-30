import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class Tags(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tags Cog Loaded")

    @commands.group(pass_context=True)
    @has_permissions(kick_members=True)
    async def tag(self, ctx):
        await ctx.message.delete()

    @tag.command()
    @has_permissions(kick_members=True)
    async def pool(self, ctx):
        poolEmbed = discord.Embed(title="Paying with Paypal Pool",
                                  description="Please follow steps.", color=discord.Color.blue())
        poolEmbed.add_field(name="Step 1", value="Visit our Paypal Pool : https://paypal.me/pools/c/8CvM1x6G63",
                            inline=False)
        poolEmbed.add_field(name="Step 2",
                            value="Press the **CHIP IN** button and enter the amount you need to pay. Then, as a note, add:        **\"I am (yourdiscordname#xxxx) on discord, and I want xxxMil\"**",
                            inline=False)
        poolEmbed.add_field(name="Step 3",
                            value="Send a screenshot of the payment summary after you have completed the payment.", inline=False)
        poolEmbed.set_footer(icon_url=ctx.guild.icon_url,
                              text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=poolEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def paypal(self, ctx):
        paypalEmbed = discord.Embed(title="Paying with Paypal F&F (FRIENDS AND FAMILY)",
                                    description="Please follow steps correctly, __make sure to read **carefully**__.",
                                    color=discord.Color.blue())
        paypalEmbed.add_field(name="Step 1", value="Visit our Paypal : https://paypal.me/huaweilover",
                              inline=False)
        paypalEmbed.add_field(name="Step 2",
                              value="Press **\"Send\"**, and enter how much you want to pay. Then, as a note, add:        **\"I am (yourdiscordname#xxxx) on discord, and I want xxxMil\"**",
                              inline=False)
        paypalEmbed.add_field(name="Step 3",
                              value="Press continue. You will be prompted with: **\"What’s this payment for?\"**. Select **Sending to a Friend**. *(Don't you see that option? Let us know in your ticket for alternative payment methods)*\n*Make sure you've completed this step correctly.*",
                              inline=False)
        paypalEmbed.add_field(name="Step 4",
                              value="Press continue. You will see the payment confirmation. If everything looks correct, press **Send.**",
                              inline=False)
        paypalEmbed.add_field(name="Step 5",
                              value="After you have sent the payment, send a screenshot of the payment summary.\n*Still not sure how to pay? Check out this video : https://youtu.be/t5jgBY8McFs*",
                              inline=False)
        paypalEmbed.set_footer(icon_url=ctx.guild.icon_url,
                              text=f"Quick and easy delivery provided by {ctx.guild.name}.")
        await ctx.send(embed=paypalEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def paypalcard(self, ctx):
        paypalcardEmbed = discord.Embed(title="Paying with Credit/Debit ",
                                        description="Please follow steps.", color=discord.Color.green())
        paypalcardEmbed.add_field(name="Step 1",
                                  value="**Visit our Paypal Donation Link : https://www.paypal.com/donate?hosted_button_id=QHG6TYPXLFRA6** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 2",
                                  value="**Enter the amount that you need to pay. Convert that  to GBP (Example: \"15USD to GBP\" on Google)** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 3",
                                  value="**Click the button says: I'd like to add £0.xx to my donation to help offset the cost of processing fees. Then, click:** *Donate with a debit or credit card* ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 4",
                                  value="**Please leave a note with the following contents:** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Note", value="**This is a donation for my friend Volkan's new company.**",
                                  inline=False)
        paypalcardEmbed.add_field(name="Example", value="https://prnt.sc/1tldq62", inline=False)
        await ctx.send(embed=paypalcardEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def amazon(self, ctx):
        amazonEmbed = discord.Embed(title="Paying With Giftcards",
                                    description="Please follow steps.", color=discord.Color.purple())
        amazonEmbed.add_field(name="Step 1",
                              value="Visit any website that sells **Amazon __*Turkey*__ Giftcards**. Here is one that I recommend: https://eneba.com/amazon-amazon-gift-card-100-try-turkey",
                              inline=False)
        amazonEmbed.add_field(name="Step 2", value="**Buy the giftcard, and get the code.**", inline=False)
        amazonEmbed.add_field(name="Step 3", value="Please **send the giftcard code in the TICKET**, and ping wovl.", inline=False)
        await ctx.send(embed=amazonEmbed)

def setup(client):
    client.add_cog(Tags(client))