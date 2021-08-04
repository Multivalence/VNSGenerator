import discord
import os
from discord.ext import commands
import aiofiles
import aiosqlite

class Startup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.initializeDB())



    async def updateAccounts(self):

        self.bot.accounts = dict()

        self.bot.gen_channels = list()

        for filename in os.listdir('./accounts'):

            async with aiofiles.open(f"./accounts/{filename}", 'r', encoding='utf-8') as textFile:
                accounts = await textFile.read()
                accounts = accounts.splitlines()


            self.bot.accounts[filename[:-4]] = [i.replace("\ufeff","") for i in accounts if i not in self.bot.used_accounts]

            self.bot.gen_channels.append(filename[:-4])




    async def updateUsedAccounts(self):

        async with self.bot.db.execute("SELECT * FROM accounts") as cursor:
            rows = await cursor.fetchall()

            self.bot.used_accounts = [i[0] for i in rows]
            print("USED ACCOUNTS",self.bot.used_accounts)

        await self.updateAccounts()




    async def initializeDB(self):

        self.bot.db = await aiosqlite.connect('used.db')

        sql = """CREATE TABLE IF NOT EXISTS accounts (
            account TEXT PRIMARY KEY
            )
        """

        await self.bot.db.execute(sql)
        await self.bot.db.commit()

        await self.updateUsedAccounts()




    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name} | {self.bot.user.id}')




    #Setup
def setup(bot):
    bot.add_cog(Startup(bot))