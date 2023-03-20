import disnake
from disnake import Button, ButtonStyle, Member, Role, TextInputStyle
from disnake.ext import commands
import random
import asyncio
import re
import sqlite3



from config import TOKEN, server_rules

bot = commands.Bot(command_prefix="/", intents=disnake.Intents.all())


con = sqlite3.connect('users.db')
cur = con.cursor()

@bot.event
async def on_member_join(member):
    if cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cur.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0)')
        con.commit()
    else:
        pass


@bot.event
async def on_ready():
    game = disnake.Activity(name="Dota 2", type=disnake.ActivityType.playing)
    await bot.change_presence(status=disnake.Status.idle, activity=game)
    print("Bot is ready")

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INT,
        name TEXT,
        warn INT
    )""")
    con.commit()
    for guild in bot.guilds:
        for member in guild.members:
            if cur.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cur.execute(f'INSERT INTO users VALUES ({member.id}, "{member}", 0)')
                con.commit()
            else:
                pass





@bot.event
async def on_message(message: disnake.Message):
    if message.author.bot:
        return
    '''if message.author.guild_permissions.administrator:
        return'''
    
    server_links = re.findall(r'(?:https?://)?discord\.gg/(\w+)', message.content) + re.findall(r"discord\.gg/(\w+)", message.content)
    
    if server_links:

        await message.delete()
        
        guild = message.guild
        
        if guild:
            server_name = guild.name
        else:
            server_name = 'неизвестно'
        reason = "размещение ссылок на дискорд сервера"
        channel = bot.get_channel(1087150283752210452)
        cur.execute("UPDATE users SET warn = warn + {} WHERE id = {}".format(1,message.author.id))
        await channel.send(f"Выдано предупреждение для {message.author.name}({message.author.display_name}) по причине '{reason}'")
        await message.author.send(f"Вам выдано предупреждение по причине '{reason}'")



@bot.slash_command(description="Выдача ролей (Admin only)")
@commands.has_permissions(administrator=True)
async def role(ctx, member: disnake.Member, role: disnake.Role):
    await member.add_roles(role)





@bot.slash_command(description="Правила сервера(Admin only)")
@commands.has_permissions(administrator=True)
async def rules(ctx):
    embed = disnake.Embed(
    title="ПРАВИЛА СЕРВЕРА",
    description=server_rules,
    color=0xEF9E11
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1038566341252227132/1054058321730076702/41431C32-0485-481F-995A-6D186A87F787.gif")
    await ctx.send(embed=embed)




#just for fun system
@bot.slash_command(description="Случайное число от 1 до 100")
async def roll(ctx):
    await ctx.send(random.randint(1,101))




#CREATE_EMBED SYSTEM
@bot.slash_command(description="Создает embed сообщение, если url не треубется введите в последнем агрументе '-' (Admin only)")
@commands.has_permissions(administrator=True)
async def create_embed(ctx, title, main_text,url_if_u_need):
    if "https://" in url_if_u_need:
        embed = disnake.Embed(
        title=title,
        description=main_text,
        )
        embed.set_image(url=url_if_u_need)
        await ctx.send(embed=embed)
    elif 'tenor' in url_if_u_need:
        await ctx.send("Can`t use 'tenor', try again with other url", ephemeral=True)
    else:
        embed = disnake.Embed(
        title=title,
        description=main_text,
        )
        await ctx.send(embed=embed)




#GET_ROLE SYSTEM
@bot.slash_command(description="Выберете свои любимые роли в Dota 2(Admin only)")
@commands.has_permissions(administrator=True)
async def dota_positions(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(
        "Выберете свои любимые роли в Dota 2",
        components=[
            disnake.ui.Button(label="Carry", style=disnake.ButtonStyle.gray, custom_id="Carry"),
            disnake.ui.Button(label="Midlaner", style=disnake.ButtonStyle.gray, custom_id="Midlaner"),
            disnake.ui.Button(label="Offlaner", style=disnake.ButtonStyle.gray, custom_id="Offlaner"),
            disnake.ui.Button(label="Roamer", style=disnake.ButtonStyle.gray, custom_id="Roamer"),
            disnake.ui.Button(label="Hard Support", style=disnake.ButtonStyle.gray, custom_id="Hard Support")
        ],
    )

@bot.listen("on_button_click")
async def role_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id == "Carry":
        role_name = "Carry"
    elif inter.component.custom_id == "Midlaner":
        role_name = "Midlaner"
    elif inter.component.custom_id == "Offlaner":
        role_name = "Offlaner"
    elif inter.component.custom_id == "Roamer":
        role_name = "Roamer"
    elif inter.component.custom_id == "Hard Support":
        role_name = "Hard Support"
    else:
        return

    guild = inter.guild
    role = disnake.utils.get(guild.roles, name=role_name)

    if role in inter.author.roles:
        try:
            await inter.author.remove_roles(role)
            if not inter.response.is_done():
                await inter.response.send_message(f"Роль '{role_name}' была удалена.", ephemeral=True)
        except disnake.errors.Forbidden:
            await inter.response.send_message(f"Ошибка: У меня нет прав для удаления роли '{role_name}'.", ephemeral=True)
    else:
        try:
            await inter.author.add_roles(role)
            await inter.response.send_message(f"Роль '{role_name}' была добавлена.", ephemeral=True)
        except disnake.errors.Forbidden:
            await inter.response.send_message(f"Ошибка: У меня нет прав для выдачи роли '{role_name}'.", ephemeral=True)




#REGESTRATION IN TOURNAMENT SYSTEM
@bot.slash_command(description="Создает конпку для регестрации в турнире (Admin only)")
@commands.has_permissions(administrator=True)
async def create_questionnaire(inter):
    await inter.response.send_message(
        "Нажмите на кнопку, чтобы зарегестрироваться в турнире",
        components=[    
            disnake.ui.Button(label="Зарегестрироваться", style=disnake.ButtonStyle.gray, custom_id="create_tag_button"),
        ],
    )

@bot.listen("on_button_click")
async def tags_low(inter: disnake.AppCmdInter):
    channel = await inter.client.fetch_channel(1086634245025443850)
    if inter.channel.id != 1086341856817856593:
        return
    await inter.response.send_modal(
        title="Регестрация",
        custom_id="create_tag_low",
        components=[
            disnake.ui.TextInput(
                label="Имя/ник:",
                custom_id="Имя/ник:",
                style=disnake.TextInputStyle.short,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="Количество игр:",
                custom_id="Количество игр:",
                style=disnake.TextInputStyle.short,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="Количество ммр:",
                custom_id="Количество ммр:",
                style=disnake.TextInputStyle.short,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="ID в доте:",
                custom_id="ID в доте:",
                style=disnake.TextInputStyle.short,
                max_length=500,
            ),
            disnake.ui.TextInput(
                label="Мейн персы/сигнатурки:",
                custom_id="Мейн персы/сигнатурки:",
                style=disnake.TextInputStyle.short,
                max_length=500,
            ),
        ],
    )
    try:
        modal_inter: disnake.ModalInteraction = await bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "create_tag_low" and i.author.id == inter.author.id,
            timeout=600,
        )
    except asyncio.TimeoutError:
        return

    embed = disnake.Embed(title=f"Регестрация игрока @{inter.author}")
    for key, value in modal_inter.text_values.items():
        embed.add_field(name=key.capitalize(), value=value[:1024], inline=False)
    await modal_inter.response.send_message("Заявка принята!",ephemeral=True)
    await channel.send(embed=embed)




#WARN SYSTEM
def cheak_warns(user):
    if cur.execute('SELECT warn FROM users WHERE id = {}'.format(user.id)).fetchone()[0] == 3:
        user.send(f"Ваше количество предупреждений на сервере - 3, вам выдано наказание.")
    else: 
        pass 



@bot.slash_command(description="Посмотреть свое количество предупреждений")
async def my_warns(ctx):
    await ctx.send(f"Ваше количество предупреждений - {cur.execute('SELECT warn FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}", ephemeral=True)



@bot.slash_command(description="Выдает информацию о количестве варнов пользователя (Admin only)")
@commands.has_permissions(administrator=True)
async def user_warns(ctx, member: disnake.Member):
    await ctx.send(f"На данный момент количество предупреждений у {member} - {cur.execute('SELECT warn FROM users WHERE id = {}'.format(member.id)).fetchone()[0]}", ephemeral=True)



@bot.slash_command(description="Выдать предупреждение пользователю (Admin only)")
@commands.has_permissions(administrator=True)
async def warn(ctx, member: disnake.Member, reason):
    channel = await ctx.client.fetch_channel(1087150283752210452)
    cur.execute("UPDATE users SET warn = warn + {} WHERE id = {}".format(1,member.id))
    con.commit()

    await ctx.send(f"Пользователю {member} было выдано предупреждение по причине '{reason}', на данный момент его количество предупреждений - {cur.execute('SELECT warn FROM users WHERE id = {}'.format(member.id)).fetchone()[0]}",ephemeral=True)
    await channel.send(f"{ctx.author.mention} выдал предупреждение для {member.mention}({member.display_name}) по причине '{reason}'")
    await member.send(f"{ctx.author.mention} выдал предупреждение для вас по причине '{reason}'")
    


@bot.slash_command(description="Меняет количество предупреждений (Admin only)")
@commands.has_permissions(administrator=True)
async def set_warns(ctx, member: disnake.Member, new_amount):
    channel = await ctx.client.fetch_channel(1087150283752210452)
    cur.execute(f"UPDATE users SET warn = {new_amount} WHERE id = {member.id}")
    con.commit()
    await member.send(f"Количество предупреждений для вас обновлено до {new_amount}")
    await ctx.send(f"Количество предупреждений для {member.mention} обновлено до {new_amount}",ephemeral=True)
    await channel.send(f"{ctx.author.mention}({ctx.author.display_name}) обновил количество предупреждений для {member.mention}({member.display_name}) до {new_amount}")



#HELP SYSTEM
'''@bot.slash_command(description="Показывает информацию о любой команде в этом боте (в аргументе надо передать команду)")
async def help(ctx, command):
    coms = {"roll": "Выдает случайное число от 1 до 100",
            }'''




bot.run(TOKEN)