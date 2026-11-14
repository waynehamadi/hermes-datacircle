"""The tools' schemas: what the model reads to choose a tool and its arguments."""

LIST_APIS = {
    "name": "datacircle_list_apis",
    "description": (
        "Lists the GTM APIs on Datacircle's sheet (https://datacircle.dev), with each API's slug, "
        "how many plans and providers it has and its best plan. Call it first to find an API's slug."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Words of the API's name or slug, like 'email' or 'linkedin profile': the APIs that hold "
                    "the most of them come first. The sheet's order when left out."
                ),
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 200,
                "description": "How many APIs to give, 1 to 200. 20 when left out: the sheet has about 150.",
            },
        },
        "required": [],
    },
}

BEST_PLANS = {
    "name": "datacircle_best_plans",
    "description": (
        "Gives an API's plans best first by their score out of 100 on Datacircle's benchmark "
        "(https://datacircle.dev), each with its rank, provider, plan, $ per 1,000 calls and its page. "
        "perThousand is a plan's price of 1,000 items in dollars, pay the plan's whole price in its currency."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "slug": {
                "type": "string",
                "description": "The API's slug, like 'email-finder' or 'linkedin-profile', as datacircle_list_apis gives it.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "How many plans to give, 1 to 50. 10 when left out.",
            },
        },
        "required": ["slug"],
    },
}

SEARCH_PLANS = {
    "name": "datacircle_search_plans",
    "description": (
        "Searches every plan on Datacircle's sheet (https://datacircle.dev), or one API's, by provider or plan "
        "name, sorted by score, provider or price. Gives how many were found and up to limit of them. "
        "perThousand is a plan's price of 1,000 items in dollars, pay the plan's whole price in its currency."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "api": {
                "type": "string",
                "description": (
                    "Only this API's plans: its name or slug, like 'email-finder'. A provider's name goes in "
                    "query, never here. Every API when left out."
                ),
            },
            "query": {
                "type": "string",
                "description": "Words that must all appear in the provider's or plan's name, like 'bright data'.",
            },
            "sort": {
                "type": "string",
                "enum": ["score", "provider", "price"],
                "description": "score (best first, the default), provider (A to Z) or price ($ per 1,000, lowest first).",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "How many plans to give, 1 to 50. 10 when left out.",
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "description": "How many found plans to skip first. 0 when left out.",
            },
        },
        "required": [],
    },
}

PROVIDER = {
    "name": "datacircle_provider",
    "description": (
        "Gives each API one provider sells and its rank on each on Datacircle's benchmark "
        "(https://datacircle.dev), with its best plan there."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "slug": {
                "type": "string",
                "description": "The provider's slug, like 'bright-data', or its name, like 'Bright Data': the name is made a slug.",
            },
        },
        "required": ["slug"],
    },
}
