class unknbotenv:
  import datetime
  import disnake
  from disnake.ext import commands
  intents = disnake.Intents.default()
  intents.members = True
  intents.message_content = True
  tz = datetime.timezone(datetime.timedelta(hours=3))
  dt_obj = datetime.datetime.now(tz)
  timme = dt_obj.strftime("%d.%m.%Y")
  
  token = "-"
  client = commands.Bot(command_prefix='!', intents=intents)
  slash_prefix = "/"
