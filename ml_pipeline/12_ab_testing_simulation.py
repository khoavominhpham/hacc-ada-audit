import csv

INPUT_CSV = "ml_pipeline/data/hacc_empirical_audit.csv"

# Standard manual editorial time estimates (in minutes)
TIME_PER_HEADING_FIX = 2    
TIME_PER_ALT_TEXT = 3       
TIME_PER_PARAGRAPH = 10     

# AI-Assisted time estimate
TIME_PER_AI_AUTO_FIX = 0.25 

def run_roi_benchmark():
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        pages = list(csv.DictReader(f))

    total_skips = sum(int(p["heading_skips"]) for p in pages)
    total_bad_alt = sum(int(p["missing_or_weak_alt"]) for p in pages)
    total_dense = sum(int(p["exceeds_grade_9"]) for p in pages)
    pages_with_violations = sum(1 for p in pages if int(p["total_violations"]) > 0)

    # Calculate Manual Hours
    manual_mins = (total_skips * TIME_PER_HEADING_FIX) + \
                  (total_bad_alt * TIME_PER_ALT_TEXT) + \
                  (total_dense * TIME_PER_PARAGRAPH)
    manual_hours = manual_mins / 60

    # Calculate AI Hours
    ai_mins = pages_with_violations * TIME_PER_AI_AUTO_FIX
    ai_hours = ai_mins / 60

    reduction_pct = ((manual_hours - ai_hours) / manual_hours) * 100

    print("==========================================================")
    print("📈 HACC WORKFLOW A/B SIMULATION: MANUAL VS. AI-ASSISTED")
    print("==========================================================")
    print(f"Sample Size: {len(pages)} Real Pages")
    print(f"Total Defects to Fix: {total_skips} Headings, {total_bad_alt} Alt-Texts, {total_dense} Dense Pages")
    print("-" * 58)
    print(f"Traditional Manual Workflow: {manual_hours:.1f} Hours")
    print(f"AI-Assisted Auto-Apply:      {ai_hours:.1f} Hours")
    print("-" * 58)
    print(f"Time Reduction:              {reduction_pct:.1f}%")
    print(f"Labor Saved per 100 Pages:   {manual_hours - ai_hours:.1f} Hours")
    
    # Extrapolate for the Final Report
    extrapolated_savings = (manual_hours - ai_hours) * 50 
    print(f"\n🚀 Projected Extrapolation for 5,000 Page CMS Migration:")
    print(f"Total Projected Savings:     {extrapolated_savings:,.0f} Labor Hours")

if __name__ == "__main__":
    run_roi_benchmark()