# Lumora Decision Intelligence — Modular Streamlit Platform

A modular Streamlit application for the Lumora Bank case competition. It combines the supplied case workbook with external CSV/Excel dataset analysis.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run in Google Colab
1. Upload and extract this project ZIP in Colab.
2. Change directory into the extracted project folder.
3. Run:
```python
!pip -q install -r requirements.txt
!streamlit run app.py &>/content/lumora_streamlit.log &
```
4. Use a permitted tunnel or deploy on an authenticated Streamlit-compatible host to open the app.

## Modules
- `lumora/data.py`: workbook loading, column mapping, generic uploads, data profiling.
- `lumora/analytics.py`: KPI calculations, segmentation summaries, correlations, readiness rules, scenario analysis.
- `lumora/recommendations.py`: segment actions and next-best-action rules.
- `lumora/predictive.py`: gated binary classification with preprocessing and held-out evaluation.
- `lumora/chatbot.py`: deterministic rule-based assistant.
- `lumora/ui.py`: shared dark theme and reusable UI components.
- `app.py`: navigation and page orchestration.

## Features
Executive overview, customer intelligence, diagnostic analytics, liquidity-first readiness and recommendations, scenario simulator, universal dataset intelligence, report exports, methodology and governance.

## Important limitations
The workbook marks the bank baseline and customer sample/research as illustrative or synthetic. Do not present them as real bank observations. Predictive modelling is not claimed as validated because a reliable historical outcome label is not supplied. Readiness bands are educational screening aids, not regulated suitability decisions or investment advice. Indicative surplus is calculated only if monthly essential expenses and debt obligations are both present; otherwise it is not estimated.
