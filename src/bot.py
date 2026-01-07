import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import os
import sys

# Add the current directory to sys.path to allow absolute imports
sys.path.insert(0, os.path.dirname(__file__))

from database import Database

# Cargar configuración
config_path = os.path.join(os.path.dirname(__file__), '../config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
db = Database(config['database'])

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    await db.init_db()
    # Sincronizar comandos slash
    await bot.tree.sync()
    print('Comandos slash sincronizados.')

# Cargar cogs
async def load_cogs():
    await bot.load_extension('cogs.moderation')
    await bot.load_extension('cogs.security')
    await bot.load_extension('cogs.config')
    await bot.load_extension('cogs.help')

async def main():
    await load_cogs()
    await bot.start(config['token'])

if __name__ == '__main__':
    asyncio.run(main())
