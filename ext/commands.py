import discord
import random
import aiofiles
import aiohttp
from discord.ext import commands
from sqlite3 import IntegrityError
from ext.checks import is_correct_channel
from typing import Union


class NoMoreAccounts(commands.CommandError):
    pass

class SomethingWentWrong(commands.CommandError):
    pass


class FileNotValid(commands.CommandError):
    pass


class FileConverter(commands.Converter):

    async def convert(self, ctx : commands.Context, argument : Union[discord.TextChannel, str]) -> tuple:

        try:
            t = await commands.TextChannelConverter().convert(ctx, argument)
            argument = t.name

        except commands.BadArgument:
            pass



        if argument not in ctx.bot.gen_channels:
            raise FileNotValid

        return (f"./accounts/{argument}.txt", argument)



class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



    async def cog_command_error(self, ctx, error):

        #Gets original attribute of error
        error = getattr(error, "original", error)

        if isinstance(error, NoMoreAccounts):
            await ctx.send("Uh oh. There are no more accounts available for this channel. Please ask an administrator to refill it.")

        elif isinstance(error, SomethingWentWrong):
            await ctx.send("An internal error occured. Please let an administrator know!")

        elif isinstance(error, FileNotValid):
            await ctx.send("The channel you provided is not a valid gen channel!")




    @commands.has_permissions(administrator=True)
    @commands.command(name='add', description='Command to add an account')
    async def add(self, ctx, channel : FileConverter, username : str = None, password : str = None):

        if username is None or password is None:

            if len(ctx.message.attachments) == 0:
                return await ctx.send("You have not provided any Username, Password, or Text File")

            url = ctx.message.attachments[0].url

            if not url.endswith('.txt'):
                return await ctx.send("Please make sure your attachment is a txt file!")

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    x = await resp.read()
                    content = x.decode('utf-8').splitlines()

            content[0].replace("\ufeff","")

            self.bot.accounts[channel[1]] += content

            content = ["\n" + i for i in content]

            async with aiofiles.open(channel[0], 'a') as textFile:
                await textFile.writelines(content)





        else:
            content = f"{username}:{password}"

            self.bot.accounts[channel[1]].append(content)

            content = "\n" + content

            async with aiofiles.open(channel[0], 'a') as textFile:
                await textFile.writelines(content)


        return await ctx.send("Successfully Added Data")









    @commands.guild_only()
    @commands.check(is_correct_channel)
    @commands.command(name='stock', description="Command to see how many accounts are left", aliases=['s','st'])
    async def stock(self, ctx):


        if len(self.bot.accounts[ctx.channel.name]) == 0:
            c = discord.Colour.red()

        else:
            c = discord.Colour.green()

        embed = discord.Embed(
            title="Stock",
            description=ctx.channel.mention,
            colour=c
        )

        embed.add_field(name="Accounts remaining", value=str(len(self.bot.accounts[ctx.channel.name])))

        await ctx.send(embed=embed)





    @commands.guild_only()
    @commands.check(is_correct_channel)
    @commands.cooldown(1, 14400, commands.BucketType.user)
    @commands.command(name='generate', description="Command to generate account", aliases=['gen','g'])
    async def generate(self, ctx):

        if len(self.bot.accounts[ctx.channel.name]) == 0:
            raise NoMoreAccounts

        account = random.choice(self.bot.accounts[ctx.channel.name])

        self.bot.accounts[ctx.channel.name].remove(account)
        self.bot.used_accounts.append(account)



        sql = 'INSERT INTO accounts(account) VALUES (?)'

        try:
            await self.bot.db.execute(sql, (account,))
            await self.bot.db.commit()

        except IntegrityError:
            raise SomethingWentWrong




        embed = discord.Embed(
            title="Here's your account. Have fun!",
            description=ctx.channel.mention,
            colour=discord.Colour.gold()
        )

        username, password = account.split(":")

        embed.add_field(name="Username", value=username)
        embed.add_field(name="Password", value=password)

        await ctx.author.send(embed=embed)




#Setup
def setup(client):
    client.add_cog(Commands(client))

