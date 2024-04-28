from pyrogram import Client, filters
from .config import api_id, api_hash, bot_token,workers,sleep_threshold
import pyromod.listen
from os import getcwd

bot = Client('bot', api_id, api_hash, bot_token=bot_token, workers=workers, sleep_threshold=sleep_threshold)

@bot.on_message(filters.command('start'))
async def send_welcome(client, message):
    await message.reply_text('Howdy, how are you doing?')

@bot.on_message(filters.text)
async def echo_all(client, message):
    await message.reply_text(message.text)

multi_clients = {}
work_loads = {}
