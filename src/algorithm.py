#Algorithm for stock analysis

score = 0

# Profitability
if net_margin.mean() > 0.1: score += 1
if roe.mean() > 0.15: score += 1
if roic.mean() > 0.10: score += 1

# Growth
if revenue_growth_yoy.mean() > 0.10: score += 1
if eps_growth.mean() > 0.10: score += 1

# Debt
if de_ratio.mean() < 1.0: score += 1

# Cash Flow
if fcf.mean() > 0: score += 1
if fcf_yield.mean() > 0.05: score += 1

# Valuation
if meta.info.get("trailingPE", 999) < 25: score += 1

if score >= 6:
    print("✅ Likely a strong investment candidate")
elif 3 <= score < 6:
    print("⚖️ Neutral / needs more analysis")
else:
    print("❌ Likely a weak investment candidate")