import pandas as pd
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]

CATALOG_FILE = BASE_DIR / "data/processed/catalog_clean.csv"
FAISS_FILE = BASE_DIR / "data/index/faiss.index"
TRAIN_FILE = BASE_DIR / "data/train/Gen_AI_Dataset.xlsx"  # adjust if filename differs

df = pd.read_csv(CATALOG_FILE).fillna("")
index = faiss.read_index(str(FAISS_FILE))
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

train_df = pd.read_excel(TRAIN_FILE)

QUERY_COL = "Query"
RELEVANT_COL = "Assessment_url"   # comma-separated URLs

def expand_query(query: str) -> str:
    q = query.lower()
    expansions = []

    if any(k in q for k in ["java", "python", "sql", "developer", "engineer", "backend", "ml"]):
        expansions.append("knowledge and skills assessment")

    if any(k in q for k in ["collaborate", "stakeholder", "communication", "team", "lead", "manage"]):
        expansions.append("personality and behavior assessment")

    if any(k in q for k in ["senior", "manager", "lead"]):
        expansions.append("competency and leadership assessment")

    return query + ". " + ". ".join(expansions)


def recall_at_k(retrieved, relevant, k):
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & set(relevant)) / len(relevant) if relevant else 0.0


recall_5 = []
recall_10 = []

for _, row in train_df.iterrows():
    query = row[QUERY_COL]
    relevant_urls = [u.strip() for u in row[RELEVANT_COL].split(",")]

    expanded_query = expand_query(query)

    query_vec = model.encode(
        [expanded_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    _, indices = index.search(query_vec, 30)

    retrieved_urls = [
        df.iloc[int(i)]["URL"] for i in indices[0]
    ]

    recall_5.append(recall_at_k(retrieved_urls, relevant_urls, 5))
    recall_10.append(recall_at_k(retrieved_urls, relevant_urls, 10))

print("Evaluation Results (After Query Expansion)")
print(f"Mean Recall@5  : {np.mean(recall_5):.3f}")
print(f"Mean Recall@10 : {np.mean(recall_10):.3f}")
