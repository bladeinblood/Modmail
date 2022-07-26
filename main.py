import disnake
from disnake.ext import commands
import sqlite3
import os


connection = sqlite3.connect('prefixes.db')
cur = connection.cursor()

def command_prefix(client, message:disnake.Message):

    return(cur.execute("SELECT prefix FROM prefixes WHERE guild = ?", (message.guild.id,)).fetchone())

client = commands.Bot(command_prefix=command_prefix)
client.remove_command("help")

from datetime import datetime

@client.slash_command(name="ban")
@commands.has_permissions(administrator = True)
async def ban(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason):

  await member.ban(reason=reason)
  await inter.response.send_message(embed=disnake.Embed(title=f"Ban {member.name}#{member.discriminator}", description = f"Reason: {reason}\nModerator: {inter.author}\nTime: {disnake.utils.format_dt(disnake.utils.utcnow())}"))

#@client.event
#async def on_slash_command_error(inter, error):
#  if isinstance(error, commands.CommandInvokeError):
#    await inter.send("Недостаточно прав")

@client.command()
@commands.has_permissions(administrator = True)
async def ban(ctx, member: disnake.Member, reason):

  await member.ban(reason=reason)
  await ctx.send(embed=disnake.Embed(title=f"Ban {member.name}#{member.discriminator}", description = f"Reason: {reason}\nModerator: {ctx.author}\nTime: {disnake.utils.format_dt(disnake.utils.utcnow())}"))

@client.event
async def on_ready():
    print('con')
    
    
@client.event
async def on_guild_join(guild):

    cur.execute("INSERT INTO prefixes VALUES (?, ?)", (guild.id, "."))
    connection.commit()

@client.event
async def on_guild_remove(guild):

    cur.execute("DELETE FROM prefixes WHERE guild = ?", (guild.id,))
    connection.commit()

@client.command()
async def changeprefix(ctx, prefix):

    if cur.execute("SELECT guild FROM prefixes WHERE guild = ?", (ctx.guild.id,)).fetchone() is None:
        await ctx.send("Айди вашей гильдии нет в базе данных, пере приглосите бота пожалуйста либо напишите команду: setstandart")
    else:
        cur.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, ctx.guild.id))
        connection.commit()
        await ctx.send("Wait a second...")

@client.slash_command(name="changeprefix")
async def changepref(interaction, prefix):

    if cur.execute("SELECT guild FROM prefixes WHERE guild = ?", (interaction.guild.id,)).fetchone() is None:
        await interaction.send("Айди вашей гильдии нет в базе данных, пере приглосите бота пожалуйста либо напишите команду: setstandart")
    else:
        cur.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (prefix, interaction.guild.id))
        connection.commit()
        await interaction.send("Wait a second...")

from disnake import ButtonStyle, Button

class Buttons(disnake.ui.View):

    def __init__(self):

        super().__init__(timeout=0)

    @disnake.ui.button(label="Изменить префикс", style=ButtonStyle.red)
    async def changeprefix(self, button: disnake.ui.Button, interaction: disnake.ApplicationCommandInteraction):
        await interaction.send("Prefix:")

        res = await client.wait_for("message", check=lambda x: x.author.id == interaction.author.id)

        cur.execute("UPDATE prefixes SET prefix = ? WHERE guild = ?", (res.content, interaction.guild.id))
        connection.commit()
        await interaction.send("Successfully")

@client.slash_command()
async def setstandart(interaction):

    if cur.execute("SELECT guild FROM prefixes WHERE guild = ?", (interaction.guild.id,)).fetchone() is None:
        cur.execute("INSERT INTO prefixes VALUES (?, ?)", (interaction.guild.id, "."))
        connection.commit()
        await interaction.send("Successfully")
        

    else:
        await interaction.send(embed=disnake.Embed(title="Your server ID is already in the database"), view = Buttons())


@client.message_command(name="report")
async def report(inter: disnake.ApplicationCommandInteraction, message: disnake.Message):
    cur.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?)", (message.author.id, message.jump_url, inter.author.id, int(datetime.now().timestamp()), inter.guild.id))
    connection.commit()

    embed = disnake.Embed(title=f"Report: {message.author}", description=f"```Sender: {inter.author}```\nTime: {disnake.utils.format_dt(disnake.utils.utcnow())}")
    embed.add_field(name="Proof", value=f"{message.jump_url}", inline=False)
    embed.add_field(name="Tralalala", value=f"{message.content}", inline=False)

    await inter.guild.get_channel(1001428415875924029).send(embed=embed)

@client.slash_command()
async def reports(inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
    cur.execute("SELECT id, sender, time, proof FROM reports WHERE guild = ? AND id = ?", (inter.guild.id, member.id))
    data = cur.fetchall()
    embed = disnake.Embed(title=f"Reports: {member.name}")
    if data:
        i=0
        for reportid, sender, time, proof in data:
            embed.add_field(name=f"Report {i}", value=f"```Reported user id: {reportid}\nSender: {sender}```\nTime: {disnake.utils.format_dt(time)}\n```Proof: {proof}```", inline=False)
            i+=1
        await inter.response.send_message(embed=embed)
    else:
        await inter.send("No reports")

@client.command()
async def hi(ctx):

    await ctx.send("hi")

if __name__ == "__main__":
    cur.execute("CREATE TABLE IF NOT EXISTS prefixes (guild TEXT, prefix TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS reports (id TEXT, proof TEXT, sender TEXT, time TEXT, guild TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS messages_ban (content TEXT, guild TEXT)")
    connection.commit()

@client.slash_command(description = "There can only be one forbidden word")
@commands.has_permissions(administrator=True)
async def add_ban_word(inter: disnake.ApplicationCommandInteraction, word):

  cur.execute("INSERT INTO messages_ban VALUES (?, ?)", (word, inter.guild.id))
  connection.commit()

  await inter.send("Yes")

@client.slash_command()
@commands.has_permissions(administrator=True)
async def remove_all_ban_word(inter: disnake.ApplicationCommandInteraction, word):
  cur.execute("DELETE FROM messages_ban WHERE guild = ?", (inter.guild.id,))
  connection.commit()
  await inter.send("Yes")

@client.event
async def on_message(message):
  if str(cur.execute("SELECT content FROM messages_ban WHERE guild = ?", (message.guild.id,)).fetchone()[0]) in message.content:
    await message.delete()
  
  await client.process_commands(message)
  








client.run("modmail-token-here)")
