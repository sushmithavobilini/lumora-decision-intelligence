
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from lumora.data import load_case_workbook, baseline_dict, normalize_customer_columns
from lumora.analytics import kpi_snapshot, readiness_assessment, segment_summary, correlation_matrix
from lumora.recommendations import segment_recommendations

sheets=load_case_workbook(ROOT/"data"/"Lumora_Case_Workbook.xlsx")
baseline=baseline_dict(sheets)
customers=normalize_customer_columns(sheets["Synthetic Customer Sample"])
ready=readiness_assessment(customers)
assert len(customers)==120
assert round(kpi_snapshot(baseline)["Investment penetration (%)"],1)==18.1
assert len(segment_summary(customers))==6
assert correlation_matrix(customers).shape==(6,6)
assert "Readiness band" in ready
assert len(segment_recommendations(ready))==6
print("LUMORA SMOKE TEST PASSED")
