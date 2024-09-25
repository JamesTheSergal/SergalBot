import typing
import hikari
import crescent
import logging
import pprint

plugin = crescent.Plugin[hikari.GatewayBot, None]()
utils_group = crescent.Group("utils")

# Standardized imports per module #
from main import settings
import core.sergalcommon as sergal
import configparser
# ------------------------------- #

@plugin.include
@utils_group.child
@crescent.command(
    description="Ping the bot to see if its up!"
)
async def ping(ctx: crescent.Context):
    await ctx.respond("Pong!")


@plugin.load_hook
def on_load():
    print("Util plugin loaded...")
    logging.info(f'Plugins available -> \n{pprint.pformat(plugin.client.plugins.plugins)}')

@plugin.unload_hook
def on_unload():
    print("Unloaded Util plugin...")