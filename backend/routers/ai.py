import asyncio
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anthropic

from scraper import search_phone_candidates, get_phone_specs

router = APIRouter()

def _get_client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured.")
    return anthropic.Anthropic(api_key=key)


class RecommendRequest(BaseModel):
    query: str  # e.g. "best camera phone under $500 with 5G"


class CompareRequest(BaseModel):
    phone1_url: str
    phone2_url: str


@router.post("/recommend")
async def recommend(req: RecommendRequest):
    """
    Takes a natural language query, uses Claude to extract a search term,
    runs the scraper, then Claude summarises the top candidates.
    """
    client = _get_client()

    # Step 1: Claude extracts a concrete search term from the natural language query
    extract = await asyncio.to_thread(
        lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": (
                    f"The user is looking for: \"{req.query}\"\n"
                    "Reply with ONLY the most likely phone model name or brand + model to search "
                    "on GSMArena (e.g. 'Samsung Galaxy S24'). No explanation, just the search term."
                ),
            }],
        )
    )
    search_term = extract.content[0].text.strip()

    # Step 2: Run scraper with extracted term
    candidates = await asyncio.to_thread(search_phone_candidates, search_term)
    if not candidates:
        raise HTTPException(status_code=404, detail=f"No phones found for '{search_term}'.")

    top = candidates[:5]

    # Step 3: Claude recommends from the candidates
    candidate_list = "\n".join(f"- {c['name']} (score: {c['score']:.2f})" for c in top)
    summary = await asyncio.to_thread(
        lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    f"The user wants: \"{req.query}\"\n\n"
                    f"These phones were found on GSMArena:\n{candidate_list}\n\n"
                    "Briefly recommend which one best matches the user's needs and why (2-3 sentences)."
                ),
            }],
        )
    )

    return {
        "query": req.query,
        "search_term": search_term,
        "candidates": top,
        "recommendation": summary.content[0].text.strip(),
    }


@router.post("/compare")
async def compare(req: CompareRequest):
    """
    Fetches specs for two phones and asks Claude to compare them.
    """
    client = _get_client()

    phone1, phone2 = await asyncio.gather(
        asyncio.to_thread(get_phone_specs, req.phone1_url),
        asyncio.to_thread(get_phone_specs, req.phone2_url),
    )

    if not phone1:
        raise HTTPException(status_code=502, detail="Could not fetch specs for phone 1.")
    if not phone2:
        raise HTTPException(status_code=502, detail="Could not fetch specs for phone 2.")

    def fmt(phone: dict) -> str:
        lines = [f"**{phone.get('name', 'Unknown')}**"]
        for k, v in list(phone.get("specs", {}).items())[:30]:
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    comparison = await asyncio.to_thread(
        lambda: client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": (
                    f"Compare these two phones based on their specs:\n\n"
                    f"{fmt(phone1)}\n\n{fmt(phone2)}\n\n"
                    "Give a concise comparison covering display, performance, camera, battery, "
                    "and value. End with a clear recommendation."
                ),
            }],
        )
    )

    return {
        "phone1": {"name": phone1.get("name"), "url": req.phone1_url, "specs": phone1.get("specs")},
        "phone2": {"name": phone2.get("name"), "url": req.phone2_url, "specs": phone2.get("specs")},
        "comparison": comparison.content[0].text.strip(),
    }
