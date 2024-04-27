import asyncio
import logging
from .config import sleep_threshold,bot_token,api_hash,api_id
from pyrogram import Client
from .utils.config_parser import TokenParser
from botCode.py import multi_clients, work_loads, bot


async def initialize_clients():
    multi_clients[0] = bot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return
    
    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=":memory:",
                api_id=api_id,
                api_hash=api_hash,
                bot_token=token,
                sleep_threshold=sleep_threshold,
                no_updates=True,
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        Var.MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
