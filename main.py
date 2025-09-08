from typing import Optional
import asyncio
import re

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Pokémon Gateway")

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon/"


def json_resp(content: dict, status_code: int = 200):
    return JSONResponse(content=content, status_code=status_code)


@app.get("/health")
async def health():
    return json_resp({"status": "ok"}, status_code=200)


@app.get("/pokemon-info")
async def pokemon_info(name: Optional[str] = Query(None, description="Pokemon name (case-sensitive, lowercase only)")):
    if not name or not name.strip():
        return json_resp({"error": "missing 'name' query parameter"}, status_code=400)

    raw_name = name.strip()

    # ✅ Rule: only lowercase letters, digits, hyphens allowed
    if not re.fullmatch(r"[a-z0-9\-]+", raw_name):
        return json_resp({"error": "Invalid Pokémon name"}, status_code=400)

    url = POKEAPI_BASE + raw_name

    max_retries = 3
    backoff_base = 0.5

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)

            if resp.status_code == 404:
                return json_resp({"error": "Pokemon not found"}, status_code=404)

            if resp.status_code == 200:
                data = resp.json()
                try:
                    result = {
                        "name": data.get("name"),
                        "type": (data.get("types") or [])[0]["type"]["name"]
                        if data.get("types") else None,
                        "height": data.get("height"),
                        "weight": data.get("weight"),
                        "first_ability": (data.get("abilities") or [])[0]["ability"]["name"]
                        if data.get("abilities") else None,
                    }
                except Exception:
                    return json_resp({"error": "upstream returned unexpected data"}, status_code=502)
                return json_resp(result, status_code=200)

            if 500 <= resp.status_code < 600:
                raise httpx.HTTPStatusError("Upstream 5xx", request=resp.request, response=resp)

            return json_resp({"error": "upstream error"}, status_code=502)

        except (httpx.RequestError, httpx.HTTPStatusError):
            if attempt == max_retries:
                return json_resp({"error": "upstream service unavailable"}, status_code=502)
            await asyncio.sleep(backoff_base * attempt)
