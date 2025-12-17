import pandas as pd
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]

CATALOG_FILE = BASE_DIR / "data/processed/catalog_clean.csv"
FAISS_FILE = BASE_DIR / "data/index/faiss.index"
TEST_FILE = BASE_DIR / "data/dataset/Gen_AI_Dataset.xlsx"   # adjust name if needed
OUTPUT_FILE = BASE_DIR / "data/test_predictions/test_predictions.csv"


df = pd.read_csv(CATALOG_FILE).fillna("")
index = faiss.read_index(str(FAISS_FILE))
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

test_df  = pd.read_excel(TEST_FILE, sheet_name="Test-Set")

QUERY_COL = "Query"
TOP_K = 10


def expand_query(query: str) -> str:
    q = query.lower()
    expansions = []

    if any(k in q for k in ["java", "python", "sql", "developer", "engineer", "backend", "ml"]):
        expansions.append("knowledge and skills assessment")

    if any(k in q for k in ["collaborate", "stakeholder", "communication", "team", "lead", "manage"]):
        expansions.append("personality and behavior assessment")

    return query + ". " + ". ".join(expansions)

# ---------------- GENERATE PREDICTIONS ---------------- #

rows = []

for _, row in test_df.iterrows():
    query = row[QUERY_COL]

    expanded_query = expand_query(query)

    query_vec = model.encode(
        [expanded_query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    _, indices = index.search(query_vec, 30)

    urls = []
    for idx in indices[0]:
        url = df.iloc[int(idx)]["URL"]
        if url not in urls:
            urls.append(url)
        if len(urls) == TOP_K:
            break

    for url in urls:
        rows.append({
            "Query": query,
            "Assessment_url": url
        })


pd.DataFrame(rows).to_csv(OUTPUT_FILE, index=False)

print(f"Saved test predictions to {OUTPUT_FILE}")
