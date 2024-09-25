import logging
import os
import hikari
import crescent
from openai import OpenAI
from core import sergalcommon as sergbot
from core.sergalcommon import checkSettings

settings = checkSettings()

logging.basicConfig(
    encoding="utf-8",
    format="{asctime}.{msecs} - [{module}.{funcName}:({lineno})] - [{levelname}] - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=settings.getint("application", "loglevel"),
    handlers=[
        logging.FileHandler(
                        filename = f'{settings.get("application", "logname")}.log',
                        mode='a'
                ),
        logging.StreamHandler()
    ]
)

if settings.getboolean("application", 'startup-update') == True:
        sergbot.SergalBot(settings=settings)

if __name__ == '__main__':
        bot = hikari.GatewayBot(
                token=settings.get("discord", "api-key"),
                logs=settings.getint("discord", "hikari-loglevel"), 
                intents=hikari.Intents.ALL
        )
        client = crescent.Client(
                app=bot,
                update_commands=True
        )
        client.plugins.load_folder("plugins")
        bot.run()