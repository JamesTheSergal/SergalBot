from datetime import datetime

import hikari
import crescent
from crescent.ext import tasks

plugin = crescent.Plugin[hikari.GatewayBot, None]()

@plugin.include
@tasks.loop(minutes=1)
async def loop() -> None:
    print(f'Ran at {datetime.now()}')
