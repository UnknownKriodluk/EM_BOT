# coding=UTF-8
import os
import sys
import disnake
from disnake.ext.commands import has_permissions
from disnake.ext import commands
from background import keep_alive
import sqlite3
import asyncio
import time
import datetime
from partModerator import Admin
from partUser import partUser

partmoder = Admin
partser = partUser

base_xp_per_level = 100
intents = disnake.Intents.all()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)
slash_prefix = '/'
tz = datetime.timezone(datetime.timedelta(hours=3))
dt_obj = datetime.datetime.now(tz)
timme = dt_obj.strftime("%d.%m.%Y")
token = os.environ['token']

class main:
  client.remove_command("help")
  
  @client.event
  async def on_ready():
    await client.change_presence(status=disnake.Status.online,
                                 activity=disnake.Activity(
                                   type=disnake.ActivityType.listening,
                                   name=f"{slash_prefix}help"))
    print(f"[{client.user}]", " ====={Бот готов к работе}=====")
  
  
  @client.event
  async def on_member_ban(guild, user):
    await user.send("Вы были забанены на сервере EaverMine")
  
  
  @client.event
  async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
      await ctx.send("У вас недостаточно прав для использования этой команды!")
  
  def myotvetembed(message, last_username):
    embed = disnake.Embed(title=f"Я => {last_username}",
                          description=f'{message}',
                          color=disnake.Colour.purple())
    return embed
  
  @client.event
  async def on_member_join(member):
    guild = member.guild
    role = guild.get_role(1069387522771255296)
    await member.add_roles(role)
  
    last_user_id = None
    last_message_content = None
  
  
  @client.slash_command(name="list", descripiton="Список игроков на сервере")
  async def list(ctx):
    await partser.list(ctx)
  
  
  @has_permissions(administrator=True)
  @client.slash_command(name="send_embed", description="Отправить embed")
  async def send_embed(ctx, title, description, color, channel: disnake.TextChannel = None, header=None, poluchatel: disnake.Member = None):
    await partmoder.send_embed(ctx, title, description, color, channel, header, poluchatel)
  
  
  @client.event
  async def on_message(message: disnake.Message):
    if message.author.bot:
      return
    else:
      """
      if message.channel.id == 1134033445123801179:
        nickname = message.content
        await partmoder.add_to_whitelist(client, message, nickname)
        time.sleep(4)
        await message.channel.purge(limit=2)
      """
    if "<@1097890571403677889>" in message.content:
      await message.channel.send("Всегда к вашим услугам, сэр!")
      if "Какие у тебя функции" in message.content:
        await help()
      elif "Что ты можешь" in message.content:
        await help()
      else:
        pass
    global last_user_id, last_message_content, last_username
    if message.guild is None and not message.author.bot:
      if message.content.startswith("!"):
        return
      elif message.author.name == "p78_":
        return
      else:
        print(f"[{timme}] {message.author} пишет вам: {message.content}")
        unknkrio = await client.fetch_user(810914294437773352)
        user = message.author
        kreyze = await client.fetch_user(503112478847401994)
        perryntony = await client.fetch_user(660534347429969931)
        bismarckk_ = await client.fetch_user(1078247578036088883)
        embed = disnake.Embed(
          title='Вам пришло сообщение',
          color=disnake.Colour.blue(),
          description=
          f'{message.author} пишет вам: {message.content}\n\n!reply <ответ>')
        embed.set_author(name=f'{timme}')
        for moderator in partmoder.get_moders():
          if partmoder.name != partmoder.name:
            moderator.send(embed=embed)
        last_user_id = message.author.id
        last_message_content = message.content
        last_username = message.author.name
    await client.process_commands(message)
    if message.author.bot or message.guild is None:
      return
    # Check if the user is in the database
    guild_name = message.guild.name
    
    guild_name_low = guild_name.lower()
    db_name = f'{guild_name_low}_users.db'
    
    conn = sqlite3.connect(db_name)
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
               (user_id INTEGER PRIMARY KEY, username TEXT, xp INTEGER, level INTEGER)'''
            )
    c.execute("SELECT * FROM users WHERE user_id=?", (message.author.id, ))
    user = c.fetchone()
    num_of_words_in_message = len(message.content.split())
    if num_of_words_in_message == 1:
      xp_earned = 1
    elif num_of_words_in_message == 2 or num_of_words_in_message == 3 or num_of_words_in_message == 4:
      xp_earned = 2
    elif num_of_words_in_message >= 5 and num_of_words_in_message < 10:
      xp_earned = 5
    elif num_of_words_in_message >= 10:
      xp_earned = 10
    else:
      xp_earned = 1
    # If the user is not in the database, add them with 0 xp and level 1
    if user is None:
      c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                (message.author.id, str(message.author), 0, 1))
      conn.commit()
      user = (message.author.id, str(message.author), 0, 1)
    # Add xp to the user's total
    c.execute("UPDATE users SET xp=xp+? WHERE user_id=?",
              (xp_earned, message.author.id))
    conn.commit()
    # Check if the user has earned enough xp to level up
    current_xp = user[2] + xp_earned
    xp_per_level = base_xp_per_level * (2**(user[3] - 1))
    if current_xp >= xp_per_level:
      # Increase the user's level and update the required xp for the next level
      new_level = user[3] + 1
      new_xp_required = xp_per_level * 1.5
      c.execute("UPDATE users SET xp=?, level=? WHERE user_id=?",
                (current_xp - xp_per_level, new_level, message.author.id))
      conn.commit()
      author = message.author
      # Check if the user has leveled up and send a message if they have
      await author.send(
        f'Поздравляю, {message.author.mention}! Ты достиг уровня  {new_level}!')
    await client.process_commands(message)
  
  @client.command()
  async def reply(ctx, *, message=None):
    global last_user_id, last_message_content, last_username
    if (ctx.author.name == 'unknkriod') or (ctx.author.name
                                            == 'kreyze') or (ctx.author.name
                                                             == 'n3wer_') or (ctx.author.name == '_fas_5678') or (ctx.author.name == 'andrew69'):
      if message is not None and last_user_id is not None and last_message_content is not None:
        user = client.get_user(last_user_id)
        if ctx.guild is None and not ctx.author.bot:
          embed = main.myotvetembed(message=message, last_username=last_username)
          await partmoder.send_embed_to_adm(embed=embed)
          embedw = disnake.Embed(title='Вам пришло сообщение',
                                 color=disnake.Colour.purple(),
                                 description=f'{message}')
          embed.set_author(name=f'{timme}')
          await user.send(embed=embedw)
          print(f"{ctx.message.author} отвечает {last_username}: {message}")
          last_username = None
          last_message_content = None
          last_username = None
        else:
          await ctx.send('Эта комманда используется только в ЛС')
      else:
        await ctx.send(
          'Поле "message" пусто или нет пользователя, который отправил сообщение последним'
        )
    else:
      await ctx.send('Вам не позволено использовать эту комманду')
  
  
  @has_permissions(administrator=True)
  @client.slash_command(name="spam", description="ТОЛЬКО ДЛЯ АДМИНИСТРАЦИИ!!! Спамит сообщение")
  async def spam(ctx, message: str, amount: int, channel: disnake.TextChannel):
    await partmoder.spam(ctx, message, amount, channel)
  
  
  @client.slash_command(name="rank", description="Показывает ваш уровень или уровень другого пользователя")
  async def rank(ctx, member: disnake.Member = None):
    await partser.rank(ctx, member)
  
  
  @client.event
  async def on_member_remove(member):
    # Delete the user's data from the database
    guild_name = member.guild.name
    
    guild_name_low = guild_name.lower()
    db_name = f'{guild_name_low}_users.db'
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE user_id=?", (member.id, ))
    conn.commit()
    await member.send("Ваш уровень был обнулён на сервере EaverMine")
  
  
  # Rest of your code...
  
  
  @client.slash_command(name="leaderboard",
                        description="Таблица лидеров по уровню")
  async def leaderboard(ctx):
    await partser.leaderboard(ctx)
  
  
  @client.slash_command(name="help", description="Помощь")
  async def help(ctx, command=None):
    if (command == None):
      em = disnake.Embed(title="Помощь",
                         description="/help <command>",
                         color=disnake.Colour.yellow())
      em.add_field(name="Модерация", value="ban, unban, kick, mute")
      em.add_field(name="Сообщения", value="clear, dm, email")
      em.add_field(name="Fun", value="say, rank, list")
      await ctx.send(embed=em)
    elif (command == "ban"):
      em = disnake.Embed(title="Бан",
                         description="Банит пользователя",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}ban <пользователь> <причина>")
      await ctx.send(embed=em)
    elif (command == "unban"):
      em = disnake.Embed(title="Разбан",
                         description="Разбанивает пользователя",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}unban <пользователь> <причина>")
      await ctx.send(embed=em)
    elif (command == "kick"):
      em = disnake.Embed(title="Выгнать",
                         description="Выгоняет пользователя",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}kick <пользователь> <причина>")
      await ctx.send(embed=em)
    elif (command == "mute"):
      em = disnake.Embed(title="Мут",
                         description="Заглушает пользователя",
                         color=disnake.Colour.yellow())
      em.add_field(
        name="Использование",
        value=
        f"{slash_prefix}mute <пользователь> <время(Ns, Nm, Nh, Nd, Nw, Nmo, Ny) <причина>"
      )
      await ctx.send(embed=em)
    elif (command == "clear"):
      em = disnake.Embed(title="Очистить",
                         description="Удаляет указанное кол-во сообщений",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}clear <кол-во сообщений>")
      await ctx.send(embed=em)
    elif (command == "dm"):
      em = disnake.Embed(
        title="Личное сообщение",
        description=
        "Отправляет указанному пользователю личное сообщение от имени бота",
        color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}dm <пользователь> <сообщение>")
      await ctx.send(embed=em)
    elif (command == "email"):
      em = disnake.Embed(title="Email",
                         description="Отправляет письмо на указанный email",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}email <получатель> <тема> <текст>")
      await ctx.send(embed=em)
    elif (command == "say"):
      em = disnake.Embed(title="Отправить сообщение в канал",
                         description="Отправляет сообщение в указанный канал",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}say #название-канала <сообщение>")
      await ctx.send(embed=em)
  
    elif (command == "minecraft"):
      em = disnake.Embed(title="Выполнить команду в майнкрафте",
                         description="ДОСТУПНО ТОЛЬКО ДЛЯ АДМИНИСТРАЦИИ",
                         color=disnake.Colour.yellow())
      em.add_field(name="Использование",
                   value=f"{slash_prefix}minecraft <команда без />")
      em.add_field(name="Например",
                   value=f"{slash_prefix}minecraft say какие-то слова")
      await ctx.send(embed=em)
    else:
      await ctx.send("Такой комманды не существует")
  
  #
  @has_permissions(administrator=True)
  @client.slash_command(name="say", description="Отправляет сообщение в канал")
  async def say(ctx, channel: disnake.TextChannel, *, message):
    await partmoder.say(ctx=ctx, channel=channel, message=message)
    #
  @client.slash_command(name="clear", description="Очистить сообщения")
  @has_permissions(manage_messages=True)
  async def clear(ctx, limit: int):
    await partmoder.clear(ctx, limit)
  #
  @client.slash_command(name="kick", description="Кикает пользователя")
  @has_permissions(kick_members=True)
  async def kick(ctx, member: disnake.Member, *, reason='Нарушение правил сервера'):
    await partmoder.kick(ctx, member, reason)
  #
  @client.slash_command(name="ban", description="Забанить пользователя")
  @has_permissions(ban_members=True)
  async def ban(ctx, member: disnake.Member, *, reason="Нарушение правил сервера"):
    await partmoder.ban(ctx, member, reason)
  #
  @client.slash_command(name="mute", description="Мут")
  @has_permissions(administrator=True)
  async def mute(ctx, user: disnake.Member, time: str, reason="Нарушение правил сервера"):
    await partmoder.mute(slash_prefix=slash_prefix, ctx=ctx,user=user, time=time, reason=reason)
  
  @client.slash_command(name='anekdot', description='Выдаëт случайный анекдот')
  async def anekdot(ctx):
    await partser.anekdot(ctx)
  
  @client.slash_command(name="rps", description="Камень-ножницы-бумага")
  async def rps(ctx, my_choice):
    await partser.rps(ctx, my_choice)

def exittt():
  print("=========")
  print("  Выход  ")
  print("=========")
  sys.exit(0)

stop_bot_flag = False

async def check_stop_flag():
    global stop_bot_flag
    while not stop_bot_flag:
        await asyncio.sleep(5)  # Проверяем флаг каждые 5 секунд
    print("Stopping the bot...")
    await client.logout()

def start():
  while True:
    try:
      try:
        client.run(token=token, reconnect=True)
      except KeyboardInterrupt:
        exittt()
    except Exception as e:
      print(f"Произошла ошибка {e}")
      if "Event loop is closed" in str(e):
        exittt()
      print("Перезапуск...")
      continue
    except KeyboardInterrupt:
      exittt()


keep_alive()
#start()
