# Value Investment Dashboard [Streamlit Host](https://valueinvest.streamlit.app)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://valueinvest.streamlit.app)

```bash
# git clone this repo, then
pip install streamlit yfinance pandas numpy plotly
streamlit run app.py
```

A comprehensive personal dashboard for value investment analysis, supporting stocks from global markets through Yahoo Finance integration.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
   - [Step 1: Enter Your Ticker Symbol](#step-1-enter-your-ticker-symbol)
   - [Step 2: Click "Run" and Review Results](#step-2-click-run-and-review-results)
   - [Step 3: Adjust Parameters for Scenario Analysis](#step-3-adjust-parameters-for-scenario-analysis-optional)
   - [Step 4: Generate Your AI Analyst Report](#step-4-generate-your-ai-analyst-report)
2. [Tab Guide](#tab-guide)
   - [Manual Tab](#manual-tab-you-are-here)
   - [Overview Tab](#overview-tab)
   - [Data Points Tab](#data-points-tab)
   - [Valuation Tab](#valuation-tab)
   - [Evaluation Tab](#evaluation-tab)
   - [Prompts Tab](#prompts-tab)
3. [Understanding Valuation Parameters](#understanding-valuation-parameters)
   - [Auto-Calculated Parameters](#auto-calculated-parameters)
   - [When to Override Parameters](#when-to-override-parameters)
4. [Limitations & Important Notes](#limitations--important-notes)
   - [Data Limitations](#data-limitations)
   - [Model Limitations](#model-limitations)
   - [Interpretation Guidance](#interpretation-guidance)
5. [Disclaimers](#disclaimers)
   - [Not Financial Advice](#not-financial-advice)
   - [User Responsibility](#user-responsibility)
   - [No Guarantees](#no-guarantees)
   - [Data Sources Disclaimer](#data-sources-disclaimer)
6. [Yahoo Finance Ticker Format Reference](#yahoo-finance-ticker-format-reference)
   - [How Tickers Work](#how-tickers-work)
   - [Regional Ticker Guide](#regional-ticker-guide)
   - [Tips for Finding Tickers](#tips-for-finding-tickers)
   - [Common Issues](#common-issues)

---

## Quick Start Guide

### Step 1: Enter Your Ticker Symbol
Type a stock ticker in the sidebar text field:
- **US stocks:** AAPL, MSFT, GOOGL, etc.
- **Non-US stocks:** Use Yahoo Finance format (see regional reference below)
  - Japan: `9697.T` | Hong Kong: `0700.HK` | London: `ULVR.L` | Poland: `CDR.WA`
  - See [Yahoo Finance Ticker Format Reference](#yahoo-finance-ticker-format-reference) for more examples.

[↑ Return to Table of Contents](#table-of-contents)

---

### Step 2: Click "Run" and Review Results
The system will:
- Fetch 10 years of price data and financial statements
- Auto-calculate valuation parameters from historical data
- Run 7 valuation methods and 30+ investment criteria
- Display comprehensive analysis across all tabs

**Navigate through the tabs to explore:**
- Overview: Visual summary and key metrics
- Data Points: Raw financial data
- Valuation: Detailed fair value calculations
- Evaluation: Investment criteria assessment

[↑ Return to Table of Contents](#table-of-contents)

---

### Step 3: Adjust Parameters for Scenario Analysis (Optional)
**Purpose:** Test different assumptions to see how fair value changes

**In the sidebar, expand "Valuation Parameters":**
- **For conservative estimates:** Increase discount rate (+1-2%), decrease growth rate
- **For optimistic estimates:** Decrease discount rate, increase growth rate
- **For what-if scenarios:** Adjust any parameter and click "Run" again

The system auto-calculates parameters, but you can override any value to reflect your own judgment or test sensitivity.

[↑ Return to Table of Contents](#table-of-contents)

---

### Step 4: Generate Your AI Analyst Report
**Get a comprehensive equity research report written by AI:**

Example report:
- FIVN: [Gemini 2.5 Flash](https://g.co/gemini/share/644f7b7cf0b5)
- FIVN: [Claude 4.5 Sonnet](https://claude.ai/share/a4780e70-bf12-4a2a-b484-2802ca53e6d9)
- CPRX: [Gemini 2.5 Flash](https://g.co/gemini/share/45158ac2bf0d)
- CPRX: [Claude 4.5 Sonnet](https://claude.ai/share/a4780e70-bf12-4a2a-b484-2802ca53e6d9)
- INMB: [Gemini 2.5 Flash](https://g.co/gemini/share/076cdc65f4aa)

1. **Find recent fiscal reports online:**
   - Search: `[Company Name] 10-K SEC filing` or `[Company Name] annual report investor relations`
   - Copy the URL of the most recent 10-K (annual) or 10-Q (quarterly) report

2. **Add URLs to the app:**
   - In the sidebar, expand "Fiscal Report URLs (Optional)"
   - Paste the 10-K URL (annual report)
   - Paste the 10-Q URL (quarterly report) if available
   - Add any other relevant documents (investor presentations, proxy statements)

3. **Generate the prompt:**
   - Click "Generate Prompt" button in the sidebar
   - Switch to the "Prompts" tab
   - Copy the entire prompt text

4. **Get your AI report:**
   - Paste the prompt into Claude 4.5 Sonnet > Gemini 2.5 Pro/Flash > GPT-5
   - Enable "deep thinking" or "reasoning" mode if available
   - Enable web search for latest news context
   - The AI will generate a detailed investment report with:
     - Executive summary with Buy/Hold/Sell recommendation
     - Financial analysis and valuation discussion
     - Risk assessment and catalysts
     - Target price with upside/downside scenarios

[↑ Return to Table of Contents](#table-of-contents)

---

## Tab Guide

### Manual Tab (You Are Here)
**Purpose:** Instructions and reference guide

This tab is always visible, even before loading data. Refer back here anytime you need help.

[↑ Return to Table of Contents](#table-of-contents)

---

### Overview Tab
**Purpose:** Quick investment snapshot for rapid screening

**What's included:**
- **Historical Price Chart:** 10-year monthly price trend to visualize momentum
- **Fair Value Table:** 7 valuation methods ranked by upside potential
  - Shows current price vs. fair value estimates
  - Upside % indicates potential gain/loss
- **Evaluation Snowflakes (Radar Chart):** Visual scores across 6 dimensions
  - Past, Present, Future, Health, Dividend, Macroeconomics
  - Larger area = stronger overall profile
- **Evaluation Checklist:** Top 6 criteria per dimension with ✅/❌ indicators
- **Key Ratios:** Essential metrics (P/E, ROE, debt ratios, margins)
- **News:** Recent company headlines
- **Officers:** Management team
- **About:** Company description and business overview

[↑ Return to Table of Contents](#table-of-contents)

---

### Data Points Tab
**Purpose:** Access raw financial data and historical trends

**Sections:**

1. **Basic Information**
   - Market cap, enterprise value, shares outstanding
   - Current valuation ratios (P/E, P/B, P/S)
   - Profitability metrics (ROE, ROA, margins)

2. **Time Series: Financial Points**
   - Income statement, balance sheet, cash flow items
   - Shows latest 5 reporting periods
   - Raw data from financial statements

3. **Time Series: Derived Metrics**
   - Calculated ratios and growth rates
   - Year-over-year changes
   - Trend indicators

4. **Time Series: Dividend Metrics** (if applicable)
   - Dividend history, yield, payout ratio
   - May show different date ranges than other metrics

[↑ Return to Table of Contents](#table-of-contents)

---

### Valuation Tab
**Purpose:** Understand how fair value is calculated

**7 Valuation Methods:**

Each method shows full transparency:
- **Overview:** What the method does and when it works best
- **Step-by-Step Calculation:** Follow the math with actual company data
- **Formulas:** LaTeX equations with variable definitions
- **Final Fair Value:** Per-share intrinsic value estimate

**Methods available:**
1. **P/E Multiple Method** - Projects earnings, applies industry P/E
2. **DCF One-Stage** - Free cash flow with declining growth
3. **DCF Two-Stage** - High growth → suitable for companies that do not necessarily grow at a constant rate over time. They tend to be high-growth initially, and become stable after a couple of years.
4. **Dividend Discount Model** - Best for companies with long streak of stable/increasing dividend payout
5. **ROE Capitalization** - Book value growth approach
6. **Residual Income** - Excess returns above cost of equity, best for financial companies such as banks and insurance, generally do not have a significant proportion of physical assets, and face different regulatory requirements for cash holdings.
7. **Graham Number** - Benjamin Graham's conservative formula

**How to use:** 
- If most methods agree → higher confidence in fair value range
- If methods diverge widely → dig into assumptions
- Click each expander to see detailed calculations

[↑ Return to Table of Contents](#table-of-contents)

---

### Evaluation Tab
**Purpose:** Systematic assessment of investment quality

**6 Evaluation Dimensions:**

1. **Past Performance** - Historical growth and consistency
2. **Present Fundamentals** - Current profitability and valuation
3. **Future Momentum** - Forward growth indicators
4. **Financial Health** - Balance sheet strength and leverage
5. **Dividend Quality** - Payout sustainability (if applicable)
6. **Macroeconomic Context** - Interest rates, GDP, currency trends

**Each criterion shows:**
- ✅ Pass or ❌ Fail status
- Description of what it measures
- Specific criteria threshold
- Input data used (with dates)
- Calculation methodology

**How to use:** 
- 5-6 passes per dimension = strong
- 3-4 passes = moderate
- 0-2 passes = weak or needs investigation

[↑ Return to Table of Contents](#table-of-contents)

---

### Prompts Tab
**Purpose:** Generate AI-ready prompt for equity research report

**What's included in the prompt:**
- Complete company overview
- All fair value estimates with calculations
- All evaluation criteria results
- Financial data tables
- Links to fiscal reports you provided

**How to use:** See Step 4 in Quick Start Guide above.

[↑ Return to Table of Contents](#table-of-contents)

---

## Understanding Valuation Parameters

### Auto-Calculated Parameters
The system calculates parameters from historical data and market conditions:

- **Discount Rate:** From CAPM (risk-free rate + beta × equity risk premium)
- **Growth Rate:** From 3-5 year historical CAGR
- **Terminal Growth Rate:** From long-run GDP + inflation (~2-3%)
- **Risk-Free Rate:** Current 10-year Treasury yield

[↑ Return to Table of Contents](#table-of-contents)

---

### When to Override Parameters

**For Conservative Valuation:**
- Increase discount rate by 1-3%
- Decrease growth rate by 20-30%
- Increase margin of safety from 25% to 33% or higher
- Use shorter projection periods

**For Optimistic Valuation:**
- Decrease discount rate (if you believe risk is overstated)
- Increase growth rate based on industry tailwinds
- Extend projection periods for high-quality compounders

**For Sensitivity Analysis:**
- Test how fair value changes with different growth assumptions
- See impact of discount rate on DCF valuations
- Adjust margin of safety based on conviction level

**Parameter Definitions:**

| Parameter | What It Is | Typical Range |
|-----------|------------|---------------|
| Discount Rate | Required return reflecting risk | 8-15% |
| Growth Rate | Expected annual growth | 5-20% |
| Decline Rate | How much growth decays/year | 5-15% |
| Terminal Growth | Perpetual growth rate | 2-3% |
| Margin of Safety | Discount for conservatism | 15-35% |
| Years (Stage 1) | High growth period | 3-7 years |
| Years (Stage 2) | Transition period | 3-7 years |

**After adjusting:** Click "Run" to recalculate all valuations with new parameters.

[↑ Return to Table of Contents](#table-of-contents)

---

## Limitations & Important Notes

### Data Limitations
- **Historical bias:** Valuations based on past financial data
- **No forward guidance:** Does not include management guidance or analyst estimates  
- **API dependencies:** Relies on Yahoo Finance and World Bank data accuracy
- **Missing data:** Some international stocks may have incomplete macro data

[↑ Return to Table of Contents](#table-of-contents)

---

### Model Limitations
- **Simplification:** All models are simplified representations of reality
- **Assumption sensitivity:** Small changes in parameters can significantly impact fair value
- **Method applicability:** Not all methods work for all companies:
  - Dividend models require stable dividends
  - Graham Number requires positive earnings and book value
  - Startup/Growth companies may not fit value-oriented models

[↑ Return to Table of Contents](#table-of-contents)

---

### Interpretation Guidance
- **Fair value is a range, not a precise number**
- **Multiple methods provide confidence intervals**
- **Always verify key assumptions make economic sense**
- **Cross-reference with qualitative factors (moat, management, industry trends)**

[↑ Return to Table of Contents](#table-of-contents)

---

## Disclaimers

### Not Financial Advice
This tool is designed for **educational and research purposes only**. It is NOT:
- Financial, investment, or tax advice
- A recommendation to buy, sell, or hold any security
- A substitute for professional financial guidance
- Suitable as the sole basis for investment decisions

[↑ Return to Table of Contents](#table-of-contents)

---

### User Responsibility
You are responsible for:
- Verifying all data and calculations independently
- Conducting additional due diligence
- Understanding the risks of equity investing
- Consulting qualified financial professionals before investing
- Complying with all applicable securities laws and regulations

[↑ Return to Table of Contents](#table-of-contents)

---

### No Guarantees
- **Past performance does not guarantee future results**
- **Valuation estimates are subject to significant uncertainty**
- **Market prices may diverge from calculated fair values indefinitely**
- **The tool developers assume no liability for investment outcomes**

[↑ Return to Table of Contents](#table-of-contents)

---

### Data Sources Disclaimer
- Price data from Yahoo Finance (15-20 minute delay)
- Company information from Yahoo Finance
- Macroeconomic data from World Bank API
- Data accuracy and completeness not guaranteed

**By using this tool, you acknowledge that you understand these limitations and disclaimers.**

[↑ Return to Table of Contents](#table-of-contents)

---

## Yahoo Finance Ticker Format Reference

### How Tickers Work
Yahoo Finance uses **suffixes** to identify exchanges for non-US stocks:
- Format: `TICKER.SUFFIX`
- Example: `0700.HK` (Tencent on Hong Kong Stock Exchange)

[↑ Return to Table of Contents](#table-of-contents)

---

### Regional Ticker Guide

#### Asia-Pacific

| Country/Region | Suffix | Example | Company |
|---------------|--------|---------|---------|
| **Australia** | .AX | BHP.AX | BHP Group |
| **China (Shanghai)** | .SS | 600519.SS | Kweichow Moutai |
| **China (Shenzhen)** | .SZ | 000858.SZ | Wuliangye |
| **Hong Kong** | .HK | 0700.HK | Tencent |
| **India (NSE)** | .NS | RELIANCE.NS | Reliance Industries |
| **India (BSE)** | .BO | RELIANCE.BO | Reliance Industries |
| **Indonesia** | .JK | BBRI.JK | Bank Rakyat |
| **Japan** | .T | 9697.T | Capcom |
| **South Korea** | .KS or .KQ | 005930.KS | Samsung Electronics |
| **Malaysia** | .KL | MAYBANK.KL | Malayan Banking |
| **New Zealand** | .NZ | FPH.NZ | Fisher & Paykel |
| **Philippines** | .PS | BDO.PS | BDO Unibank |
| **Singapore** | .SI | D05.SI | DBS Group |
| **Taiwan** | .TW | 2330.TW | TSMC |
| **Thailand** | .BK | KBANK.BK | Kasikornbank |
| **Vietnam** | .VN | VNM.VN | Vinamilk |

#### Europe

| Country/Region | Suffix | Example | Company |
|---------------|--------|---------|---------|
| **Austria** | .VI | VOE.VI | Voestalpine |
| **Belgium** | .BR | ABI.BR | AB InBev |
| **Denmark** | .CO | NOVO-B.CO | Novo Nordisk |
| **Finland** | .HE | NOKIA.HE | Nokia |
| **France** | .PA | MC.PA | LVMH |
| **Germany (Xetra)** | .DE | SAP.DE | SAP |
| **Germany (Frankfurt)** | .F | SAP.F | SAP |
| **Greece** | .AT | OPAP.AT | OPAP |
| **Ireland** | .IR | CRH.IR | CRH |
| **Italy** | .MI | ISP.MI | Intesa Sanpaolo |
| **Netherlands** | .AS | ASML.AS | ASML |
| **Norway** | .OL | EQNR.OL | Equinor |
| **Poland** | .WA | CDR.WA | CD Projekt |
| **Portugal** | .LS | EDP.LS | EDP |
| **Russia** | .ME | GAZP.ME | Gazprom |
| **Spain** | .MC | TEF.MC | Telefónica |
| **Sweden** | .ST | VOLV-B.ST | Volvo |
| **Switzerland** | .SW | NESN.SW | Nestlé |
| **Turkey** | .IS | THYAO.IS | Turkish Airlines |
| **UK (London)** | .L | ULVR.L | Unilever |

#### Americas (Non-US)

| Country/Region | Suffix | Example | Company |
|---------------|--------|---------|---------|
| **Argentina** | .BA | GGAL.BA | Grupo Financiero Galicia |
| **Brazil** | .SA | PETR4.SA | Petrobras |
| **Canada (TSX)** | .TO | SHOP.TO | Shopify |
| **Canada (TSXV)** | .V | Example.V | Various |
| **Chile** | .SN | SQM-B.SN | SQM |
| **Mexico** | .MX | WALMEX.MX | Walmart de México |

#### Middle East & Africa

| Country/Region | Suffix | Example | Company |
|---------------|--------|---------|---------|
| **Egypt** | .CA | COMI.CA | Commercial International Bank |
| **Israel** | .TA | TEVA.TA | Teva Pharmaceutical |
| **Qatar** | .QA | QNBK.QA | QNB |
| **Saudi Arabia** | .SAU | 2222.SAU | Saudi Aramco |
| **South Africa** | .JO | NPN.JO | Naspers |
| **UAE** | .AD or .DU | FAB.AD | First Abu Dhabi Bank |

#### United States
**No suffix needed** - just use the ticker symbol:
- AAPL (Apple)
- MSFT (Microsoft)  
- GOOGL (Alphabet)
- TSLA (Tesla)

[↑ Return to Table of Contents](#table-of-contents)

---

### Tips for Finding Tickers
1. **Search Yahoo Finance directly:** Go to finance.yahoo.com and search the company name
2. **Use the format guide above:** Match country to suffix

[↑ Return to Table of Contents](#table-of-contents)

---

### Common Issues
- **"No price data returned":** Wrong suffix or ticker doesn't exist on Yahoo Finance
- **ADRs vs. local:** For US-listed foreign stocks, no suffix needed (e.g., BABA for Alibaba ADR)

[↑ Return to Table of Contents](#table-of-contents)

---