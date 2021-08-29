# Imports
import discord
from discord.ext import commands,tasks
import random
import asyncpraw
import time
from asyncpraw.reddit import Subreddit
import json

ap_channel_list = []

#  Create a class 'meme' which inherits from the 'commands.Cog' class
class meme(commands.Cog):

    def __init__(self, client):
        self.client = client

    # 'Cog.listener' event which triggers autoposting in servers where it is enabled
    @commands.Cog.listener()
    async def on_ready(self):
        with open ('./cogs/autoid.json', 'r') as f:
            ap_channels = json.load(f)
        for i in ap_channels:
            if (ap_channels[i] != "0"):
                ap_channel_list.append(int(ap_channels[i]))
        self.test.start()


    # Command for getting a meme
    @commands.command()
    async def memes(self, ctx, arg : int, x = 1):

        with open('./cogs/credentials.json', 'r') as from_file:
            data = from_file.read()
        credentials = json.loads(data)
        
        reddit = asyncpraw.Reddit(**credentials)

        memes_list = []
        f = open('./cogs/subreddit.txt', 'r')
        memes_list = f.readlines()
        f.close()

        if (x <= 5):
            if (arg > 0) and (arg <= len(memes_list)):
                subred = str(memes_list[arg-1])
                subreddit = await reddit.subreddit(subred)
                all_meme = []
                    
                hot = subreddit.hot(limit = 500)
                async for submission in hot:
                    all_meme.append(submission)
                    
                for i in range(x):
                    random_sub = random.choice(all_meme)
                    name = random_sub.title
                    url = random_sub.url
                    author = random_sub.author
                    pst = "https://www.reddit.com" + random_sub.permalink
                    
                    embed = discord.Embed(title = name , url = pst, description = f'Created by u\{author}', colour = discord.Color.purple())
                    embed.set_author(name = f'r\ {subred}')
                    embed.set_image(url = url)
                    embed.set_footer(text = f'Ordered by {ctx.author}', icon_url = ctx.author.avatar_url)
                    await ctx.send(embed = embed)
                    
            else:
                embed_inc_index = discord.Embed(title="Incorrect Index", description = " Trigger the <memelist> command for getting correct index" , color = discord.Color.blue(), inline = False)
                await ctx.send(embed= embed_inc_index)
                
        else:
            embed_rng_exc = discord.Embed(title = "Range Exceeded", description = "We are bound to provide you maximum 5 memes at a time", color = discord.Color.green())
            await ctx.send(embed = embed_rng_exc)

    # Command for starting AutoPost
    @commands.command(aliases = ['apon'])
    async def autoposton(self, ctx, channel : commands.TextChannelConverter):
        with open ('./cogs/autoid.json', 'r') as f:
            ap_channels = json.load(f)

        ap_channels[str(ctx.guild.id)] = str(channel.id)

        with open ('./cogs/autoid.json', 'w') as f:
            json.dump(ap_channels, f, indent = 4)
        ap_channel_list.append(channel.id)

    # Command for ending AutoPost
    @commands.command(aliases = ['apoff'])
    async def autopostoff(self, ctx):
        with open ('./cogs/autoid.json', 'r' ) as f:
            ap_channels = json.load(f)
        del_channel = int(ap_channels[str(ctx.guild.id)])
        ap_channels[str(ctx.guild.id)] = "0"

        with open ('./cogs/autoid.json', 'w') as f:
            json.dump(ap_channels, f, indent = 4)
        ap_channel_list.remove(del_channel)


    # Loop for autoposting every 15 minutes
    @tasks.loop(minutes = 15)
    async def test(self):

        with open('./cogs/credentials.json', 'r') as from_file:
            data = from_file.read()
        credentials = json.loads(data)

        reddit = asyncpraw.Reddit(**credentials)
        memes_list = []
        f = open('./cogs/subreddit.txt', 'r')
        memes_list = f.readlines()
        f.close()
        
        subzero = random.choice(memes_list)
        subreddit = await reddit.subreddit(subzero)
        all_meme = []
        hot = subreddit.hot(limit = 500)
        async for submission in hot:
            all_meme.append(submission)
        random_sub = random.choice(all_meme)
        name = random_sub.title
        url = random_sub.url
        author = random_sub.author
        pst = "https://www.reddit.com" + random_sub.permalink
                    
        embed = discord.Embed(title = name, url = pst, description = f'Created by u\{author}', colour = discord.Color.purple())
        embed.set_author(name = f'r\ {subzero}')
        embed.set_image(url = url)
        for channel_id in ap_channel_list:
            channel = self.client.get_channel(channel_id)
            await channel.send(embed = embed)

    # Command for getting the Subreddit List
    @commands.command()
    async def sublist(self, ctx):
        f = open('./cogs/subreddit.txt', 'r')
        memes_list = f.readlines()
        f.close()
        s = []
        for x in range(1,(len(memes_list)+1)):
            m = str(x) + f'. r\{memes_list[x-1]}'
            s.append(m)
        meme_list = ''.join(s)
        embed = discord.Embed(title = "Subreddit List", description = f"{meme_list}" , color = discord.Color.green(), inline = False)
        await ctx.send(embed = embed)

    # Command for adding a subreddit in the list (admin only command)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def addsub(self, ctx, s):
        with open('./cogs/subreddit.txt', 'a+') as f5:
            f5.seek(0)
            data = f5.read(10000)
            if len(data) > 0 :
                f5.write("\n")
            f5.write(s)
            f5.close()

        memes_list = []
        f = open('./cogs/subreddit.txt', 'r')
        memes_list = f.readlines()
        f.close()
        s = []
        for x in range(1, (len(memes_list)+1)):
            m = str(x) + f'.  r\{memes_list[x-1]}'
            s.append(m)
        meme_list = ''.join(s)
        embed = discord.Embed(title = "Subreddit Added Successfully", color = discord.Color.blue(), inline = False)
        embed.add_field(name = "Updated Subreddit List:\n", value = f"{meme_list}" , inline = False)
        await ctx.send(embed = embed)


    # Command for deleting a subreddit in the list (admin only command)
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def delsub(self, ctx, m : int):
        memes_list = []
        with open('./cogs/subreddit.txt', 'r+') as fp:
            memes_list = fp.readlines()
            if (m>0) and (m<=len(memes_list)):
                fp.seek(0)
                fp.truncate()
                memes_list.pop(m-1)
                memes_list[-1] = memes_list[-1].strip()
                fp.writelines(memes_list)
                fp.close()

                with open('./cogs/subreddit.txt', 'r') as sp:
                    list1 = sp.readlines()
                    sp.close()
                    s = []
                    for x in range(1, (len(list1)+1)):
                        m = str(x) + f'.  r\{list1[x-1]}'
                        s.append(m)
                    meme_list = ''.join(s)
                    embed = discord.Embed(title = "Subreddit Deleted Successfully", color = discord.Color.blue(), inline = False)
                    embed.add_field(name = "Updated Subreddit List:\n", value = f"{meme_list}" , inline = False)
                    await ctx.send(embed = embed)
            else:
                embed_inc_index= discord.Embed(title="Incorrect Index", 
                description = f"We only have {len(memes_list)} subreddits enlisted in our Subreddit List. \nTrigger the <sublist> command for getting correct Subreddit list" , 
                color = discord.Color.blue(), inline=False)
                await ctx.send(embed= embed_inc_index)

    # Error handling for 'meme' command
    @memes.error
    async def memes_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title = "Missing Required Arguement",  description = " Trigger the <memelist> command for getting correct index", color = discord.Color.blue())      
            embed.set_footer(text = "correct command: <prefix>memes <subreddit_index> <no.of_memes(limit=5)>")
            await ctx.send(embed = embed)

    # Error handling for 'addsub' command
    @addsub.error
    async def addsub_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed_not_admin = discord.Embed(title = "{}, you are not an Administrator".format(ctx.author) , color= discord.Color.magenta())
            await ctx.send(embed = embed_not_admin)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_miss_req_arg = discord.Embed(title = "Missing Required Argument",  color = discord.Color.magenta())
            embed_miss_req_arg.set_footer(text = "correct command: <prefix>addsub  <correct subreddit name>")
            await ctx.send(embed = embed_miss_req_arg)
        
    # Error handling for 'delsub' command
    @delsub.error
    async def delsub_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed_not_admin = discord.Embed(title = "{}, you are not an Administrator".format(ctx.author), color = discord.Color.magenta())
            await ctx.send(embed = embed_not_admin)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed_miss_req_arg = discord.Embed(title = "Missing Required Arguments", color = discord.Color.magenta())
            embed_miss_req_arg.set_footer(text = "correct command: <prefix>delsub  <index value of subreddit>")
            await ctx.send(embed = embed_miss_req_arg)
        elif isinstance(error, commands.BadArgument):
            embed_correct_req_arg = discord.Embed(title = "Correct Required Argument", color = discord.Color.magenta())
            embed_correct_req_arg.set_footer(text = "correct command: <prefix>delsub  <index value of subreddit>")
            await ctx.send(embed = embed_correct_req_arg)
       
# Setup Cogs 'meme'
def setup(client):
    client.add_cog(meme(client))