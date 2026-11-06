import pandas as pd
import numpy as np

def segment_recommendations(df):
    if df.empty or "Segment" not in df:
        return pd.DataFrame([{"Segment":"Not available","Finding":"Segment field missing","Recommended action":"Map a customer segment field before generating segment-specific recommendations."}])
    rows=[]
    for segment, group in df.groupby("Segment", dropna=False):
        months = pd.to_numeric(group["Emergency fund (months)"], errors="coerce").mean() if "Emergency fund (months)" in group else np.nan
        conf = pd.to_numeric(group["Confidence (1–10)"], errors="coerce").mean() if "Confidence (1–10)" in group else np.nan
        high_liq = group["Liquidity need"].astype(str).str.lower().eq("high").mean() if "Liquidity need" in group else np.nan
        if (pd.notna(months) and months < 3) or (pd.notna(high_liq) and high_liq >= .4):
            action = "Protect liquidity first: explain emergency buffers, retain near-term funds and offer optional adviser support. Avoid conversion pressure."
            priority = "Protect"
        elif pd.notna(conf) and conf < 5:
            action = "Build confidence: use plain-language education, inflation visualisation and risk explanations before discussing products."
            priority = "Educate"
        else:
            action = "Offer goal-based planning and a documented suitability review. Explain fees, risks, time horizon and liquidity before any opt-in."
            priority = "Review"
        rows.append({"Segment":str(segment),"Sample size":len(group),"Average emergency fund (months)":months,
                     "Average confidence":conf,"High liquidity share":high_liq,"Priority":priority,"Recommended action":action})
    return pd.DataFrame(rows)

def next_best_action(row):
    band = row.get("Readiness band", "")
    if band == "Protect liquidity":
        return "Review emergency cash needs and near-term commitments. Keep required funds accessible."
    if band == "Educate / adviser support":
        return "Offer a guided learning journey and optional conversation with a qualified adviser."
    if band == "Potentially ready for suitability review":
        return "Invite a suitability review; this is not an automatic product recommendation."
    return "Collect missing financial-goal and liquidity information before deciding the next step."

def strategic_recommendations(baseline):
    return [
        ("Protect", "Introduce a liquidity-first financial health check before investment prompts."),
        ("Educate", "Deploy an inflation visualiser with plain-language risk and return explanations."),
        ("Guide", "Offer human adviser escalation for low confidence, complex goals or uncertainty."),
        ("Measure", "Track informed adoption alongside complaints, opt-outs, retention and customer outcomes."),
        ("Govern", "Require consent, suitability review, transparent disclosures and auditable decision rules."),
    ]
