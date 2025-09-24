
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import os

from .explain import explain_route
from .routing import toy_route
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PathGuard API", version="0.1.0")

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Segment(BaseModel):
    id: str
    name: str
    safety: float
    reasons: List[str]


class RouteResponse(BaseModel):
    segments: List[Segment]
    safety_score: float
    explanation: str


@app.get("/")
def root():
    return {"name": "PathGuard API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok", "env": {"USE_HF": os.getenv("USE_HF", "false")}}


@app.get("/route", response_model=RouteResponse)
def get_route(
    start: str = Query(..., description="lat,lon e.g. 50.1,8.6"),
    end: str = Query(..., description="lat,lon e.g. 50.11,8.68"),
):
    # parse inputs (not used in toy_route, but realistic signature)
    segments = toy_route(start, end)  # returns list of dicts with id,name,safety,reasons
    score = sum(s["safety"] for s in segments) / max(len(segments), 1)
    explanation = explain_route(segments, use_hf=os.getenv("USE_HF", "false").lower() == "true")
    return {"segments": segments, "safety_score": round(score, 3), "explanation": explanation}
