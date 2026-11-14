"""The tools' handlers: each makes one HTTPS GET to Datacircle's open API and gives its answer as JSON."""

import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.datacircle.dev/v1"
AGENT = "hermes-datacircle/0.1.0"

# A plan holds about 90 keys (its terms of use, its aggregators...): the model gets the ones that choose a plan, the rest is on its page.
PLAN_KEYS = ["api", "rank", "provider", "plan", "score", "perThousand", "notFoundPerThousand", "billing", "pay",
             "currency", "units", "unit", "strengths", "latencyMs", "page", "pricingPage", "docs"]


class ApiError(Exception):
    pass


def _brief(item, keys=PLAN_KEYS):
    return {key: item[key] for key in keys if item.get(key) is not None}


def _int(value, low, high):
    """A number the model sent, as an int within the API's range, or None when it sent none."""
    if value is None or value == "":
        return None
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return None


def _slug(value):
    """The API's rule for a slug: the name in lowercase letters and digits, the rest a hyphen."""
    plain = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    plain = "".join(char for char in plain if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")


def _get(path, params=None):
    query = urllib.parse.urlencode({key: value for key, value in (params or {}).items() if value not in (None, "")})
    url = f"{BASE}{path}{'?' + query if query else ''}"
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": AGENT})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=30) as answer:
                return json.loads(answer.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", "replace")
            if error.code == 429 and attempt == 0:
                try:
                    wait = int(error.headers.get("Retry-After") or 30)
                except ValueError:
                    wait = 30
                time.sleep(min(max(wait, 1), 60))
                continue
            words = body
            try:
                parsed = json.loads(body)
                words = f"{parsed['error']}; the slugs: {', '.join(parsed['slugs'])}" if parsed.get("slugs") else parsed.get("error", body)
            except (ValueError, KeyError, TypeError, AttributeError):
                pass
            raise ApiError(f"Datacircle's API answered {error.code}: {str(words)[:3000]}") from None
    raise ApiError("Datacircle's API answered 429 twice: wait a minute and call again")


def _answer(work):
    """Runs one call: its answer as a JSON string, or the error as one, never an exception."""
    try:
        return json.dumps(work(), ensure_ascii=False)
    except ApiError as error:
        return json.dumps({"error": str(error)}, ensure_ascii=False)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        return json.dumps({"error": f"Datacircle's API could not be reached: {error}"}, ensure_ascii=False)


def list_apis(args, **kwargs):
    def work():
        apis = _get("/apis")
        words = [word for word in str(args.get("query") or "").lower().replace("-", " ").split() if word]
        held = []
        for index, api in enumerate(apis):
            name = f"{api.get('api', '')} {str(api.get('slug', '')).replace('-', ' ')}".lower()
            matched = sum(word in name for word in words)
            if matched or not words:
                held.append((-matched, index, api))
        found = [_brief(api, ["api", "slug", "plans", "providers", "best", "bestPage", "sheetPage"]) for _, _, api in sorted(held, key=lambda h: h[:2])]
        return {"total": len(found), "apis": found[:_int(args.get("limit"), 1, 200) or 20]}
    return _answer(work)


def best_plans(args, **kwargs):
    def work():
        slug = _slug(args.get("slug"))
        if not slug:
            raise ApiError("Give an API's slug, like 'email-finder': datacircle_list_apis gives every slug")
        answer = _get(f"/apis/{urllib.parse.quote(slug)}/best", {"limit": _int(args.get("limit"), 1, 50)})
        return {**answer, "plans": [_brief(plan) for plan in answer.get("plans") or []]}
    return _answer(work)


def search_plans(args, **kwargs):
    def work():
        sort = args.get("sort") if args.get("sort") in ("score", "provider", "price") else None
        answer = _get("/plans", {"api": args.get("api"), "query": args.get("query"), "sort": sort,
                                 "limit": _int(args.get("limit"), 1, 50), "offset": _int(args.get("offset"), 0, 10**6)})
        return {**answer, "plans": [_brief(plan) for plan in answer.get("plans") or []]}
    return _answer(work)


def _best(plans):
    """A provider's best plan on an API: its lowest rank, a plan with no score having none."""
    ranked = sorted(plans, key=lambda plan: plan.get("rank") if isinstance(plan.get("rank"), (int, float)) else float("inf"))
    return _brief(ranked[0], ["plan", "score", "perThousand", "page"]) if ranked else None


def provider(args, **kwargs):
    def work():
        slug = _slug(args.get("slug"))
        if not slug:
            raise ApiError("Give a provider's slug or name, like 'bright-data' or 'Bright Data'")
        answer = _get(f"/providers/{urllib.parse.quote(slug)}")
        apis = [{**_brief(entry, ["api", "slug", "rank", "bestPage"]), "plans": len(entry.get("plans") or []),
                 "best": _best(entry.get("plans") or [])} for entry in answer.get("apis") or []]
        return {**answer, "apis": apis}
    return _answer(work)
