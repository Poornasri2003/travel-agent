from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .geography import fetch_india_states, fetch_state_cities
from .models import TripRequest, TripResponse
from .place_image import wikipedia_thumbnail
from .planner import build_agent_payload, normalize_agent_response
from .tinyfish_client import TinyFishError, get_config, run_agent


app = FastAPI(title="TinyFish Travel Agent", version="1.0.0")

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
def startup_event() -> None:
    pass


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.post("/api/plan", response_model=TripResponse)
def create_plan(req: TripRequest) -> TripResponse:
    run_id = uuid4().hex
    payload = build_agent_payload(req)
    try:
        raw = run_agent(payload)
    except TinyFishError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
    response = normalize_agent_response(raw, req.max_budget_inr)
    response.run_id = run_id
    response.created_at = datetime.now(timezone.utc).isoformat()
    if isinstance(raw, dict):
        remote = raw.get("run_id")
        response.tinyfish_automation_run_id = str(remote) if remote is not None else None

    wiki = wikipedia_thumbnail(f"{req.to_city}, {req.to_state or 'India'}")
    if not wiki.get("url"):
        wiki = wikipedia_thumbnail(req.to_city)
    response.destination_image_url = wiki.get("url") if isinstance(wiki.get("url"), str) else None
    response.destination_image_attribution = (
        str(wiki.get("attribution")) if wiki.get("attribution") else None
    )

    return response


@app.get("/api/runs")
def get_runs(limit: int = 10) -> dict[str, list[dict]]:
    return {"items": []}


class GeographyCitiesRequest(BaseModel):
    state: str = Field(min_length=2, max_length=80)


@app.get("/api/geography/states")
def geography_states() -> dict[str, list[str]]:
    return {"states": fetch_india_states()}


@app.post("/api/geography/cities")
def geography_cities(body: GeographyCitiesRequest) -> dict[str, list[str]]:
    return {"cities": fetch_state_cities(body.state)}


@app.get("/api/place-image")
def place_image(query: str) -> dict[str, str | None]:
    info = wikipedia_thumbnail(query)
    return {"query": query, **info}


class TinyFishTestRequest(BaseModel):
    url: str
    goal: str


@app.get("/api/tinyfish/config")
def tinyfish_config() -> dict[str, str | bool]:
    config = get_config()
    return {
        "base_url": config.base_url,
        "run_path": config.run_path,
        "api_key_present": bool(config.api_key),
    }


@app.post("/api/tinyfish/test")
def tinyfish_test(req: TinyFishTestRequest) -> dict:
    payload = {"url": req.url, "goal": req.goal}
    try:
        raw = run_agent(payload)
    except TinyFishError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
    return {"ok": True, "raw": raw}
