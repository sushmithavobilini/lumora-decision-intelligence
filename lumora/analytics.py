import numpy as np
import pandas as pd

def safe_num(df, col):
    if col not in df: return pd.Series(index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce")

def kpi_snapshot(baseline):
    active = baseline.get("Active retail customers", np.nan)
    savers = baseline.get("Savings-account customers", np.nan)
    investors = baseline.get("Customers with any investment product", np.nan)
    balances = baseline.get("Total savings-account balances", np.nan)
    def div(a,b):
        try: return float(a)/float(b)*100
        except: return np.nan
    return {
        "Active customers": active,
        "Savings customers": savers,
        "Investment customers": investors,
        "Investment penetration (%)": div(investors, active),
        "Savings customer share (%)": div(savers, active),
        "Total savings balances": balances,
        "Average savings balance": (float(balances)/float(savers)) if pd.notna(balances) and pd.notna(savers) and float(savers) else np.nan,
    }

def segment_summary(df):
    if df.empty or "Segment" not in df: return pd.DataFrame()
    agg = {}
    for col in ["Age","Monthly income (INR)","Savings balance (INR)","Emergency fund (months)","Goal horizon (years)","Confidence (1–10)"]:
        if col in df: agg[col] = (col, "mean")
    out = df.groupby("Segment", dropna=False).size().rename("Sample customers").to_frame()
    if agg:
        extra = df.groupby("Segment", dropna=False).agg(**{f"Mean {k}": v for k,v in agg.items()})
        out = out.join(extra)
    return out.reset_index()

def correlation_matrix(df):
    cols = [c for c in ["Age","Monthly income (INR)","Savings balance (INR)","Emergency fund (months)","Goal horizon (years)","Confidence (1–10)"] if c in df]
    if len(cols) < 2: return pd.DataFrame()
    return df[cols].apply(pd.to_numeric, errors="coerce").corr()

def readiness_assessment(df):
    out = df.copy()
    if out.empty: return out
    emergency = safe_num(out, "Emergency fund (months)")
    confidence = safe_num(out, "Confidence (1–10)")
    horizon = safe_num(out, "Goal horizon (years)")
    liquidity = out["Liquidity need"].astype(str).str.lower() if "Liquidity need" in out else pd.Series("", index=out.index)
    conditions = [
        (emergency.notna() & (emergency < 3)) | liquidity.eq("high"),
        (confidence.notna() & (confidence < 5)) | (horizon.notna() & (horizon < 3)),
        (emergency.notna() & (emergency >= 6)) & (confidence.notna() & (confidence >= 6)) & (horizon.notna() & (horizon >= 5)),
    ]
    choices = ["Protect liquidity", "Educate / adviser support", "Potentially ready for suitability review"]
    out["Readiness band"] = np.select(conditions, choices, default="Needs suitability review")
    # Only estimate potential surplus when all required expense/obligation fields exist.
    required = ["Savings balance (INR)", "Monthly essential expenses (INR)", "Debt obligations (INR)"]
    if all(c in out.columns for c in required):
        savings = safe_num(out, required[0])
        expenses = safe_num(out, required[1])
        debt = safe_num(out, required[2]).fillna(0)
        buffer_months = emergency.fillna(0).clip(lower=0)
        reserve = expenses * np.maximum(buffer_months, 6)
        out["Indicative surplus after reserve and debt"] = (savings - reserve - debt).clip(lower=0)
        out.loc[out["Readiness band"] != "Potentially ready for suitability review", "Indicative surplus after reserve and debt"] = 0
    return out

def inflation_projection(principal, savings_rate, inflation_rate, years, investment_rate=None):
    rows=[]
    for year in range(int(years)+1):
        nominal = principal * (1+savings_rate/100)**year
        real = nominal / (1+inflation_rate/100)**year
        row={"Year":year,"Savings nominal value":nominal,"Savings purchasing power (today's money)":real}
        if investment_rate is not None:
            row["Illustrative investment scenario"] = principal*(1+investment_rate/100)**year
        rows.append(row)
    return pd.DataFrame(rows)

def generic_numeric_summary(df):
    nums = df.select_dtypes(include=np.number)
    if nums.empty: return pd.DataFrame()
    return nums.describe().T.reset_index(names="Column")

def category_summary(df, col, top_n=15):
    return df[col].astype(str).value_counts(dropna=False).head(top_n).rename_axis(col).reset_index(name="Records")

def experiment_kpis():
    return pd.DataFrame([
        ["Education A/B test","Inflation visualiser vs standard explainer","Comprehension score","Misunderstanding, exit rate"],
        ["Liquidity journey pilot","Emergency-buffer check vs no check","Suitable plan completion","Inadequate buffer, opt-outs"],
        ["Adviser support pilot","Callback offer vs digital-only","Issue resolution and trust","Wait time, cost, complaints"],
        ["Cohort monitoring","Voluntary recurring plan","6-month continuation","Opt-outs, missed contributions"],
    ], columns=["Experiment","Comparison","Primary outcome","Guardrails"])
