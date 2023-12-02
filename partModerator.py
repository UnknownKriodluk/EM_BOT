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
from rcon.source import Client
import re

def myotvetembed(message, last_username):
    embed = disnake.Embed(title=f"Я => {last_username}",
                          description=f'{message}',
                          color=disnake.Colour.purple())
    return embed

class Admin:
  async def __init__(self, client):
    self.moderator_role = disnake.utils.get(client.guilds[0].roles, name="Модератор")
    self.moderators = self.moderator_role.members
    for self.moderator in self.moderators:
      return self.moderator

  
  def get_moders(self):
    return self.moderators

  
  async def send_embed_to_adm(self, embed):
    moderator = self.moderator
    moderators = self.moderators
    try:
      for moderator in moderators:
        await moderator.send(embed=embed)
        print(f"Embed отправлен {moderator.name}")
    except Exception as e:
      print(f'Не удалось отправить embed {moderator.name}: {e}')
  
  async def send_msg_to_adm(self, message):
    moderator = self.moderator
    moderators = self.moderators
    try:
      for moderator in moderators:
        await moderator.send(message)
        print(f"Embed отправлен {moderator.name}")
    except Exception as e:
      print(f'Не удалось отправить embed {moderator.name}: {e}')

  
  async def add_to_whitelist(client, ctx, nickname):
    with Client('138.201.142.120', 25900, passwd='A9DF9542623629A120') as mcr:
      command = f'whitelist add {nickname}'
      response = mcr.run(command)
      admchannel = client.get_channel(1069585321475444797)
      channel = client.get_channel(1134033445123801179)
      if "Added" or "Добавлен" or "добавлен" or "added" in response:
        embed = disnake.Embed(title=f"{nickname} был добавлен в whitelist",
                              color=disnake.Colour.green())
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await channel.send(embed=embed)
        await admchannel.send(embed=embed)
      else:
        embed = disnake.Embed(title="Ответ сервера:",
                              description=response,
                              color=disnake.Colour.yellow())
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await channel.send(embed=embed)
        await admchannel.send(embed=embed)

  
  async def mute(slash_prefix, ctx, user, time, reason):
    number_match = re.findall("\d+", time)
    letter_match = re.findall("[a-zA-Z]+", time)
    if (number_match and not letter_match) or (letter_match and not number_match):
      embed = disnake.Embed(
        title="Использование /mute:",
        description=f"{slash_prefix}mute <пользователь> <время (Ns, Nm, Nh, Nd, Nw, Nmo, Ny)> <причина>",
        color=disnake.Colour.yellow()
      )
      await ctx.send(embed=embed)
    else:
      number = int(re.findall("\d+", time)[0])
      letter = re.findall("[a-zA-Z]+", time)[0]
      minutes = number * 60
      if letter == "s":
        minutes /= 60
      elif letter == "m":
        minutes = minutes
      elif letter == "h":
        minutes *= 60
      elif letter == "d":
        minutes = minutes * 60 * 24
      elif letter == "w":
        minutes = minutes * 60 * 24 * 7
      elif letter == "mo":
        minutes = minutes * 60 * 24 * 31
      elif letter == "y":
        minutes = minutes * 60 * 24 * 365
      else:
        embed = disnake.Embed(
          title="Использование /mute:",
          description=
          f"{slash_prefix}mute <пользователь> <время (Ns, Nm, Nh, Nd, Nw, Nmo, Ny)> <причина>",
          color=disnake.Colour.yellow())
        await ctx.send(embed=embed)
    
      await user.timeout(until=disnake.utils.utcnow() +
                         datetime.timedelta(seconds=minutes),
                         reason=reason)
      if letter == "s":
        mmminutes = f"{number} секунд(у)"
      elif letter == "m":
        mmminutes = f"{number} минут(у)"
      elif letter == "h":
        mmminutes = f"{number} час(ов)"
      elif letter == "d":
        mmminutes = f"{number} день(дней)"
      elif letter == "w":
        mmminutes = f"{number} недель(ю)"
      elif letter == "mo":
        mmminutes = f"{number} месяц(ей)"
      elif letter == "y":
        mmminutes = f"{number} лет"
      embedy = disnake.Embed(
        title=f"Пользователь {user.name} заглушён на {mmminutes}",
        description=f"По причине: {reason}",
        color=disnake.Colour.yellow())
    
      embedy.set_author(name='Заглушить пользователя')
      await ctx.send(embed=embedy)
      await user.send(f"Вы были заглушены по причине: {reason}")

  
  async def send_embed(ctx, title, description, color, channel, header, poluchatel):
    if (color == "blue"):
      colo = disnake.Colour.blue()
    elif (color == "red"):
      colo = disnake.Colour.red()
    elif (color == "yellow"):
      colo = disnake.Colour.yellow()
    elif (color == "green"):
      colo = disnake.Colour.green()
    elif (color == "purple"):
      colo = disnake.Colour.purple()
    else:
      colo = disnake.Colour.purple()
  
    embed = disnake.Embed(title=title, color=colo, description=description)
    if (header != None):
      embed.set_author(name=header)
  
    embed.set_thumbnail(url=ctx.guild.icon.url)
    try:
      if (channel != None):
        await channel.send(embed=embed)
      elif (poluchatel != None):
        await poluchatel.send(embed=embed)
        embedotv = myotvetembed(message=message, last_username=poluchatel)
        await Admin.send_embed_to_adm(embed=embedotv)
      elif (poluchatel != None) and (channel != None):
        await ctx.send("Указывать канал и получателя в одной комманде нельзя!")
      elif (poluchatel == None) and (channel == None):
        await ctx.send("Укажите получателя ИЛИ канал!")
      else:
        await ctx.send("Неправильно указан получатель")
    except Exception as e:
      await ctx.send(f"Произошла ошибка при выполнении комманды: {e}")
  
  
  async def spam(ctx, message: str, amount: int, channel):
    for i in range(amount):
      await channel.send(message)

  
  async def say(ctx, channel, message):
    await channel.send(message)

  
  async def clear(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    print(f'Команда "очистить" была использована {ctx.author.name}')


  async def kick(ctx, member: disnake.Member, reason='Нарушение правил сервера'):
    try:
      await member.send(f"Вы были кикнуты с сервера EaverMine по причине: {reason}")
      await member.kick(reason=reason)
      print(f'Команда kick была использована {member}')
      embedyes = disnake.Embed(
        title='Успешно',
        color=disnake.Colour.green(),
        description=f'{member} был кикнут по причине: {reason}')
      embedyes.set_author(name='Кик')
      await ctx.send(embed=embedyes)
    except:
      embedn = disnake.Embed(title='Неуспешно',
                             color=disnake.Colour.red(),
                             description=f'Не удалось кикнуть {member}')
      embedn.set_author(name='Кик')
      await ctx.send(embed=embedn)


  async def ban(ctx, member: disnake.Member, reason = "Нарушение правил сервера"):
    await member.send(f"Вы были забанены на сервере EaverMine по причине: {reason}")
    await member.ban(reason=reason)
    await ctx.send(f'{ member.mention } был забанен по причине: {reason}')
    print(f'{ member.mention } был забанен пользователем {ctx.author.name}')
