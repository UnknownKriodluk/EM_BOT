from ast import Try
from email import message
from email.base64mime import body_encode
import datetime
import os
import sys
import requests
import disnake
from disnake.ext.commands import has_permissions
from disnake.ext import commands
from disnake.ext import tasks
import asyncio
from asyncio import sleep
import sqlite3
import bs4
import lxml
import random
base_xp_per_level = 100
class partUser:
  def get_online_players():
    url = "https://api.mcsrvstat.us/2/138.201.142.120:25959"
  
    try:
      response = requests.get(url)
      data = response.json()
  
      if response.status_code == 200 and data['online']:
        if 'list' in data['players']:
          players = data['players']['list']
          player_count = len(players)
  
          if player_count == 1:
            return f"1 игрок онлайн: {players[0]}"
          elif player_count > 1:
            players_str = ', '.join(players)
            return f"{player_count} игроков онлайн: {players_str}"
  
        return "Сервер пуст"
  
    except Exception as e:
      print(f"Произошла ошибка: {e}")
  
      return e

  async def list(ctx):
    list = partUser.get_online_players()
    await ctx.send(list)
  
    list = None
  
  async def rank(ctx, member: disnake.Member = None):
    if member is None:
      member = ctx.author
  
    rank_guild_name = ctx.guild.name
    
    rank_guild_name_low = rank_guild_name.lower()
    rank_db_name = f'{rank_guild_name_low}_users.db'
    
    connrank = sqlite3.connect(rank_db_name)
  
    c = connrank.cursor()
  
    c.execute("SELECT * FROM users WHERE user_id=?", (member.id, ))
    user = c.fetchone()
  
    guild_namerps = ctx.guild.name
    
    guild_namerps_low = guild_namerps.lower()
    db_rps_name = f'{guild_namerps_low}_rps_stats.db'
    
    rps_statdb = sqlite3.connect(db_rps_name)
    rps_statsc = rps_statdb.cursor()
  
    rps_statsc.execute("SELECT * FROM rps_stats WHERE user_id=?", (member.id, ))
    rps_stats = rps_statsc.fetchone()
  
    if user is None:
      await ctx.send(f"{member.display_name} не заработал ещë опыта")
      return
  
    if not member.avatar:
      avatar_url = ""
    else:
      avatar_url = member.avatar.url
  
    current_xp = user[2]
    current_level = user[3]
    xp_required = base_xp_per_level * 2**(current_level - 1)
    percent_complete = current_xp / xp_required
    progress_bar_length = 16  # or any desired length
    filled_blocks = round(percent_complete * progress_bar_length)
    empty_blocks = progress_bar_length - filled_blocks
    filled_blocks_str = "█" * filled_blocks
    empty_blocks_str = "░" * empty_blocks
    progress_bar = f"[{filled_blocks_str}{empty_blocks_str}]"
    # Create an embed to display the user's level and xp
    embed = disnake.Embed(title=f"{member.display_name}'s Уровень",
                          color=0x3498db)
    embed.add_field(name="Уровень",
                    value=f"{current_level} {progress_bar}",
                    inline=False)
    embed.add_field(name="XP", value=f"{current_xp}/{xp_required}", inline=False)
    embed.add_field(name="Прогресс",
                    value=f"`{percent_complete*100:.2f}%`",
                    inline=False)
  
    roles_raw = sorted(member.roles, key=lambda r: r.position, reverse=True)
    roles = [role.name for role in roles_raw if role != ctx.guild.default_role]
    if roles:
      embed.add_field(name="Роли:", value=", ".join(roles))
  
    if rps_stats:
      embed.add_field(
        name="Статистика КНБ:",
        value=
        f"Победы: {rps_stats[1]}, Поражения: {rps_stats[2]}, Ничьи: {rps_stats[3]}"
      )
  
    embed.set_thumbnail(url=avatar_url)
    await ctx.response.defer()
    await ctx.send(embed=embed)

  async def leaderboard(ctx):
    # Fetch the leaderboard data from the database
    guild_name = ctx.guild.name
    
    guild_name_low = guild_name.lower()
    db_name = f'{guild_name_low}_users.db'
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    c.execute("SELECT * FROM users ORDER BY level DESC, xp DESC")
    leaderboard_data = c.fetchall()
  
    # Create an empty list to hold the leaderboard entries
    leaderboard_entries = []
  
    # Loop through the leaderboard data and add formatted entries to the list
    for i, (user_id, user_name, user_xp,
            user_level) in enumerate(leaderboard_data[:10]):
      try:
        member = await ctx.guild.fetch_member(user_id)
      except disnake.NotFound:
        member = None
  
      if member:
        leaderboard_entries.append(
          f"#{i+1}. **{member.display_name}**: Уровень {user_level} и {user_xp} XP"
        )
      else:
        leaderboard_entries.append(
          f"#{i+1}. **{user_name}**: Уровень {user_level} и {user_xp} XP")
  
    # Create the embed with the leaderboard entries
    embed = disnake.Embed(title="Таблица лидеров по уровню", color=0x00ff00)
    embed.description = "\n".join(leaderboard_entries)
    embed.set_thumbnail(url=ctx.guild.icon.url)
    # Send the embed as a response to the /leaderboard command
    await ctx.response.defer()
    await ctx.send(embed=embed)
  
  def anekdot_get():
    url = 'https://anekdot.ru/random/anekdot'
    h = {"User-Agent": "1"}  # сайт не пускает без header
    web = requests.get(
      url, headers=h
    ).text  # Получение кода веб-сайта, где расположены случайные анекдоты
  
    bs = bs4.BeautifulSoup(web, "lxml")
    result = str(bs.find_all(class_="topicbox")[1].find(
      class_="text"))  # получаем элемент, в котором написан текст анекдота
    text = result.replace(
      "<br/>", "\n"
    )  # удаляем лишние теги, которые попали в наш текст. заменяем тег переноса на \n
    text = text.split(">")
    text[0] = ""
    text = ''.join(text)
    text = text.split("<")
    text[-1] = ""
    text = ''.join(text)
    return text

  async def anekdot(ctx):
    embed = disnake.Embed(title='Анекдот',
                          description=partUser.anekdot_get(),
                          color=disnake.Colour.yellow())
    await ctx.response.defer()
    await ctx.send(embed=embed) 

  async def rps(ctx, my_choice):
    choicesrps = ["камень", "ножницы", "бумага"]
    bot_choice = random.choice(choicesrps)
  
    guild_namerps = ctx.guild.name
    
    guild_namerps_low = guild_namerps.lower()
    db_rps_name = f'{guild_namerps_low}_rps_stats.db'
    
    rps_statdb = sqlite3.connect(db_rps_name)
    rps_statsc = rps_statdb.cursor()
  
    rps_statsc.execute('''CREATE TABLE IF NOT EXISTS rps_stats (
    user_id INTEGER,
    wins INTEGER,
    losses INTEGER, 
    draws INTEGER
  )''')
    rps_statsc.execute("SELECT * FROM rps_stats WHERE user_id=?",
                       (ctx.author.id, ))
    resultt = rps_statsc.fetchone()
  
    if resultt is None:
      rps_statsc.execute(
        "INSERT INTO rps_stats (user_id, wins, losses, draws) VALUES (?, 0, 0, 0)",
        (ctx.author.id, ))
      rps_statdb.commit()
  
    result = partUser.check_win(my_choice, bot_choice)
    color = None
    if result == 0:
      text = "Ничья!"
      color = disnake.Colour.default()
      rps_statsc.execute("UPDATE rps_stats SET draws=draws+1 WHERE user_id=?",
                         (ctx.author.id, ))
    elif result == 1:
      text = "Ты выиграл!"
      color = disnake.Colour.green()
      rps_statsc.execute("UPDATE rps_stats SET wins=wins+1 WHERE user_id=?",
                         (ctx.author.id, ))
    else:
      text = "Ты проиграл!"
      color = disnake.Colour.red()
      rps_statsc.execute("UPDATE rps_stats SET losses=losses+1 WHERE user_id=?",
                         (ctx.author.id, ))
  
    embed = disnake.Embed(
      title=text,
      description=f"Твой выбор: {my_choice}\nМой выбор: {bot_choice}",
      color=color)
    await ctx.send(embed=embed)
    rps_statdb.commit()
  
  
  def check_win(p1, p2):
  
    if p1 == p2:
      return 0
  
    if p1 == "камень":
      if p2 == "ножницы":
        return 1
      elif p2 == "бумага":
        return 2
      else:
        return 1
  
    if p1 == "ножницы":
      if p2 == "бумага":
        return 1
      elif p2 == "камень":
        return 2
      else:
        return 1
  
    if p1 == "бумага":
      if p2 == "камень":
        return 1
      elif p2 == "ножницы":
        return 2
      else:
        return 1
