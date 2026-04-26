import asyncio
from fastapi import APIRouter, HTTPException, Query

from scraper import find_brand, get_all_brands, get_phones_for_brand

router = APIRouter()


@router.get("/")
async def list_brands():
    """Return all brands from GSMArena."""
    brands = await asyncio.to_thread(get_all_brands)
    return {"brands": brands}


@router.get("/search")
async def search_brand(q: str = Query(..., description="Brand name e.g. Samsung")):
    """Find a brand by name and return its phone listing."""
    brand = await asyncio.to_thread(find_brand, q)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{q}' not found.")
    return {"brand": brand}


@router.get("/{name}/phones")
async def brand_phones(
    name: str,
    limit: int = Query(20, description="Max phones to return, 0 = all"),
):
    """Return the phone list for a given brand name."""
    brand = await asyncio.to_thread(find_brand, name)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{name}' not found.")
    phones = await asyncio.to_thread(get_phones_for_brand, brand["url"], limit)
    return {"brand": brand, "phones": phones}
