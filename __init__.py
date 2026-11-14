"""Datacircle for Hermes: four tools on Datacircle's open API (https://api.datacircle.dev/v1), no key."""

from . import schemas, tools


def register(ctx):
    for schema, handler in ((schemas.LIST_APIS, tools.list_apis), (schemas.BEST_PLANS, tools.best_plans),
                            (schemas.SEARCH_PLANS, tools.search_plans), (schemas.PROVIDER, tools.provider)):
        ctx.register_tool(name=schema["name"], toolset="datacircle", schema=schema, handler=handler)
