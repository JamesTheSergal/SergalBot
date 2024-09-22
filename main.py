import logging
import os
import hikari
import crescent
from openai import OpenAI
from core import sergalcommon as sergbot

if not os.path.exists("secrets"):
        print("Please set your token and mysql password.")
        os.makedirs("secrets")
        exit()

with open("secrets/token") as tokenfile:
        token = tokenfile.read().strip()

# Begin to connect and setup redis
with open("secrets/mysql") as addressfile:
        address = addressfile.read().strip()

with open("secrets/mysql-pass") as passfile:
        mysql_pass = passfile.read().strip()

with open("secrets/mysql-user") as passfile:
        mysql_user = passfile.read().strip()


logging.basicConfig(
    encoding="utf-8",
    format="{asctime}.{msecs} - [{module}.{funcName}:({lineno})] - [{levelname}] - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("SergalBot.log", mode='a'),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
        bot = hikari.GatewayBot(token, logs="DEBUG", intents=hikari.Intents.ALL)
        client = crescent.Client(bot, update_commands=True)
        client.plugins.load_folder("plugins")
        bot.run()