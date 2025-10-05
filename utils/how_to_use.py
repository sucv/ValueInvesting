# utils/how_to_use.py

MANUAL_CONTENT = """
# Value Investing Dashboard - User Manual

## Getting Started

### 1. Enter a Ticker Symbol
- Type a valid stock ticker in the sidebar (e.g., AAPL, MSFT, GOOGL)
- For non-US stocks, use Yahoo Finance format:
  - Japan: `9697.T`
  - Hong Kong: `0700.HK`
  - London: `ULVR.L`
  - Poland: `CDR.WA`

### 2. Click "Run"
The system will:
- Fetch stock data from Yahoo Finance
- Calculate valuation parameters automatically
- Run investment criteria evaluation
- Generate fair value estimates using 7 different methods

---

## Understanding the Tabs

### Overview Tab
**Purpose:** Quick snapshot of the company's investment profile

**What you'll see:**
- **Price Chart:** 10-year historical price trend (monthly)
- **Fair Value Table:** 7 valuation methods ranked by upside potential
- **Evaluation Snowflakes:** Radar chart showing scores across 6 dimensions (Past, Present, Future, Health, Dividend, Macro)
- **Checklist:** Top 6 criteria per dimension with pass/fail indicators
- **Key Ratios:** Important financial metrics
- **News:** Recent company news
- **Officers:** Management team
- **About:** Company description

---

### Data Points Tab
**Purpose:** Raw financial data and historical trends

**Sections:**
1. **Basic Information:** Core metrics like market cap, P/E ratio, dividend yield
2. **Financial Points:** Historical income statement, balance sheet, and cash flow data (latest 5 periods)
3. **Derived Metrics:** Calculated ratios and growth rates
4. **Dividend Metrics:** Separate table for dividend-related data (may have different date ranges)

---

### Valuation Tab
**Purpose:** Detailed valuation methodology and calculations

**7 Methods Available:**
1. **P/E Multiple Method:** Projects earnings with growth, applies median P/E, discounts to present
2. **DCF One-Stage:** Free cash flow with declining growth rate
3. **DCF Two-Stage:** High growth phase → stable growth phase → terminal value
4. **Dividend Discount Model:** Two-stage dividend projection (best for dividend payers)
5. **ROE Capitalization:** Projects book value and dividends, capitalizes terminal earnings
6. **Residual Income (Excess Return):** Values excess returns above cost of equity
7. **Graham Number:** Benjamin Graham's conservative formula (√22.5 × EPS × BVPS)

**Each method shows:**
- Overview and when it works best
- Step-by-step calculation with actual data
- Input parameters
- LaTeX formulas with variable explanations
- Final fair value per share

---

### Evaluation Tab
**Purpose:** Systematic investment criteria assessment across 6 dimensions

**Dimensions:**
1. **Past Performance:** Historical growth trends (revenue, earnings, FCF)
2. **Present Fundamentals:** Current profitability, valuation, competitive position
3. **Future Momentum:** Growth indicators and forward-looking metrics
4. **Financial Health:** Balance sheet strength, leverage, liquidity
5. **Dividend Quality:** Payout sustainability and track record
6. **Macroeconomic Context:** Interest rates, GDP growth, currency trends

**Each criterion shows:**
- Pass/Fail status (✅/❌)
- Description of what it measures
- Criteria threshold
- Input data used (with fancy metric names)
- Results and methodology

---

### Prompts Tab
**Purpose:** Generate AI-ready prompt for equity research report

**How to use:**
1. Optionally add fiscal report URLs (10-K, 10-Q, extra documents)
2. Click "Generate Prompt"
3. Copy the entire prompt text
4. Paste into an AI with reasoning capability (Gemini 2.5 Pro recommended)
5. Enable web search and deep thinking modes
6. The AI will generate a comprehensive equity research report

**Prompt includes:**
- All data from Overview, Data Points, Valuation, and Evaluation tabs
- Structured instructions for the AI
- Expected report format (Buy/Hold/Sell rating with target price)

---

## Adjusting Valuation Parameters

### When to Adjust
The system auto-calculates parameters, but you may want to adjust them to:
- Test sensitivity to different assumptions
- Reflect your own views on growth or risk
- Match specific industry characteristics

### Parameters Explained

**In the sidebar under "Valuation Parameters":**

1. **Discount Rate (r):** 
   - What it is: Required return reflecting risk
   - Auto-calculated from: CAPM (risk-free rate + beta × equity risk premium)
   - Typical range: 8-15%

2. **Growth Rate (g):**
   - What it is: Expected revenue/earnings growth rate
   - Auto-calculated from: Historical 3-5 year CAGR
   - Typical range: 5-20% for growth companies

3. **Growth Decline Rate (d):**
   - What it is: How much growth decays each year
   - Auto-calculated from: Conservative assumption
   - Typical range: 5-15% per year

4. **Terminal Growth Rate:**
   - What it is: Perpetual growth rate after projection period
   - Auto-calculated from: Long-run GDP + inflation
   - Typical range: 2-3%

5. **Margin of Safety:**
   - What it is: Discount applied to fair value for conservatism
   - Default: 25%
   - Adjust based on conviction level

6. **Projection Years (Stage 1 & 2):**
   - Stage 1: High growth phase (default 5 years)
   - Stage 2: Transition phase (default 5 years)

7. **Risk-Free Rate:**
   - What it is: Return on "risk-free" government bonds
   - Auto-set to: Current 10-year Treasury yield
   - Typical range: 3-5%

8. **Average Market Return:**
   - What it is: Historical equity market return
   - Default: ~10% (used in CAPM)

**After adjusting:** Click "Run" again to recalculate valuations

---

## Interpreting Results

### Fair Value Upside/Downside
- **>20% upside:** Potentially undervalued (consider Buy)
- **-10% to +20%:** Fairly valued (consider Hold)
- **<-10% downside:** Potentially overvalued (consider Sell)

### Evaluation Scores
- **5-6 passed:** Strong on that dimension
- **3-4 passed:** Average
- **0-2 passed:** Weak on that dimension

### Method Agreement
- **Most methods agree:** Higher confidence in fair value range
- **Wide dispersion:** Signals uncertainty; dig deeper into assumptions

---

## Tips for Best Results

1. **Use multiple tickers:** Compare valuations across peers
2. **Check data quality:** Verify key metrics make sense (no obvious errors)
3. **Read the "When This Works Best":** Each valuation method has limitations
4. **Cross-reference with filings:** Use the prompt + actual 10-K/10-Q for best AI reports
5. **Sanity check:** If fair value seems extreme, review parameter assumptions

---

## Troubleshooting

**"No price data returned"**
- Check ticker symbol spelling
- For non-US stocks, ensure correct Yahoo Finance suffix
- Some delisted or very small companies may not have data

**"Failed to fetch or compute"**
- Temporary API issue - try again in a few seconds
- For certain countries, World Bank data may be unavailable

**Valuation seems way off**
- Check if company is profitable (some methods require positive earnings/FCF)
- Verify currency and share count consistency
- Adjust parameters if auto-calculated values seem unreasonable

**Evaluation criteria all fail**
- May indicate distressed company or data quality issue
- Check if company is in turnaround phase (historical metrics poor)

---

## Data Sources

- **Price Data:** Yahoo Finance (yfinance library)
- **Company Info:** Yahoo Finance (sector, industry, officers, news)
- **Macroeconomic Data:** World Bank API (GDP growth, inflation, interest rates, FX rates)
- **Calculations:** All valuation and derived metrics computed in-app

**Data Freshness:**
- Price data: Real-time (15-20 min delay)
- Financials: Updated quarterly after earnings releases
- Macro data: Updated annually by World Bank

---

## Limitations

1. **Not financial advice:** This tool is for educational and research purposes only
2. **Backward-looking:** Valuations based on historical data and assumptions
3. **Model risk:** All models are simplifications of reality
4. **Data quality:** Relies on accuracy of Yahoo Finance and World Bank data
5. **No forward guidance:** Does not incorporate management guidance or analyst estimates

**Always conduct additional due diligence before making investment decisions.**

---

## Support & Feedback

This is an open-source educational tool. For questions or improvements, please refer to the project repository.
"""