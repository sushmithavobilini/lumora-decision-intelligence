from pathlib import Path
import pandas as pd
import numpy as np
import re

SHEET_HEADER_HINTS = {
    "Case Overview": ["area", "bank", "customer tension"],
    "Illustrative Baseline": ["metric", "value"],
    "Customer Segments": ["segment", "share"],
    "Synthetic Customer Sample": ["customer id", "segment", "age"],
    "Product Catalogue": ["product", "type"],
    "Customer Research": ["id", "segment", "barrier"],
    "Nudge Experiments": ["id", "intervention"],
    "Digital Feature Portfolio": ["feature", "type"],
}

def _detect_header(path, sheet_name, hints=None, max_rows=8):
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    hints = [x.lower() for x in (hints or [])]
    best_row, best_score = 0, -1
    for i in range(min(max_rows, len(raw))):
        vals = [str(x).strip().lower() for x in raw.iloc[i].tolist() if pd.notna(x)]
        joined = " | ".join(vals)
        score = sum(1 for h in hints if any(h in v for v in vals))
        score += min(len(vals), 10) * 0.05
        if score > best_score:
            best_row, best_score = i, score
    return best_row

def load_case_workbook(path):
    xls = pd.ExcelFile(path)
    sheets = {}
    for sheet in xls.sheet_names:
        hints = SHEET_HEADER_HINTS.get(sheet, [])
        header = _detect_header(path, sheet, hints)
        df = pd.read_excel(path, sheet_name=sheet, header=header)
        df = df.dropna(how="all").dropna(axis=1, how="all")
        df.columns = [str(c).strip() for c in df.columns]
        sheets[sheet] = df
    return sheets

def baseline_dict(sheets):
    df = sheets.get("Illustrative Baseline", pd.DataFrame())
    if df.empty: return {}
    metric = next((c for c in df.columns if "metric" in c.lower()), None)
    value = next((c for c in df.columns if "value" in c.lower()), None)
    if not metric or not value: return {}
    result = {}
    for _, row in df.iterrows():
        if pd.notna(row.get(metric)):
            result[str(row[metric]).strip()] = row[value]
    return result

ALIASES = {
    "Customer ID": ["customer id", "customerid", "client id", "account id"],
    "Segment": ["segment", "customer segment", "cluster"],
    "Age": ["age", "customer age"],
    "Monthly income (INR)": ["monthly income", "income", "salary"],
    "Savings balance (INR)": ["savings balance", "savings", "deposit balance"],
    "Emergency fund (months)": ["emergency fund", "emergency months", "buffer months"],
    "Monthly essential expenses (INR)": ["monthly essential expenses", "essential expenses", "monthly expenses"],
    "Debt obligations (INR)": ["debt obligations", "monthly debt", "loan payments", "liabilities"],
    "Liquidity need": ["liquidity need", "liquidity requirement"],
    "Goal horizon (years)": ["goal horizon", "investment horizon", "goal period"],
    "Risk comfort": ["risk comfort", "risk appetite", "risk tolerance"],
    "Confidence (1–10)": ["confidence", "investment confidence"],
    "Current product status": ["current product", "product status", "investment status"],
    "Primary channel": ["primary channel", "channel"],
    "Marketing consent": ["marketing consent", "consent"],
}

def normalize_customer_columns(df):
    rename = {}
    lower_cols = {str(c).strip().lower(): c for c in df.columns}
    for canonical, aliases in ALIASES.items():
        for col in df.columns:
            cl = str(col).strip().lower()
            if any(a in cl for a in aliases):
                rename[col] = canonical
                break
    out = df.rename(columns=rename).copy()
    for col in ["Age", "Monthly income (INR)", "Savings balance (INR)",
                "Emergency fund (months)", "Goal horizon (years)", "Confidence (1–10)",
                "Monthly essential expenses (INR)", "Debt obligations (INR)"]:
        if col in out:
            out[col] = pd.to_numeric(out[col].astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")
    return out

def load_external_dataset(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin-1")
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Please upload a CSV or Excel file.")
    df = df.dropna(how="all").dropna(axis=1, how="all")
    return df

def profile_dataset(df):
    return pd.DataFrame({
        "Column": [str(c) for c in df.columns],
        "Data type": [str(df[c].dtype) for c in df.columns],
        "Missing values": [int(df[c].isna().sum()) for c in df.columns],
        "Missing %": [round(float(df[c].isna().mean()*100), 1) for c in df.columns],
        "Unique values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })

def quality_clean(df):
    out = df.copy()
    out.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in out.columns]
    out = out.drop_duplicates()
    for c in out.select_dtypes(include="object").columns:
        out[c] = out[c].map(lambda x: x.strip() if isinstance(x, str) else x)
    return out
