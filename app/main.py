from typing import Optional
import asyncio

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI(title="Pokémon Gateway")

POKEAPI_BASE = "https://pokeapi.co/api/v2/pokemon/"

# Small helper to standardize JSON responses and ensure Content-Type
def json_resp(content: dict, status_code: int = 200):
    return JSONResponse(content=content, status_code=status_code)


@app.get("/health")
async def health():
    return json_resp({"status": "ok"}, status_code=200)


@app.get("/pokemon-info")
async def pokemon_info(name: Optional[str] = Query(None, description="Pokemon name (case-insensitive)")):
    # Validate input
    if not name or not name.strip():
        return json_resp({"error": "missing 'name' query parameter"}, status_code=400)

    pokemon_name = name.strip().lower()

    url = POKEAPI_BASE + httpx.URL(pokemon_name).raw_path.decode() if hasattr(httpx.URL(pokemon_name), 'raw_path') else POKEAPI_BASE + pokemon_name

    # Simple retry loop for transient upstream failures
    max_retries = 3
    backoff_base = 0.5
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)

            # Upstream 404 -> Pokemon not found
            if resp.status_code == 404:
                return json_resp({"error": "Pokemon not found"}, status_code=404)

            # If success parse and return simplified payload
            if resp.status_code == 200:
                data = resp.json()
                # Safely extract fields with fallbacks
                try:
                    result = {
                        "name": data.get("name"),
                        "type": (data.get("types") or [])[0]["type"]["name"] if data.get("types") else None,
                        "height": data.get("height"),
                        "weight": data.get("weight"),
                        "first_ability": (data.get("abilities") or [])[0]["ability"]["name"] if data.get("abilities") else None,
                    }
                except Exception:
                    # Malformed upstream response
                    return json_resp({"error": "upstream returned unexpected data"}, status_code=502)

                return json_resp(result, status_code=200)

            # For 5xx from upstream, retry
            if 500 <= resp.status_code < 600:
                raise httpx.HTTPStatusError("Upstream 5xx", request=resp.request, response=resp)

            # Other unexpected status codes -> treat as upstream failure
            return json_resp({"error": "upstream error"}, status_code=502)

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # If last attempt, return an error. Else backoff and retry.
            if attempt == max_retries:
                return json_resp({"error": "upstream service unavailable"}, status_code=502)
            await asyncio.sleep(backoff_base * attempt)


# Global handler for method not allowed and other unhandled exceptions
@app.exception_handler(405)
async def method_not_allowed(request: Request, exc):
    return json_resp({"error": "method not allowed"}, status_code=405)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc):
    # Log exception details in production; return generic error here
    return json_resp({"error": "internal server error"}, status_code=500)
