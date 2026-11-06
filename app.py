import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from lumora.config import *
from lumora.data import load_case_workbook, baseline_dict, normalize_customer_columns, load_external_dataset, profile_dataset, quality_clean
from lumora.analytics import kpi_snapshot, segment_summary, correlation_matrix, readiness_assessment, inflation_projection, generic_numeric_summary, category_summary, experiment_kpis
from lumora.recommendations import segment_recommendations, next_best_action, strategic_recommendations
from lumora.chatbot import answer_question
from lumora.predictive import train_binary_classifier
from lumora.ui import apply_theme, hero, kpi_card, insight

st.set_page_config(page_title="Lumora | Decision Intelligence", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")
apply_theme()

# ---------------- Session state ----------------
for key, default in {
    "external_df": None, "external_name": None, "chat_history": [],
    "active_dataset": "Lumora case workbook"
}.items():
    if key not in st.session_state: st.session_state[key] = default

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## 🏦 LUMORA")
    st.caption("DECISION INTELLIGENCE PLATFORM")
    st.markdown("---")
    page = st.radio("WORKSPACE", PAGE_NAMES, label_visibility="visible")
    st.markdown("---")
    st.markdown("**DATA SOURCE**")
    use_external = st.toggle("Use uploaded dataset as active customer data", value=False, disabled=st.session_state.external_df is None)
    st.session_state.active_dataset = st.session_state.external_name if use_external and st.session_state.external_df is not None else "Lumora case workbook"
    st.markdown("---")
    st.markdown("**QUICK STATUS**")
    st.caption("Case workbook: loaded locally")
    st.caption("External dataset: " + ("available" if st.session_state.external_df is not None else "not uploaded"))
    st.markdown("---")
    st.markdown("### ✦ Lumora Guide")
    st.caption("Rule-based analytical assistant")
    for role, message in st.session_state.chat_history[-6:]:
        with st.chat_message(role):
            st.write(message)
    prompt = st.chat_input("Ask Lumora Guide...")

# ---------------- Load source workbook ----------------
case_path = Path(CASE_WORKBOOK)
if not case_path.exists():
    case_path = Path(__file__).parent / CASE_WORKBOOK
if not case_path.exists():
    case_path = Path(__file__).parent / "data" / "Lumora_Case_Workbook.xlsx"
try:
    case_sheets = load_case_workbook(case_path)
except Exception as e:
    st.error(f"Unable to load the Lumora case workbook: {e}")
    st.stop()

baseline = baseline_dict(case_sheets)
case_customers = normalize_customer_columns(case_sheets.get("Synthetic Customer Sample", pd.DataFrame()))
active_customers = case_customers.copy()
if use_external and st.session_state.external_df is not None:
    active_customers = normalize_customer_columns(st.session_state.external_df)
active_customers = quality_clean(active_customers)
readiness = readiness_assessment(active_customers)
kpis = kpi_snapshot(baseline)
source_note = "Illustrative baseline and synthetic customer sample" if st.session_state.active_dataset == "Lumora case workbook" else f"Uploaded dataset: {st.session_state.external_name}"

if prompt:
    chat_context = {"active_dataset": st.session_state.active_dataset}
    if "Readiness band" in readiness:
        chat_context["readiness_counts"] = readiness["Readiness band"].value_counts().to_dict()
    try:
        chat_context["segment_recommendations"] = segment_recommendations(readiness).to_dict("records")
    except Exception:
        chat_context["segment_recommendations"] = []
    reply = answer_question(prompt, page, chat_context)
    st.session_state.chat_history.extend([("user", prompt), ("assistant", reply)])
    st.rerun()

# ---------------- Page: Overview ----------------
if page == "Executive Overview":
    hero("Banking intelligence, simplified.", "Understand customer behaviour, protect liquidity and support responsible wealth growth.", "LUMORA / EXECUTIVE OVERVIEW")
    st.caption(f"Active source: {source_note}")
    cols = st.columns(4)
    vals = [
        ("Active customers", f"{float(kpis['Active customers'])/1e6:.1f}M" if pd.notna(kpis["Active customers"]) else "—", "Illustrative bank baseline"),
        ("Savings customers", f"{float(kpis['Savings customers'])/1e6:.1f}M" if pd.notna(kpis["Savings customers"]) else "—", "Illustrative bank baseline"),
        ("Investment penetration", f"{kpis['Investment penetration (%)']:.1f}%" if pd.notna(kpis["Investment penetration (%)"]) else "—", "Investment customers / active customers"),
        ("Average savings balance", f"₹{kpis['Average savings balance']:,.0f}" if pd.notna(kpis["Average savings balance"]) else "—", "Implied average from aggregate baseline"),
    ]
    for c, (lab, val, note) in zip(cols, vals):
        with c: kpi_card(lab, val, note)
    st.write("")
    c1, c2 = st.columns([1.2,1])
    with c1:
        st.subheader("Savings vs purchasing power")
        rate = float(baseline.get("Savings interest rate", 3))
        inf = float(baseline.get("Long-run inflation scenario", 5.5))
        projection = inflation_projection(100000, rate, inf, 5)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=projection["Year"], y=projection["Savings nominal value"], name="Nominal savings", mode="lines+markers", line=dict(color="#53A6DE", width=3)))
        fig.add_trace(go.Scatter(x=projection["Year"], y=projection["Savings purchasing power (today's money)"], name="Real purchasing power", mode="lines+markers", line=dict(color="#E8A34A", width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, yaxis_title="Value (₹)", legend=dict(orientation="h", y=-.2), margin=dict(t=15,b=20,l=5,r=5))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Customer confidence barriers")
        labels = ["Low investment confidence", "Principal-loss concern", "Unsure about liquid cash"]
        values = [float(baseline.get("Low investment confidence",0)), float(baseline.get("Concerned about principal loss",0)), float(baseline.get("Unsure how much cash to keep liquid",0))]
        bar = pd.DataFrame({"Barrier":labels,"Share (%)":values})
        fig = px.bar(bar, x="Share (%)", y="Barrier", orientation="h", text="Share (%)", color="Share (%)", color_continuous_scale=["#214663","#4DA9D8"])
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, coloraxis_showscale=False, margin=dict(t=15,b=10,l=5,r=5))
        st.plotly_chart(fig, use_container_width=True)
    insight("<b>Analyst interpretation:</b> The case baseline shows a savings-led customer base alongside confidence, principal-risk and liquidity concerns. The response should be suitability-led education and planning—not blanket investment conversion.")
    st.subheader("Operating reach")
    m1,m2,m3 = st.columns(3)
    m1.metric("Annual education reach", f"{float(baseline.get('Annual education reach',0))/1000:,.0f}K")
    m2.metric("Annual suitability reviews", f"{float(baseline.get('Annual suitability reviews',0))/1000:,.0f}K")
    m3.metric("Communication complaints", f"{float(baseline.get('Confusing investment communication complaints',0)):,.0f}")
    insight("All case baseline values are illustrative. The customer sample and research cards are synthetic.", warning=True)

# ---------------- Page: Customer Intelligence ----------------
elif page == "Customer Intelligence":
    hero("Customer intelligence", "Explore who Lumora's customers are, what they need and where the barriers differ.", "LUMORA / CUSTOMER 360")
    seg = case_sheets.get("Customer Segments", pd.DataFrame())
    if not seg.empty:
        seg = seg.loc[:, ~seg.columns.astype(str).str.contains("^Unnamed")]
        share = next((c for c in seg if "share" in c.lower()), None)
        name = next((c for c in seg if "segment" in c.lower()), None)
        if share and name:
            a,b = st.columns([1,1.2])
            with a:
                st.subheader("Case-defined customer mix")
                fig=px.pie(seg,names=name,values=share,hole=.58)
                fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350,margin=dict(t=10,b=10))
                st.plotly_chart(fig,use_container_width=True)
            with b:
                st.subheader("Segment needs and confidence")
                x=next((c for c in seg if "liquidity" in c.lower()),None)
                y=next((c for c in seg if "confidence" in c.lower()),None)
                if x and y:
                    fig=px.scatter(seg,x=x,y=y,size=share,color=name,hover_name=name)
                    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350,margin=dict(t=10,b=10))
                    st.plotly_chart(fig,use_container_width=True)
            st.dataframe(seg,use_container_width=True,hide_index=True)
    if not active_customers.empty and "Segment" in active_customers:
        st.subheader("Customer sample explorer")
        options=["All"]+sorted(active_customers["Segment"].dropna().astype(str).unique().tolist())
        selected=st.selectbox("Filter segment",options)
        view=active_customers if selected=="All" else active_customers[active_customers["Segment"].astype(str)==selected]
        st.caption(f"{len(view):,} records shown · {source_note}")
        st.dataframe(view,use_container_width=True,hide_index=True)
        if "Segment" in active_customers:
            summary=segment_summary(active_customers)
            st.subheader("Segment profile")
            st.dataframe(summary.round(2),use_container_width=True,hide_index=True)
    else:
        insight("The active dataset does not contain a recognised Segment column. Upload or map a segment field to enable customer segmentation.", warning=True)

# ---------------- Page: Diagnostic Analytics ----------------
elif page == "Diagnostic Analytics":
    hero("Diagnostic analytics", "Move beyond what is happening to investigate relationships and possible drivers.", "LUMORA / ROOT-CAUSE EXPLORER")
    if active_customers.empty:
        st.info("No customer records are available in the active dataset.")
    else:
        corr=correlation_matrix(active_customers)
        if not corr.empty:
            st.subheader("Correlation matrix")
            fig=px.imshow(corr,text_auto=".2f",color_continuous_scale="RdBu_r",zmin=-1,zmax=1,aspect="auto")
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=520)
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("At least two recognised numeric customer fields are required for correlation analysis.")
        if "Segment" in active_customers:
            num_options=[c for c in ["Confidence (1–10)","Savings balance (INR)","Emergency fund (months)","Goal horizon (years)","Monthly income (INR)"] if c in active_customers]
            if num_options:
                selected_metric=st.selectbox("Compare metric across segments",num_options)
                plot_df=active_customers.copy()
                plot_df[selected_metric]=pd.to_numeric(plot_df[selected_metric],errors="coerce")
                fig=px.box(plot_df,x="Segment",y=selected_metric,color="Segment",points="all")
                fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=430,showlegend=False,xaxis_tickangle=-20)
                st.plotly_chart(fig,use_container_width=True)
        insight("Correlation is not causation. The supplied 120-record customer sample is synthetic and suitable for demonstrating methods, not bank-wide inference.", warning=True)


# ---------------- Page: Predictive Analytics ----------------
elif page == "Predictive Analytics":
    hero("Predictive analytics", "Test whether historical labelled data can support a responsible customer adoption model.", "LUMORA / MODEL LAB")
    st.caption("Predictive modelling is gated: no model is trained unless the dataset has a suitable binary outcome and enough labelled observations.")
    if active_customers.empty:
        st.info("Upload a labelled customer dataset to begin.")
    else:
        targets=[c for c in active_customers.columns if active_customers[c].nunique(dropna=True)==2 and active_customers[c].notna().sum()>=50]
        if not targets:
            insight("No suitable binary outcome field was detected. The supplied Lumora 120-row synthetic sample does not provide a reliable historical investment-adoption label. A validated propensity model cannot be claimed.", warning=True)
            st.markdown("#### Data required for a future adoption model")
            st.markdown("""
            - Consented historical customer records.
            - A clear binary outcome, such as suitable product adoption within 90 days.
            - A defined observation window and outcome window.
            - Features recorded before the outcome to prevent data leakage.
            - Adequate representation across customer segments.
            """)
        else:
            target=st.selectbox("Select binary outcome field",targets)
            model_name=st.selectbox("Model",["Logistic Regression","Random Forest"])
            test_size=st.slider("Test data share",0.2,0.4,0.25,0.05)
            st.caption("Identifier-like fields are excluded automatically. Review features for leakage before interpreting results.")
            if st.button("Train and evaluate model",type="primary"):
                try:
                    model,metrics,cm,report=train_binary_classifier(active_customers,target,model_name,test_size)
                    st.session_state["predictive_metrics"]=metrics
                    st.session_state["predictive_cm"]=cm
                    st.session_state["predictive_report"]=report
                    st.session_state["predictive_model_name"]=model_name
                    st.success("Model trained and evaluated on a held-out test split.")
                except Exception as e:
                    st.error(str(e))
            if "predictive_metrics" in st.session_state:
                met=st.session_state["predictive_metrics"]
                st.subheader("Held-out test performance")
                m1,m2,m3,m4=st.columns(4)
                m1.metric("Accuracy",f"{met['Accuracy']:.1%}")
                m2.metric("Precision",f"{met['Precision (positive class)']:.1%}")
                m3.metric("Recall",f"{met['Recall (positive class)']:.1%}")
                m4.metric("ROC-AUC",f"{met['ROC-AUC']:.3f}" if pd.notna(met["ROC-AUC"]) else "—")
                st.caption(f"Model: {st.session_state['predictive_model_name']} · Train: {met['Training records']} · Test: {met['Test records']} · Positive class: {met['Positive class']}")
                st.dataframe(st.session_state["predictive_cm"],use_container_width=True)
                st.text(st.session_state["predictive_report"])
                insight("Model metrics are exploratory and depend on the selected dataset, target definition, sampling and feature quality. They do not establish causal effects or guarantee future performance.", warning=True)

# ---------------- Page: Readiness & Recommendations ----------------
elif page == "Readiness & Recommendations":
    hero("Readiness & recommendations", "A liquidity-first decision framework that guides customers toward an appropriate next step.", "LUMORA / DECISION ENGINE")
    st.caption("Transparent educational screening rules. Not a regulated suitability determination or investment advice.")
    if readiness.empty or "Readiness band" not in readiness:
        st.warning("The active dataset does not contain enough recognised fields to run the readiness screening.")
    else:
        counts=readiness["Readiness band"].value_counts().rename_axis("Readiness band").reset_index(name="Customers")
        a,b=st.columns([.9,1.1])
        with a:
            fig=px.pie(counts,names="Readiness band",values="Customers",hole=.55)
            fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=350)
            st.plotly_chart(fig,use_container_width=True)
        with b:
            st.markdown("#### Screening rules")
            st.markdown("""
            - **Protect liquidity:** emergency fund below 3 months or high liquidity need.
            - **Educate / adviser support:** low confidence or goal horizon below 3 years.
            - **Potentially ready for suitability review:** at least 6 months' emergency fund, confidence ≥6 and horizon ≥5 years.
            - **Needs suitability review:** all other cases.
            """)
            st.caption("Missing values are not treated as evidence of readiness.")
        recs=segment_recommendations(readiness)
        st.subheader("Segment-level recommendations")
        if not recs.empty:
            for _,r in recs.iterrows():
                with st.expander(f"{r['Segment']} · {r.get('Priority','Review')}"):
                    st.write(r["Recommended action"])
                    st.caption(f"Sample size: {r.get('Sample size','—')}")
        st.subheader("Customer-level screening")
        display_cols=[c for c in ["Customer ID","Segment","Emergency fund (months)","Liquidity need","Goal horizon (years)","Confidence (1–10)","Readiness band","Indicative surplus after reserve and debt"] if c in readiness]
        st.dataframe(readiness[display_cols],use_container_width=True,hide_index=True)
        if "Indicative surplus after reserve and debt" not in readiness:
            insight("Investable surplus is not calculated because monthly essential expenses and debt obligations are not both available. We will not infer a safe investment amount from savings balance alone.", warning=True)
        st.download_button("Download readiness assessment CSV",readiness.to_csv(index=False).encode("utf-8"),"lumora_readiness_assessment.csv","text/csv")
    st.subheader("Bank-wide strategic priorities")
    for title, desc in strategic_recommendations(baseline):
        insight(f"<b>{title}:</b> {desc}")

# ---------------- Page: Scenario Simulator ----------------
elif page == "Scenario Simulator":
    hero("Scenario simulator", "Stress-test savings, inflation and hypothetical investment outcomes using transparent assumptions.", "LUMORA / WHAT-IF LAB")
    st.caption("All market-linked returns are hypothetical scenario assumptions—not predictions, live quotes or guarantees.")
    a,b,c=st.columns(3)
    principal=a.number_input("Starting amount (₹)",1000,100000000,100000,10000)
    savings_rate=b.slider("Savings interest (% p.a.)",0.0,12.0,3.0,.25)
    inflation=c.slider("Inflation (% p.a.)",0.0,15.0,5.5,.25)
    d,e=st.columns(2)
    years=d.select_slider("Time horizon",options=[1,2,3,4,5,7,10],value=5)
    investment_rate=e.slider("Hypothetical investment return (% p.a.)",-15.0,20.0,8.0,.5)
    projection=inflation_projection(principal,savings_rate,inflation,years,investment_rate)
    fig=go.Figure()
    for col in projection.columns[1:]:
        fig.add_trace(go.Scatter(x=projection["Year"],y=projection[col],mode="lines+markers",name=col))
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=450,hovermode="x unified",yaxis_title="Value (₹)")
    st.plotly_chart(fig,use_container_width=True)
    last=projection.iloc[-1]
    x,y,z=st.columns(3)
    x.metric("Savings nominal",f"₹{last['Savings nominal value']:,.0f}")
    real_value = last.iloc[2]
    y.metric("Savings real purchasing power", f"₹{real_value:,.0f}")
    st.dataframe(projection.round(2),use_container_width=True,hide_index=True)
    st.download_button("Download scenario CSV",projection.to_csv(index=False).encode("utf-8"),"lumora_scenario.csv","text/csv")

# ---------------- Page: Dataset Intelligence ----------------
elif page == "Dataset Intelligence":
    hero("Dataset intelligence", "Upload another dataset and automatically profile, clean and explore its structure.", "LUMORA / UNIVERSAL DATA LAB")
    st.markdown("Upload CSV or Excel. The platform will inspect data quality, numeric distributions, categorical composition and selected relationships.")
    uploaded=st.file_uploader("Upload a dataset",type=["csv","xlsx","xls"],key="dataset_upload")
    if uploaded:
        try:
            df=quality_clean(load_external_dataset(uploaded))
            st.session_state.external_df=df
            st.session_state.external_name=uploaded.name
            st.success(f"Loaded {len(df):,} rows × {len(df.columns)} columns.")
            st.subheader("Data preview")
            st.dataframe(df.head(100),use_container_width=True,hide_index=True)
            st.subheader("Data quality profile")
            st.dataframe(profile_dataset(df),use_container_width=True,hide_index=True)
            num_cols=df.select_dtypes(include=np.number).columns.tolist()
            cat_cols=df.select_dtypes(exclude=np.number).columns.tolist()
            if num_cols:
                st.subheader("Numeric distribution")
                chosen=st.selectbox("Numeric field",num_cols)
                fig=px.histogram(df,x=chosen,marginal="box",nbins=35)
                fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=380)
                st.plotly_chart(fig,use_container_width=True)
            if len(num_cols)>=2:
                st.subheader("Relationship explorer")
                x=st.selectbox("X-axis",num_cols,index=0)
                y=st.selectbox("Y-axis",num_cols,index=1)
                color=st.selectbox("Colour by",["None"]+cat_cols)
                fig=px.scatter(df,x=x,y=y,color=None if color=="None" else color,hover_data=cat_cols[:3])
                fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=430)
                st.plotly_chart(fig,use_container_width=True)
            if cat_cols:
                st.subheader("Category explorer")
                category=st.selectbox("Category field",cat_cols)
                counts=category_summary(df,category)
                fig=px.bar(counts,x=category,y="Records",text="Records")
                fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",height=380)
                st.plotly_chart(fig,use_container_width=True)
            st.subheader("Numeric summary")
            summary=generic_numeric_summary(df)
            if not summary.empty: st.dataframe(summary.round(2),use_container_width=True,hide_index=True)
            st.download_button("Download cleaned dataset",df.to_csv(index=False).encode("utf-8"),"cleaned_dataset.csv","text/csv")
            st.info("To run Lumora banking readiness rules on this dataset, map equivalent columns such as emergency-fund months, liquidity need, goal horizon and confidence. Arbitrary datasets receive generic exploratory analysis only.")
        except Exception as e:
            st.error(f"Dataset could not be analysed: {e}")
    else:
        st.info("Choose a CSV or Excel file to begin. The case workbook remains available in the other dashboard modules.")

# ---------------- Page: Reports Centre ----------------
elif page == "Reports Centre":
    hero("Reports centre", "Export reproducible outputs from the current data source and scenario analysis.", "LUMORA / REPORTING")
    st.caption(f"Active source: {source_note}")
    if not readiness.empty:
        st.download_button("Download customer readiness CSV",readiness.to_csv(index=False).encode("utf-8"),"lumora_readiness.csv","text/csv")
    recs=segment_recommendations(readiness)
    st.download_button("Download segment recommendations CSV",recs.to_csv(index=False).encode("utf-8"),"lumora_recommendations.csv","text/csv")
    if not active_customers.empty:
        st.download_button("Download active customer data CSV",active_customers.to_csv(index=False).encode("utf-8"),"lumora_active_dataset.csv","text/csv")
    report_lines=[
        "LUMORA DECISION INTELLIGENCE — ANALYTICAL SUMMARY",
        f"Data source: {source_note}",
        " ",
        "IMPORTANT: Case baseline and customer sample are illustrative/synthetic where identified in the source workbook.",
        " ",
        "BANK BASELINE SNAPSHOT",
    ]
    for k,v in kpis.items():
        report_lines.append(f"{k}: {v}")
    report_lines += [" ","READINESS DISTRIBUTION"]
    if not readiness.empty and "Readiness band" in readiness:
        for k,v in readiness["Readiness band"].value_counts().items():
            report_lines.append(f"{k}: {v}")
    report_lines += [" ","SEGMENT RECOMMENDATIONS"]
    for _,r in recs.iterrows():
        report_lines.append(f"{r.get('Segment')}: {r.get('Recommended action')}")
    report_text="\n".join(report_lines)
    st.download_button("Download analytical summary (TXT)",report_text.encode("utf-8"),"lumora_analytical_summary.txt","text/plain")
    st.subheader("Experiment and impact measurement plan")
    st.dataframe(experiment_kpis(),use_container_width=True,hide_index=True)

# ---------------- Page: Methodology ----------------
elif page == "Methodology & Governance":
    hero("Methodology & governance", "Understand how Lumora produces insights, where the limitations are and how customer harm is avoided.", "LUMORA / TRUST & CONTROL")
    st.subheader("Analytical methods")
    methods=pd.DataFrame([
        ["Descriptive","KPIs, distributions, segment profiles, product penetration","Implemented"],
        ["Diagnostic","Correlation matrix, segment comparisons, cross-tab exploration","Implemented"],
        ["Segmentation","Case-defined segments and sample profiles; clustering can be added after validation","Partially implemented"],
        ["Readiness screening","Transparent liquidity, confidence and horizon rules","Implemented as educational screen"],
        ["Predictive","Logistic regression / tree models require historical labelled outcomes","Not claimed as validated"],
        ["Prescriptive","Segment actions and rule-based next-best actions","Implemented"],
        ["Scenario","Savings, inflation, real purchasing power and hypothetical return sensitivity","Implemented"],
        ["Experimentation","A/B test design and outcome/guardrail framework","Design included; requires live experiment data"],
    ],columns=["Approach","Techniques","Status"])
    st.dataframe(methods,use_container_width=True,hide_index=True)
    st.subheader("3–5 year implementation roadmap")
    roadmap=pd.DataFrame([
        ["Year 1","Pilot inflation education and liquidity planner","Comprehension, completion, complaints, opt-outs"],
        ["Year 2","Expand suitability and adviser-assist journeys","Suitability review coverage, trust, resolution time"],
        ["Year 3","Introduce goal buckets and controlled recurring plans","Informed adoption, continuation, opt-outs"],
        ["Years 4–5","Optimise using cohort and experiment evidence","Retention, customer outcomes, fairness, harm indicators"],
    ],columns=["Period","Initiative","Measures"])
    st.dataframe(roadmap,use_container_width=True,hide_index=True)
    st.subheader("Governance guardrails")
    for item in [
        "Obtain consent before marketing or personalised investment journeys.",
        "Disclose fees, product risks, liquidity restrictions and conflicts clearly.",
        "Escalate complex or uncertain cases to qualified human advisers.",
        "Never automatically execute investments or switch portfolios.",
        "Use data minimisation, role-based access, retention limits and audit logs.",
        "Monitor complaints, opt-outs, unsuitable recommendations and outcome disparities.",
    ]:
        insight(item)
    insight("The supplied case workbook contains illustrative baseline metrics and synthetic customer/research data. It is not evidence of actual Lumora customer behaviour.", warning=True)

st.markdown("<div style='text-align:center;color:#7893a8;font-size:11px;padding:28px 0 8px'>LUMORA DECISION INTELLIGENCE · Educational case prototype · Not investment advice</div>",unsafe_allow_html=True)
