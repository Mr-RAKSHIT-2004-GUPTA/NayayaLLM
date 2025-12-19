import os
import pandas as pd
from config.settings import DATA_RAW_PATH, EXTRACTED_TEXT_PATH

os.makedirs(EXTRACTED_TEXT_PATH, exist_ok=True)

df = pd.read_csv(DATA_RAW_PATH)

if "text" not in df.columns:
    raise ValueError("CSV must contain a 'text' column")

for idx, row in df.iterrows():
    text = str(row["text"]).strip()
    if not text:
        continue

    file_path = os.path.join(EXTRACTED_TEXT_PATH, f"doc_{idx:05d}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

print("Text extraction completed.")
