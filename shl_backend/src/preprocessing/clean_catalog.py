import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/shl_product_details.csv")
OUTPUT_FILE = Path("data/processed/catalog_clean.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


df = pd.read_csv(RAW_FILE)


def clean_text(x):
    if pd.isna(x):
        return ""
    x = str(x).strip()
    if x.lower() in ["n/a", "na", "none", "error"]:
        return ""
    return x


for col in df.columns:
    df[col] = df[col].apply(clean_text)


df = df[df["Name"] != ""]
df = df[df["URL"] != ""]



def build_concise_text(row):
    parts = [
        row.get("Name", ""),
        row.get("Description", ""),
        f"Test type: {row.get('Test Type', '')}",
        f"Duration: {row.get('Duration', '')}"
    ]
    return ". ".join([p for p in parts if p])

df["concise_text"] = df.apply(build_concise_text, axis=1)

df.to_csv(OUTPUT_FILE, index=False)

print(f"Clean catalog saved to: {OUTPUT_FILE}")
print(f"Total clean assessments: {len(df)}")
