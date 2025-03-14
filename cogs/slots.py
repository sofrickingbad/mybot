import bisect
import os
import random
from PIL import Image
import discord
from discord.ext import commands
from modules.economy import Economy
from modules.helpers import *

class InsufficientFundsException(Exception):
  def __init__(self, current_balance, bet):
    self.current_balance = current_balance
    self.bet = bet
    super().__init__(f"Insufficient funds: {current_balance} < {bet}")

class Economy:
  def get_entry(self, user_id):
    # Placeholder for getting user entry
    return [user_id, "username", 1000]

  def add_credits(self, user_id, amount):
    # Placeholder for adding credits to user
    pass

class SlotMachine:
  def __init__(self, reelNum, winDict):
    self.reels = [[i for i in range(10)]] * reelNum
    self.wins = winDict

  def spin(self):
    spinResult = ''
    for reel in self.reels:
      spinResult += str(random.choice(reel))
    return spinResult

class Slots(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.economy = Economy()
    self.slot_machine = SlotMachine(3, {"777": 300, "888": 300, "999": 300})

  @commands.command()
  async def spin(self, ctx, bet: int):
    user_id = ctx.author.id
    entry = self.economy.get_entry(user_id)
    if entry[2] < bet:
      raise InsufficientFundsException(entry[2], bet)

    path = 'modules/'
    facade = Image.open(f'{path}slot-face.png').convert('RGBA')
    reel_images = [
      Image.open(f'{path}horseshoe.png').convert('RGBA'),
      Image.open(f'{path}seven.png').convert('RGBA'),
      Image.open(f'{path}watermelon.png').convert('RGBA'),
      Image.open(f'{path}lemon.png').convert('RGBA'),
      Image.open(f'{path}heart.png').convert('RGBA'),
      Image.open(f'{path}diamond.png').convert('RGBA'),
      Image.open(f'{path}cherry.png').convert('RGBA'),
      Image.open(f'{path}bell.png').convert('RGBA'),
      Image.open(f'{path}bar.png').convert('RGBA')
    ]

    rw, rh = reel.size
    item = 180
    items = rh // item

    s1 = random.randint(1, items - 1)
    s2 = random.randint(1, items - 1)
    s3 = random.randint(1, items - 1)

    win_rate = 98 / 100

    if random.random() < win_rate:
      symbols_weights = [3.5, 7, 15, 25, 55]
      x = round(random.random() * 100, 1)
      pos = bisect.bisect(symbols_weights, x)
      s1 = pos + (random.randint(1, (items // 6) - 1) * 6)
      s2 = pos + (random.randint(1, (items // 6) - 1) * 6)
      s3 = pos + (random.randint(1, (items // 6) - 1) * 6)
      s1 = s1 - 6 if s1 == items else s1
      s2 = s2 - 6 if s2 == items else s2
      s3 = s3 - 6 if s3 == items else s3

    images = []
    speed = 6
    for i in range(1, (item // speed) + 1):
      bg = Image.new('RGBA', facade.size, color=(255, 255, 255))
      bg.paste(reel, (25 + rw * 0, 100 - (speed * i * s1)))
      bg.paste(reel, (25 + rw * 1, 100 - (speed * i * s2)))
      bg.paste(reel, (25 + rw * 2, 100 - (speed * i * s3)))
      bg.alpha_composite(facade)
      images.append(bg)

    fp = str(id(ctx.author.id)) + '.gif'
    images[0].save(
      fp,
      save_all=True,
      append_images=images[1:],
      duration=50
    )

    result = ('lost', bet)
    self.economy.add_credits(ctx.author.id, bet * -1)
    spin_result = self.slot_machine.spin()
    if spin_result in self.slot_machine.wins:
      reward = self.slot_machine.wins[spin_result] * bet
      result = ('won', reward)
      self.economy.add_credits(ctx.author.id, reward)

    embed = discord.Embed(
      title=(
        f'You {result[0]} {result[1]} credits' +
        ('.' if result[0] == 'lost' else '!')
      ),
      description=(
        'You now have ' +
        f'**{self.economy.get_entry(ctx.author.id)[2]}** ' +
        'credits.'
      ),
      color=(
        discord.Color.red() if result[0] == "lost"
        else discord.Color.green()
      )
    )

    file = discord.File(fp, filename=fp)
    embed.set_image(url=f"attachment://{fp}")
    await ctx.send(
      file=file,
      embed=embed
    )

    os.remove(fp)

async def setup(client: commands.Bot):
    await client.add_cog(Slots(client))
