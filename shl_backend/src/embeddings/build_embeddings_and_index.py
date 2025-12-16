import pandas as pd
import numpy as np
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss


INPUT_FILE = Path("data/processed/catalog_clean.csv")
EMBED_DIR = Path("data/embeddings")
INDEX_DIR = Path("data/index")

EMBED_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

EMBED_FILE = EMBED_DIR / "embeddings.npy"
ID_MAP_FILE = EMBED_DIR / "id_map.json"
FAISS_INDEX_FILE = INDEX_DIR / "faiss.index"

df = pd.read_csv(INPUT_FILE)

texts = df["concise_text"].astype(str).tolist()

print(f"Loaded {len(texts)} texts for embedding")

print("Loading Sentence-BERT (all-MiniLM-L12-v2)...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

print("Computing embeddings...")
embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

print(f"Embeddings shape: {embeddings.shape}")

np.save(EMBED_FILE, embeddings)

id_map = {str(i): int(i) for i in range(len(df))}
with open(ID_MAP_FILE, "w") as f:
    json.dump(id_map, f, indent=2)


dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)   # cosine similarity
index.add(embeddings)

faiss.write_index(index, str(FAISS_INDEX_FILE))

print("FAISS index built and saved")

print("\nSaved artifacts:")
print(f"- Embeddings: {EMBED_FILE}")
print(f"- ID map:     {ID_MAP_FILE}")
print(f"- FAISS:      {FAISS_INDEX_FILE}")
