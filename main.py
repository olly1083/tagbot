import discord
import json
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)  # BOT PREFIX




##########################
token = 'MTI0Mzk4MjcyNTk2NzM4MDUzMA.GRsXnb.bVpFVrzW7yLp4dwH5xpu9Upvbf0SglwG7o8XWs'
##########################

XP_PER_MESSAGE = 10
LEVEL_UP_XP = 100

# Load levels data from levels.json
try:
    with open('levels.json', 'r') as f:
        levels_data = json.load(f)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    levels_data = {}


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


####################################levels#####################################################

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Add XP for the user
    user_id = str(message.author.id)
    levels_data[user_id] = levels_data.get(user_id, {"xp": 0, "level": 1})
    levels_data[user_id]["xp"] += XP_PER_MESSAGE

    # Check if the user leveled up
    if levels_data[user_id]["xp"] >= levels_data[user_id]["level"] * LEVEL_UP_XP:
        levels_data[user_id]["level"] += 1
        await message.channel.send(f"Congratulations, {message.author.mention}! You've reached level {levels_data[user_id]['level']}!")

    # Save levels data to levels.json
    with open('levels.json', 'w') as f:
        json.dump(levels_data, f)

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def xp(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    user_id = str(user.id)
    xp = levels_data.get(user_id, {"xp": 0})["xp"]
    level = levels_data.get(user_id, {"level": 1})["level"]
    await ctx.send(f"{user.display_name} has {xp} XP and is at level {level}.")

@bot.command()
async def leaderboard(ctx):
    sorted_users = sorted(levels_data.items(), key=lambda x: x[1]["xp"], reverse=True)
    leaderboard_embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for index, (user_id, data) in enumerate(sorted_users[:10], start=1):
        user = ctx.guild.get_member(int(user_id))
        if user:
            leaderboard_embed.add_field(name=f"{index}. {user.display_name}", value=f"XP: {data['xp']} | Level: {data['level']}", inline=False)
    await ctx.send(embed=leaderboard_embed)



#################################### KICK ######################################################


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has kicked. reason: {reason}')

############################################## BAN ###################################################


@bot.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(member + 'Banned for', reason )

############################################## UNBAN ##################################################

@bot.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()

    member_name, member_discriminator = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f"Unbanned: {user.mention}")

############################################    PING     ###########################################

@bot.command(name="ping", pass_context=True, aliases=["latency"])
async def ping(ctx):
    embed = discord.Embed(title="__**✅ PING**__", colour=discord.Color.green(), timestamp=ctx.message.created_at)
    embed.add_field(name="Bot latency :", value=f"`{round(bot.latency * 1000)} ms`")

    await ctx.send(embed=embed)


############################################    CLEAR   ###########################################



@bot.command(name='clear', aliases=['c'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
        await ctx.channel.purge(limit=amount)
        Embed = discord.Embed(title='✅ SUSSY!', timestamp=ctx.message.created_at,description=f'{ctx.author.mention} Deleted {amount} messages!', color=0x00ff00)
        await ctx.message.channel.send(embed=Embed)



############################################    AVATAR      ###########################################

@bot.command(name='avatar', aliases=['av','pfp'])
async def avatar(ctx, user:discord.Member=None):
    embed = discord.Embed(title=user.name, description=":DD", color=0x0026e6)
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)



############################################    SETNICK @MENTION    ###########################################


@bot.command(pass_context=True, aliases=['nick'])
@commands.has_permissions(manage_nicknames=True)
async def setnick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nick changed for {member.mention} ')


############################################    UNKNOWN COMMAND     ###########################################

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f":x: ", description=f"Unknown command `.help`", color=ctx.author.color)
        await ctx.send(embed=em)



############################################    SLOWMODE    ###########################################

@bot.command(name='slowmode', aliases=['slow'])
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!")

############################################    USER INFO    ###########################################

@bot.command(name='userinfo', aliases=['user'])
async def userinfo(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author
    date_format = "%a, %d %b %Y %I:%M %p"
    embed = discord.Embed(color=0xdfa3ff, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar.url)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join position", value=str(members.index(user)+1))
    embed.add_field(name="Registered", value=user.created_at.strftime(date_format))
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
    perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
    embed.add_field(name="Permissions", value=perm_string, inline=False)
    embed.set_footer(text='user ID: ' + str(user.id))
    return await ctx.send(embed=embed)



############################################    ALIASES    ###########################################

@bot.command(name='aliases', aliases=['al'])
async def aliases(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author
    embed = discord.Embed(title="ALIASES LIST", description="✔✔✔", color=0x5b0fcc)
    embed.add_field(name=".aliases ✅", value=".`al` ", inline=False)
    embed.add_field(name=".fuck :middle_finger: ", value="`.fck <@mention>` ", inline=False)
    embed.add_field(name=".ping :robot: ", value="`.latency`", inline=False)
    embed.add_field(name=".clear :shield: ", value="`.c` ", inline=False)
    embed.add_field(name=".avatar 👨🏿‍🦰", value="`.pfp` or `.av` ", inline=False)
    embed.add_field(name=".userinfo :smirk: ", value="`.user <@mention>`", inline=False)
    embed.add_field(name=".serverinfo :white_heart:", value="`.server` or `.ser`", inline=False)
    embed.add_field(name=".setnick :pencil2: ", value="`.nick <@mention> <new username>`", inline=False)
    embed.add_field(name=".slowmode :no_bell: ", value="`.slow` ", inline=False)
    embed.set_footer(text="⭐")
    await ctx.send(embed=embed)





############################################    HELP    ###########################################
bot.remove_command('help')  # Delete help


class MyClient:
    pass


client = MyClient()



@bot.command()
async def help(ctx, user: discord.Member = None):
    embed = discord.Embed(title="TAG BOT 2.0 MADE IN PYTHON",url="https://discord.com/oauth2/authorize?client_id=1243982725967380530",color=0x12abed)
    embed.add_field(name=".help", value="cmd list ℹ", inline=False)
    embed.add_field(name=".leaderboard", value="showes the leaderboard of xp/levels", inline=False)
    embed.add_field(name=".ping", value="Bot Ping 〽", inline=False)
    embed.add_field(name=".clear", value="del messages `.clear <amount>` ✉", inline=False)
    embed.add_field(name=".avatar", value="ur pfp `.av <@mention>` 👨🏿‍🦰", inline=False)
    embed.add_field(name=".kick", value="kick user from server `.kick <@mention> <reason>` 📢", inline=False)
    embed.add_field(name=".ban", value="Ban user from server `.ban <@mention> <reason>` 📢", inline=False)
    embed.add_field(name=".userinfo", value="shows user join date etc. `.userinfo @mention` ☢", inline=False)
    embed.add_field(name=".server", value="server info ℹ", inline=False)
    embed.add_field(name=".setnick", value="new nickname for @mention `.setnick @mention <new nickname>` ✏", inline=False)
    embed.add_field(name=".slowmode", value="time in sec 🕐 ex. `.slow 2`", inline=False)
    embed.add_field(name=".aliases", value="commands shortcuts `.al` ⚡", inline=False)
    embed.set_footer(text="⭐")
    await ctx.send(embed=embed)


############################################    SERVER INFO    ###########################################


@bot.command(name='serverinfo', aliases=['ser', 'server'])
async def serverinfo(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author
    embed = discord.Embed(title=f"{ctx.guild.name} Info", description="Information of this Server", color=discord.Colour.red())
    embed.add_field(name='🆔 Server ID', value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name='📆 Created On', value=ctx.guild.created_at.strftime("%d %b %Y"), inline=True)
    embed.add_field(name='👑 Owner', value=f"{ctx.guild.owner.mention}", inline=True)
    embed.add_field(name='👥 Members', value=f'{ctx.guild.member_count} Members', inline=True)
    embed.add_field(name="⭐", value="⭐", inline=True)
    embed.add_field(name='💬 Channels', value=f'{len(ctx.guild.text_channels)} Text | {len(ctx.guild.voice_channels)} Voice', inline=True)


    await ctx.send(embed=embed)




############################################    BOT STATUS       ###########################################

@bot.event
async def on_ready():
    activity = discord.Game(name=".help", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f'\n\nLogged in as: {bot.user.name} \nID: {bot.user.id}\nDiscord Version: {discord.__version__}\n')



bot.run(token,reconnect=True)
