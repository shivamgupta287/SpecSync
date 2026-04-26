import asyncio
from fastapi import APIRouter, HTTPException, Query

from scraper import search_phone_candidates, get_phone_specs

router = APIRouter()


@router.get("/search")
async def search_phones(q: str = Query(..., description="Phone name e.g. Samsung Galaxy S24")):
    """
    Search for a phone by name.
    Returns a list of scored candidates — the frontend picks one and calls /specs.
    """
    candidates = await asyncio.to_thread(search_phone_candidates, q)
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No phones found for '{q}'.")
    return {"query": q, "candidates": candidates}


@router.get("/specs")
async def phone_specs(url: str = Query(..., description="GSMArena phone page URL")):
    """Fetch full specs for a phone by its GSMArena URL."""
    specs = await asyncio.to_thread(get_phone_specs, url)
    if not specs:
        raise HTTPException(status_code=502, detail="Could not fetch specs from GSMArena.")
    return specs
