import typing
import hikari
import crescent
import logging
import pprint
import webcolors

plugin = crescent.Plugin[hikari.GatewayBot, None]()
roles_group = crescent.Group("roles")

# Standardized imports per module #
from main import settings
import core.sergalcommon as sergal
import configparser
# ------------------------------- #

async def role_color_autocomplete(ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption) -> list[hikari.CommandChoice]:
    return [
        hikari.CommandChoice(name="red", value="red"),
        hikari.CommandChoice(name="green", value="green"),
        hikari.CommandChoice(name="blue", value="blue"),
        hikari.CommandChoice(name="yellow", value="yellow"),
        hikari.CommandChoice(name="beige", value="beige"),
        hikari.CommandChoice(name="black", value="black"),
        hikari.CommandChoice(name="brown", value="brown"),
        hikari.CommandChoice(name="blueviolet", value="blueviolet"),
        hikari.CommandChoice(name="chartreuse", value="chartreuse"),
        hikari.CommandChoice(name="coral", value="coral"),
        hikari.CommandChoice(name="crimson", value="crimson"),
        hikari.CommandChoice(name="darkblue", value="darkblue"),
        hikari.CommandChoice(name="darkgreen", value="darkgreen"),
        hikari.CommandChoice(name="cyan", value="cyan"),
        hikari.CommandChoice(name="turquoise", value="turquoise"),

    ]


@plugin.include
@roles_group.child
@crescent.command(
    name="createrole",
    description="Creates a role",
    guild=916545175818473482
)
class CreateRole:
    rolename = crescent.option(str, description="Name for new role")
    rolecolor = crescent.option(str, description="Color for role (All HTML color names supported)", autocomplete=role_color_autocomplete, default=None)
    separate = crescent.option(bool, description="Display role seperately?", default=None)

    async def callback(self, ctx: crescent.Context):
        if self.rolecolor is not None:
            try:
                desired_color = webcolors.name_to_rgb(self.rolecolor)
            except ValueError:
                await ctx.respond("Sorry, there was a problem while processing the color you requested! (We might have not recognized it.)")
            role_color = hikari.Color.from_rgb(desired_color.red, desired_color.green, desired_color.blue)
        else:
            self.role_color = "white"

        await ctx.app.rest.create_role(ctx.guild_id, name=self.rolename, color=role_color)
        await ctx.respond("Created role...", ephemeral=True)