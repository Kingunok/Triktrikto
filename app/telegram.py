import math
import logging
import asyncio
from ..vars import Var
from pyrogram import Client
from utils.config_parser import TokenParser
from botCode import multi_clients, work_loads, StreamBot

class CustomClient(Client):
    async def initialize_clients(self):
        multi_clients[0] = StreamBot
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
                    api_id=Var.API_ID,
                    api_hash=Var.API_HASH,
                    bot_token=token,
                    sleep_threshold=Var.SLEEP_THRESHOLD,
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

    async def download(self, file, file_size, offset, limit):
        part_size = 512 * 1024
        first_part_cut = offset % part_size
        first_part = math.floor(offset / part_size)
        last_part_cut = part_size - (limit % part_size)
        last_part = math.ceil(limit / part_size)
        part_count = math.ceil(file_size / part_size)
        part = first_part
        try:
            while True:
                chunk = await self.download_media(
                    file,
                    offset=first_part * part_size,
                    file_size=part_size,
                    part_size=part_size,
                    progress=None
                )
                if part == first_part:
                    yield chunk[first_part_cut:]
                elif part == last_part:
                    yield chunk[:last_part_cut]
                else:
                    yield chunk
                self.log.debug(f"Part {part}/{last_part} (total {part_count}) served!")
                part += 1
        except FloodWait as e:
            self.log.warning(f"Flood wait: {e}")
            await asyncio.sleep(e.x)
        except Exception as e:
            self.log.error(f"An error occurred: {e}", exc_info=True)
