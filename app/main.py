import asyncio
import pathlib
import logging

import aiohttp_jinja2
import jinja2
from aiohttp import web

from .telegram import CustomClient 
from .routes import setup_routes
from .views import Views
from .config import host, port, api_id, api_hash, debug,bot_token,sleep_threshold,workers


log = logging.getLogger(__name__)


class Indexer:

    TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'templates'

    def __init__(self):
        self.server = web.Application()
        self.loop = asyncio.get_event_loop()
        self.tg_client = CustomClient('bot', api_id, api_hash, bot_token=bot_token, workers=workers,sleep_threshold=sleep_threshold)


    async def startup(self):
        await self.tg_client.start()
        log.debug("telegram client started!")

        await setup_routes(self.server, Views(self.tg_client))

        loader = jinja2.FileSystemLoader(str(self.TEMPLATES_ROOT))
        aiohttp_jinja2.setup(self.server, loader=loader)

        self.server.on_cleanup.append(self.cleanup)


    async def cleanup(self, *args):
        await self.tg_client.disconnect()
        log.debug("telegram client disconnected!")


    def run(self):
        self.loop.run_until_complete(self.startup())
        web.run_app(self.server, host=host, port=port)
