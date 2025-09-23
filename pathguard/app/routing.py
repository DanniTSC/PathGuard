
from typing import List, Dict

def toy_route(start: str, end: str) -> List[Dict]:
    # A tiny, hardcoded route with toy safety attributes
    # In real life you'd compute based on a graph; for MVP we keep it simple
    return [
        {"id": "s1", "name": "Main Street", "safety": 0.72, "reasons": ["dim lighting"]},
        {"id": "s2", "name": "Park Lane", "safety": 0.85, "reasons": ["good visibility"]},
        {"id": "s3", "name": "River Road", "safety": 0.65, "reasons": ["narrow sidewalk", "dim lighting"]},
    ]
