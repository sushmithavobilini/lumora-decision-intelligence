def answer_question(question, page, context=None):
    q = (question or "").lower().strip()
    context = context or {}
    page_text = page or "the platform"
    if any(k in q for k in ["hello","hi","hey","good morning"]):
        return "Hello! I'm Lumora Guide. I can explain the dashboards, analytical methods, readiness rules, scenarios and dataset upload workflow. What would you like to explore?"
    if any(k in q for k in ["inflation","purchasing power","real value","savings value"]):
        return "Open Scenario Simulator. Compare the savings interest assumption with inflation and inspect both the nominal account balance and inflation-adjusted purchasing power. Try changing the time horizon and rates. These are scenarios, not forecasts."
    if any(k in q for k in ["segment","customer group","customer type"]):
        return "Open Customer Intelligence. Compare each segment's sample size, average savings, emergency-fund months, goal horizon and confidence. The segment labels in the case workbook are illustrative and should not be treated as verified bank-wide customer facts."
    if any(k in q for k in ["liquidity","emergency fund","ready to invest","suitability"]):
        return "Open Readiness & Recommendations. The screening prioritises low emergency buffers and high liquidity needs. 'Potentially ready for suitability review' means a qualified review may be appropriate; it is not investment advice or a product recommendation."
    if any(k in q for k in ["correlation","relationship","cause","why"]):
        return "Open Diagnostic Analytics. Review the correlation matrix and segment comparisons. Correlation does not establish causation, and the supplied 120-row customer sample is synthetic."
    if any(k in q for k in ["upload","dataset","excel","csv","new data"]):
        return "Open Dataset Intelligence and upload an Excel or CSV file. The platform will profile missing values, data types, numeric distributions and category counts. Banking-specific recommendations require mapped fields and documented meanings."
    if any(k in q for k in ["predict","machine learning","logistic","random forest","decision tree"]):
        return "Open Predictive Analytics. Select a binary outcome field only if your uploaded dataset has a clearly defined historical label and enough examples of both outcomes. The supplied synthetic sample does not support a validated adoption model. Check for leakage and evaluate held-out performance before interpreting results."
    if any(k in q for k in ["recommend","next step","strategy","future"]):
        counts = context.get("readiness_counts", {})
        if counts:
            total = sum(counts.values()) or 1
            distribution = "; ".join(f"{name}: {count} ({count/total:.0%})" for name, count in counts.items())
            return ("Based on the currently active dataset, the readiness screen shows: " + distribution +
                    ". Prioritise the largest 'Protect liquidity' or 'Educate / adviser support' groups first. " +
                    "Do not treat the screen as a product recommendation; collect missing expenses, debts and goals, then route suitable cases to a qualified review.")
        return "The recommended sequence is: protect liquidity, educate customers about inflation and risk, offer goal-based suitability reviews, and measure informed adoption together with complaints, opt-outs and retention."
    if any(k in q for k in ["report","download","export"]):
        return "Open Reports Centre to download the current customer assessment, segment recommendations, and scenario results as CSV files. A summary can also be exported as a text report."
    if any(k in q for k in ["page","where","navigate","go to"]):
        return f"You are currently viewing {page_text}. Use the left navigation to open Executive Overview, Customer Intelligence, Diagnostic Analytics, Readiness & Recommendations, Scenario Simulator, Dataset Intelligence or Reports Centre."
    return f"I can guide you through {page_text} and the Lumora analysis. Try asking about inflation, customer segments, liquidity, suitability, correlations, dataset uploads or recommendations."
