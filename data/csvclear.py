# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import pandas as pd
import re

# Paths for raw, intermediate, and cleaned datasets
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW = DATA_DIR / "2022.csv"             # Original CSV export with "Stadtgebiet" column
CLEAN = DATA_DIR / "2022_clean.csv"     # Optional pre-cleaned file (without district)
OUT = DATA_DIR / "2022_ready.csv"       # Final output file after cleaning

def _to_float(x):
    """Convert messy numeric strings (e.g. with spaces, commas, plus signs) into floats."""
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if s in ("", "-", "–", "."):
        return pd.NA

    # Clean up spaces, non-breaking spaces, plus signs, unify minus and decimal point
    s = (s.replace("\u00A0", "")
           .replace(" ", "")
           .replace("+", "")
           .replace("−", "-")
           .replace(",", "."))

    # Extract the first numeric value (supports negative and decimal)
    m = re.findall(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return pd.NA
    try:
        return float(m[0])
    except Exception:
        return pd.NA

def load_from_raw(path: Path) -> pd.DataFrame:
    """
    Read the original CSV which contains two header rows:
    the first row = group, second row = actual column names.
    """
    tmp = pd.read_csv(path, sep=";", header=None, dtype=str, engine="python")
    names = tmp.iloc[1].tolist()
    names[0] = "district"  # replace the empty top-left cell with the proper column name

    df = tmp.iloc[2:].copy()  # data starts at row index 2
    df.columns = [str(c).strip().replace("\u00A0", " ") for c in names]

    # Drop empty rows and strip whitespace from district names
    df = df[df["district"].notna()].copy()
    df["district"] = df["district"].str.strip()
    df = df[df["district"].str.len() > 0]

    # Convert all numeric columns using _to_float
    for col in df.columns:
        if col == "district":
            continue
        df[col] = df[col].apply(_to_float)
    return df

def maybe_from_clean(clean_path: Path, raw_path: Path) -> pd.DataFrame:
    """
    If a pre-cleaned file exists but doesn't include 'district',
    attach the 'district' column from the raw file.
    """
    df = pd.read_csv(clean_path, sep=";", dtype=str, engine="python")
    df.columns = [c.strip() for c in df.columns]

    if "district" in df.columns:
        # Already includes district — just convert numbers and return
        for col in df.columns:
            if col != "district":
                df[col] = df[col].apply(_to_float)
        return df

    # If district is missing, grab it from the raw file and merge
    base = load_from_raw(raw_path)[["district"]]
    df_num = df.applymap(_to_float)
    out = pd.concat([base.reset_index(drop=True), df_num.reset_index(drop=True)], axis=1)
    return out

def main():
    # Use clean file if available, otherwise parse the raw file
    if CLEAN.exists():
        df = maybe_from_clean(CLEAN, RAW)
    else:
        df = load_from_raw(RAW)

    # Normalize district names (remove extra spaces)
    df["district"] = (df["district"]
                      .str.replace(r"\s+", " ", regex=True)
                      .str.strip())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")
    print(f"✅ Saved {OUT} with {len(df)} rows × {len(df.columns)} columns.")

if __name__ == "__main__":
    main()
