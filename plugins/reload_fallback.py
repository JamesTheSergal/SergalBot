import logging
import hikari 
import crescent
import pprint

plugin = crescent.Plugin[hikari.GatewayBot, None]()
fallback_group = crescent.Group("fallback")

# Standardized imports per module #
from main import settings
import core.sergalcommon as sergal
import configparser
# ------------------------------- #

@plugin.include
@fallback_group.child
@crescent.command(
    name="load",
    description="Command used by the owner to update the code on the fly."
)
class Load:
    load_target = crescent.option(str, "Plugin to load", name="plugin")

    async def callback(self, ctx: crescent.Context):
        if ctx.user.id == settings.getint("discord", "bot-owner-id"):
            print(f'Loading {self.load_target} ...')
            try:
                plugin.client.plugins.load(self.load_target)
            except ModuleNotFoundError:
                await ctx.respond(f'Plugin not found. Plugins available ->\n`{pprint.pformat(plugin.client.plugins.plugins)}`')
            await ctx.respond("Completed operation.")
        else:
            await ctx.respond("You are not the owner.", ephemeral=True)

@plugin.include
@fallback_group.child
@crescent.command(
    name="unload",
    description="Command used by the owner to update the code on the fly."
)
class Unload:
    unload_target = crescent.option(str, "Plugin to load", name="plugin")

    async def callback(self, ctx: crescent.Context):
        if ctx.user.id == settings.getint("discord", "bot-owner-id"):
            print(f'Unloading {self.unload_target} ...')
            try:
                plugin.client.plugins.unload(self.unload_target)
            except ModuleNotFoundError:
                await ctx.respond(f'Plugin not found. Plugins available ->\n`{pprint.pformat(plugin.client.plugins.plugins)}`')
            await ctx.respond("Completed operation.")
        else:
            await ctx.respond("You are not the owner.", ephemeral=True)

@plugin.include
@fallback_group.child
@crescent.command(
    name="reload",
    description="Command used by the owner to update the code on the fly."
)
class Reload:
    reload_target = crescent.option(str, "Plugin to load", name="plugin")

    async def callback(self, ctx: crescent.Context):
        if ctx.user.id == settings.getint("discord", "bot-owner-id"):
            print(f'Reloading {self.reload_target} ...')
            try:
                plugin.client.plugins.load(self.reload_target, refresh=True) #TODO: Handle KeyError when plugin failed to previously reload.
            except ModuleNotFoundError:
                await ctx.respond(f'Plugin not found. Plugins available ->\n`{pprint.pformat(plugin.client.plugins.plugins)}`')
            await ctx.respond("Completed operation.")
        else:
            await ctx.respond("You are not the owner.", ephemeral=True)

@plugin.include
@fallback_group.child
@crescent.command(
    name="command_purge",
    description="Command used by the owner to update the code on the fly."
)
class Purge:

    async def callback(self, ctx: crescent.Context):
        if ctx.user.id == settings.getint("discord", "bot-owner-id"):
            print(f'Purging commands...')
            await ctx.defer(ephemeral=True)
            await plugin.client.commands.purge_commands()
            await plugin.client.commands.register_commands()
            await ctx.respond("Commands purged...", ephemeral=True)
        else:
            await ctx.respond("You are not the owner.", ephemeral=True)


@plugin.load_hook
def on_load():
    logging.info("Fallback plugin loaded...")

@plugin.unload_hook
def on_unload():
    logging.info("Unloaded Fallback plugin...")