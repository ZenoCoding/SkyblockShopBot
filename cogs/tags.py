import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import has_permissions

import utils


class Tags(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tags Cog Loaded")

    tag = SlashCommandGroup("tag", "A tag command, with many different tags to use!")

    @tag.command()
    @has_permissions(kick_members=True)
    async def pool(self, ctx):
        poolEmbed = utils.embed(title="Paying with Paypal Pool",
                                description="Please follow steps.", color=discord.Color.blue())
        poolEmbed.add_field(name="Step 1", value="Visit our Paypal Pool : https://paypal.me/pools/c/8CvM1x6G63",
                            inline=False)
        poolEmbed.add_field(name="Step 2",
                            value="Press the **CHIP IN** button and enter the amount you need to pay. Then, as a note, add:        **\"I am (yourdiscordname#xxxx) on discord, and I want xxxMil\"**",
                            inline=False)
        poolEmbed.add_field(name="Step 3",
                            value="Send a screenshot of the payment summary after you have completed the payment.",
                            inline=False)
        await ctx.respond(embed=poolEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def crypto(self, ctx):
        cryptoEmbed = utils.embed(title="Crypto Address Details",
                                    description="Please read below to pay with Cryptocurrency",
                                    color=discord.Color.blue(),
                                    thumbnail="https://cdn.discordapp.com/attachments/895770713145888857/927586722815037520/Copper-coin-stack.png")
        cryptoEmbed.add_field(name="Bitcoin", value="**1Max1iyvQzSLBP5acbxiuNC6XstFh3xrBT**",
                              inline=False)
        cryptoEmbed.add_field(name="Litecoin",
                              value="**La5zVfLWwUUSTYQ72d5ymcsFVqZu82ZSJJ**",
                              inline=False)
        cryptoEmbed.add_field(name="Ethereum",
                              value="**0x019e2953012f09d39b4090b59f0cf12b56aff0c0**", inline=False)
        await ctx.respond(embed=cryptoEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def paypal(self, ctx):
        paypalEmbed = utils.embed(title="Paying with Paypal F&F (FRIENDS AND FAMILY)",
                                  description="Please follow steps correctly, __make sure to read **carefully**__.",
                                  color=discord.Color.blue(),
                                  thumbnail="https://cdn.discordapp.com/attachments/895770715918336023/927587799857782794/2-currency-gold-chest.png")
        paypalEmbed.add_field(name="Step 1", value="Login to your paypal account.",
                              inline=False)
        paypalEmbed.add_field(name="Step 2",
                              value="Visit our Paypal.me Link : https://paypal.me/nathanjg11 then press on **SEND**",
                              inline=False)
        paypalEmbed.add_field(name="Step 3",
                              value="Enter how much you want to pay. Then, as a note, add: **\"wovl\"** \n\n||https://prnt.sc/25u36ul||",
                              inline=False)
        paypalEmbed.add_field(name="Step 4",
                              value="Press continue. You will be prompted with: **\"What’s this payment for?\"**. Select **Sending to a Friend**. *(Don't you see that option? Let us know in your ticket for alternative payment methods)*\n*Make sure you've completed this step correctly.* \n\n||https://prnt.sc/25u3g5o||",
                              inline=False)
        paypalEmbed.add_field(name="Step 5",
                              value="Press continue. You will see the payment confirmation. If everything looks correct, press **Send.**",
                              inline=False)
        paypalEmbed.add_field(name="Step 6",
                              value="After you have sent the payment, send a screenshot of the payment summary.\n\n*Still not sure how to pay? Check out this video : https://youtu.be/t5jgBY8McFs*",
                              inline=False)
        await ctx.respond(embed=paypalEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def paypalcard(self, ctx):
        paypalcardEmbed = utils.embed(title="Paying with Credit/Debit ",
                                        description="Please follow steps.",
                                        color=discord.Color.green(),
                                        thumbnail="https://confighub.photos/images/OfYyIx8vE0v0smBEzI1o5GTzD.png")
        paypalcardEmbed.add_field(name="Step 1",
                                  value="**Visit our Paypal Donation Link : https://www.paypal.com/donate/?hosted_button_id=XBJTCZKW8JZ2E** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 2",
                                  value="**Enter the amount that you need to pay.** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 3",
                                  value="**CLICK THE BUTTON says: I'd like to add $0.xx to my donation to help offset the cost of processing fees. Then, click:** *Donate with a debit or credit card* ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Step 4",
                                  value="**Please leave a note with the following contents:** ",
                                  inline=False)
        paypalcardEmbed.add_field(name="Note", value="**I'm discordname#xxxx**",
                                  inline=False)
        paypalcardEmbed.add_field(name="Example", value="https://prnt.sc/1tldq62", inline=False)
        await ctx.respond(embed=paypalcardEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def amazon(self, ctx):
        amazonEmbed = utils.embed(title="Paying With Giftcards",
                                    description="Please follow steps.", color=discord.Color.purple())
        amazonEmbed.add_field(name="Step 1",
                              value="Visit any website that sells **Amazon __*Turkey*__ Giftcards**. Here is one that I recommend: https://eneba.com/amazon-amazon-gift-card-100-try-turkey",
                              inline=False)
        amazonEmbed.add_field(name="Step 2", value="**Buy the giftcard, and get the code.**", inline=False)
        amazonEmbed.add_field(name="Step 3", value="Please **send the giftcard code in the TICKET**, and ping wovl.",
                              inline=False)
        await ctx.respond(embed=amazonEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def venmo(self, ctx):
        venmoEmbed = utils.embed(title="Paying With Venmo",
                                 description="Please follow steps.",
                                 color=discord.Color.purple())
        venmoEmbed.add_field(name="Step 1",
                             value="Please send your money to **@snagadreem** on VENMO",
                             inline=False)
        venmoEmbed.add_field(name="Step 2", value="**Send the screenshot of payment.**", inline=False)
        await ctx.respond(embed=venmoEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def cashapp(self, ctx):
        cashappEmbed = utils.embed(title="Paying With Cashapp",
                                   description="Please follow steps.",
                                   color=discord.Color.purple())
        cashappEmbed.add_field(name="Step 1",
                               value="Please send your money to **$snagadreem** on CASHAPP",
                               inline=False)
        cashappEmbed.add_field(name="Step 2", value="**Send the screenshot of payment.**", inline=False)
        await ctx.respond(embed=cashappEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def methods(self, ctx):
        methodsEmbed = utils.embed(title="Accepted Payment Methods",
                                     description="Please read below **carefully**.", color=discord.Color.purple(),
                                     thumbnail="https://cdn.discordapp.com/attachments/895770715918336023/927598609472585738/currency-large-gold-stack.png")
        methodsEmbed.add_field(name="Paypal",
                               value="We accept only **FRIENDS AND FAMILY** payments, you get exact amount",
                               inline=False)
        methodsEmbed.add_field(name="Crypto Coins",
                               value="We accept your Crypto payments, also you get **10% DISCOUNT**", inline=False)
        methodsEmbed.add_field(name="Debit & Credit Card", value="We accept your card payments, you get exact amount",
                               inline=False)
        methodsEmbed.add_field(name="Venmo", value="We accept your Venmo Payments, **you need to pay 10% MORE**",
                               inline=False)
        methodsEmbed.add_field(name="Cashapp", value="We accept your Cashapp Payments, **you need to pay 10% MORE**",
                               inline=False)
        methodsEmbed.add_field(name="**PHYSICAL** AMAZON.COM (USD)  GIFT CARDS",
                               value="We accept **PHYSICAL** Amazon Gift Cards as Payment (you must to send photo of physical gift card),**you get 50% of its value**",
                               inline=False)
        methodsEmbed.add_field(name="**Turkey** Gift cards",
                               value="We accept **Turkey** Gift cards (Amazon.com.tr or something else in Turkey) as Payment, you get exact amount",
                               inline=False)
        methodsEmbed.add_field(name="Steam Gift cards", value="We accept Steam Gift cards, you get 70% of its value",
                               inline=False)
        methodsEmbed.add_field(name="**Paysafe / ALL OTHER GIFT CARDS**",
                               value="We **accept** Paysafe gift cards and also other type of Gift Cards. Create a **ticket** and **ask me for the amount you will get** ",
                               inline=False)
        await ctx.respond(embed=methodsEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def items(self, ctx):
        itemsEmbed = utils.embed(title="Your payment is confirmed",
                                   description="Thank you for the payment.", color=discord.Color.purple(),
                                 thumbnail="https://cdn.discordapp.com/attachments/895770715918336023/921819889956696084/856483163432812554.png")
        itemsEmbed.add_field(name="What will happen now?",
                             value="Now, im going to send you a list of items that we have in our stock. You will choose items that worths amount you buy, then we will trade you the items that you've selected.\n\n While waiting the list please get any **SHITTY EPIC OR LEGENDARY DUNGEON SWORDS OR SET PIECES** to put in trade menu (we're doing this to seen legit). If you dont have any go to the auction house and buy cheapest epic or legendary swords.\n\n **After trade you can sell items on auction house or use them**",
                             inline=False)
        await ctx.respond(embed=itemsEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def done(self, ctx):
        doneEmbed = utils.embed(title="Transfer Successfully Completed",
                                  description="Thank you for choosing us for buying coins and also thank you for **supporting my education**. I hope you enjoy with your coins in skyblock! \n\n **Please leave your review message by typing !vouch in this chat**",
                                  color=discord.Color.green(),
                                thumbnail="https://cdn.discordapp.com/attachments/895770715918336023/927587602440278016/fireworks.png")
        doneEmbed.add_field(name="Leaving Vouch",
                            value="**Please use vouch command like below:** \n\n`!vouch <score> (out of 5) <message>`\n\n **Example:** !vouch 5 i got my +120M thank you so much",
                            inline=False)
        await ctx.respond(embed=doneEmbed)

    @tag.command()
    @has_permissions(kick_members=True)
    async def faq(self, ctx):
        faqEmbed = utils.embed(title="Frequently Asked Questions",
                                 description="Please read below **before creating support ticket**.",
                                 color=discord.Color.purple(),
                                footer=f"If you still have got questions, feel free to create support ticket \n{ctx.guild.name}.")
        faqEmbed.add_field(name="**WHO ARE YOU? WHERE AM I?**",
                           value="Currently you are in the **Best Skyblock Coin Shop** You can buy skyblock coins and skyblock islands here. And also you can try your chance on Giveaways",
                           inline=False)
        faqEmbed.add_field(name="**CAN I GET FREE COINS?**",
                           value="**NO**, you **CAN NOT** get free coins here,but you can try your luck in daily-monthly-shock giveaways",
                           inline=False)
        faqEmbed.add_field(name="**HOW DOES IT WORK**",
                           value="For now, you need to create a ticket to order coins. You need to answer some questions in ticket.",
                           inline=False)
        faqEmbed.add_field(name="**HOW CAN I TRUST YOU?**",
                           value="Most of people blame us as Scammer immediately after they join. Thats really annoying. Before all please check our <#896047999472525342>. You are free to DM any random buyer,and also i have got over 500 closed tickets. I can prove you extra details if you still think we're scammer. (also we're using discord bot to Backup and also **Protect our customers from reporters** They are not fake).",
                           inline=False)
        faqEmbed.add_field(name="**CAN I GET BANNED IF I BUY COINS & ISLAND?**",
                           value="There is a small ban chance on coin transactions. But we are always **changing our stock accounts** and using the **safest trade methods** to protect our customers, If you dont tell anyone that you bought coins or act like dumb you will not get banned also, \n**islands have no ban risk**",
                           inline=False)
        faqEmbed.add_field(name="**ARE YOU SELLING DUPED/SCRIPTED COINS?**",
                           value="No, I am using islands that I didnt add as stocks. They are 100% Legit coins they are **not** scripted or duped",
                           inline=False)
        faqEmbed.add_field(name="**CAN I BUY ITEMS?**",
                           value="Yes, you can pay for item's value and i can buy the item you want and trade it to you ",
                           inline=False)
        faqEmbed.add_field(name="**HOW DO ISLANDS WORK?**",
                           value="Before all you need a minecraft account **that you own** After payment i will /coopadd you then i leave the island. So the island will be yours. Basic  ",
                           inline=False)
        faqEmbed.add_field(name="**CAN I BUY ISLANDS WITH COINS?**", value="No you **CAN NOT** buy islands with coins",
                           inline=False)
        faqEmbed.add_field(name="**HOW CAN I WIN GIVEAWAY**",
                           value="Just react to the giveaway message with :tada: \n**YOU NEED SO MUCH LUCK TO WIN** ",
                           inline=False)
        faqEmbed.add_field(name="**CAN I SELL MY COINS & ISLAND HERE **",
                           value="Coming soon..", inline=False)
        faqEmbed.add_field(name="**ARE THERE ANY MINIMUM ORDER LIMIT**",
                           value="Minimum order value is **10 USD** worth", inline=False)
        faqEmbed.add_field(name="HOW CAN I JOIN TO THE BACKUP SERVER", value="There is no current backup server.",
                           inline=False)
        faqEmbed.set_thumbnail(
            url="https://media.discordapp.net/attachments/895770715918336023/929767882366283816/faq.png")
        await ctx.respond(embed=faqEmbed)


def setup(client):
    client.add_cog(Tags(client))
