"""
agents/resource_agent.py — Nearest help resource finder.

Priority:
1. OpenStreetMap Nominatim (free, no key needed)
2. Static fallback JSON

Results are cached per (domain, location) for 5 minutes.
Never blocks pipeline — uses asyncio timeout.
"""
import asyncio
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

from utils.cache import resource_cache

load_dotenv()

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
RESOURCE_TIMEOUT = 0.6  # 600 ms max

# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS = {
    "medical": ["chest pain", "heart attack", "stroke", "bleeding", "unconscious",
                "can't breathe", "overdose", "injury", "emergency", "ambulance"],
    "mental_health": ["suicide", "kill myself", "want to die", "self harm",
                      "depressed", "hopeless", "mental", "crisis", "helpline"],
    "shelter": ["homeless", "shelter", "no place", "kicked out", "domestic violence",
                "abuse", "unsafe at home"],
    "safety": ["violence", "assault", "threatened", "danger", "police", "attacked"],
}

# ---------------------------------------------------------------------------
# Static fallback resources (India-focused)
# ---------------------------------------------------------------------------

STATIC_RESOURCES = {
    "medical": [
        {"name": "iCall Mental Health Helpline", "phone": "9152987821", "distance_km": 0, "type": "helpline"},
        {"name": "NIMHANS Emergency", "phone": "080-46110007", "distance_km": 0, "type": "hospital"},
        {"name": "Vandrevala Foundation", "phone": "1860-2662-345", "distance_km": 0, "type": "helpline"},
    ],
    "mental_health": [
        {"name": "iCall (TISS)", "phone": "9152987821", "distance_km": 0, "type": "helpline"},
        {"name": "Vandrevala Foundation 24/7", "phone": "1860-2662-345", "distance_km": 0, "type": "helpline"},
        {"name": "Snehi", "phone": "044-24640050", "distance_km": 0, "type": "helpline"},
        {"name": "AASRA", "phone": "9820466627", "distance_km": 0, "type": "helpline"},
    ],
    "shelter": [
        {"name": "iCall Crisis Support", "phone": "9152987821", "distance_km": 0, "type": "helpline"},
        {"name": "Women Helpline", "phone": "181", "distance_km": 0, "type": "helpline"},
        {"name": "Child Helpline", "phone": "1098", "distance_km": 0, "type": "helpline"},
    ],
    "safety": [
        {"name": "Police Emergency", "phone": "100", "distance_km": 0, "type": "emergency"},
        {"name": "Women Safety Helpline", "phone": "1091", "distance_km": 0, "type": "helpline"},
        {"name": "National Emergency", "phone": "112", "distance_km": 0, "type": "emergency"},
    ],
}


def detect_domain(text: str) -> str:
    """Detect resource domain from text. Returns most relevant domain."""
    lower = text.lower()
    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                scores[domain] += 1
    best = max(scores, key=lambda d: scores[d])
    return best if scores[best] > 0 else "mental_health"


async def _fetch_osm_resources(domain: str, query: str) -> list[dict]:
    """Query OpenStreetMap Nominatim for nearby resources."""
    osm_query_map = {
        "medical": "hospital",
        "mental_health": "mental health clinic",
        "shelter": "shelter",
        "safety": "police",
    }
    search_term = osm_query_map.get(domain, "hospital")

    try:
        async with httpx.AsyncClient(timeout=RESOURCE_TIMEOUT) as client:
            resp = await client.get(
                NOMINATIM_URL,
                params={
                    "q": search_term,
                    "format": "json",
                    "limit": 3,
                    "countrycodes": "in",
                },
                headers={"User-Agent": "VoiceForward-Crisis-App/1.0"},
            )
            if resp.status_code == 200:
                results = resp.json()
                return [
                    {
                        "name": r.get("display_name", "Unknown")[:60],
                        "phone": "N/A",
                        "distance_km": 0,
                        "type": domain,
                        "lat": r.get("lat"),
                        "lon": r.get("lon"),
                    }
                    for r in results[:3]
                ]
    except Exception:
        pass
    return []


async def get_resources(text: str, location: Optional[str] = None) -> dict:
    """
    Detect domain and fetch relevant resources.
    Falls back to static data if API fails or times out.

    Output:
        { "type": str, "resources": [{name, phone, distance_km, type}] }
    """
    domain = detect_domain(text)
    cache_key = f"{domain}:{location or 'default'}"

    cached = resource_cache.get(cache_key)
    if cached:
        return cached

    # Try live OSM fetch
    live_resources = await _fetch_osm_resources(domain, text)

    # Merge live + static (static always included as fallback)
    static = STATIC_RESOURCES.get(domain, STATIC_RESOURCES["mental_health"])
    resources = (live_resources + static)[:5]

    result = {"type": domain, "resources": resources}
    resource_cache.set(cache_key, result)
    return result
