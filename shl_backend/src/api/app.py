from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import numpy as np
import faiss
import math
import re
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[2]

CATALOG_FILE = BASE_DIR / "data/processed/catalog_clean.csv"
FAISS_FILE = BASE_DIR / "data/index/faiss.index"

df = pd.read_csv(CATALOG_FILE).fillna("")
index = faiss.read_index(str(FAISS_FILE))
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendRequest(BaseModel):
    query: str
    top_k: int = 10

def safe_str(x):
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x)

def parse_duration_to_minutes(value: str) -> int:
    if not value:
        return 0
    match = re.search(r"\d+", value)
    if match:
        return int(match.group())
    return 0

def expand_query(query: str) -> str:
    q = query.lower()
    expansions = []

    if any(k in q for k in ["java", "python", "sql", "developer", "engineer", "backend", "ml"]):
        expansions.append("knowledge and skills assessment")

    if any(k in q for k in ["collaborate", "stakeholder", "communication", "team", "lead", "manage"]):
        expansions.append("personality and behavior assessment")

    return query + ". " + ". ".join(expansions)

def balance_by_test_type(candidates, top_k):
    k_items, p_items, other_items = [], [], []

    for item in candidates:
        t = item["test_type"].lower()
        if "knowledge" in t:
            k_items.append(item)
        elif "personality" in t:
            p_items.append(item)
        else:
            other_items.append(item)

    final = []

    k_target = int(top_k * 0.6)
    p_target = int(top_k * 0.4)

    final.extend(k_items[:k_target])
    final.extend(p_items[:p_target])

    remaining = top_k - len(final)
    if remaining > 0:
        final.extend(other_items[:remaining])

    return final[:top_k]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    top_k = max(1, min(req.top_k, 10))

    expanded_query = expand_query(req.query)

    query_vector = model.encode(
        [expanded_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    _, indices = index.search(query_vector, 30)

    candidates = []
    for idx in indices[0]:
        row = df.iloc[int(idx)]
        candidates.append({
            "name": safe_str(row["Name"]),
            "url": safe_str(row["URL"]),
            "description": safe_str(row["Description"]),
            "test_type": safe_str(row["Test Type"]),
            "duration": parse_duration_to_minutes(safe_str(row["Duration"])),
            "remote_support": safe_str(row["Remote Testing"]),
            "adaptive_support": safe_str(row["Adaptive/IRT Support"])
        })

    results = balance_by_test_type(candidates, top_k)

    return {
        "recommended_assessments": results
    }

