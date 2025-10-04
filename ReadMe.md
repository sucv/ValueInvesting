# Value Investment Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://valueinvest.streamlit.app)

A comprehensive personal dashboard for value investment analysis, supporting stocks from global markets through Yahoo Finance integration.

## 🎯 Overview

This dashboard provides professional-grade value investment analysis tools accessible to individual investors. It combines multiple valuation models, fundamental analysis metrics, and macroeconomic indicators to help you make informed investment decisions across international markets.

## 🙏 Acknowledgments

This project builds upon excellent resources from the investment community:

- **[yfinance](https://github.com/ranaroussi/yfinance)** - Free Python library for accessing international market data
- **World Bank API** - Macroeconomic evaluation metrics
- **[SimplyWallSt](https://simplywall.st/dashboard)** - Inspiration for the elegant snowflake chart visualization ([GitHub](https://github.com/SimplyWallSt/Company-Analysis-Model))
- **Educational Resources:**
  - [Value Investing Bootcamp: How to Invest Wisely](https://www.udemy.com/course/value-investing-bootcamp-how-to-invest-wisely/) (Udemy)
  - [The Complete Financial Analyst Training & Investing Course](https://www.udemy.com/course/the-complete-financial-analyst-training-and-investing-course) (Udemy)
- **Data Validation:** [GuruFocus](https://www.gurufocus.com/) and [Morningstar](https://www.morningstar.com/)
- **Development Support:** ChatGPT for code optimization

## 🚀 Quick Start

### Installation

```bash
pip install streamlit yfinance pandas numpy plotly
```

### Running the Application

```bash
streamlit run app.py
```

## 📊 Standard Workflow

### 1. **Discover Investment Opportunities**
   - Use screeners like [Yahoo Finance Screener](https://finance.yahoo.com/research-hub/screener/) with your preferred criteria (P/E ratio, market cap, 52-week performance, etc.)
   - Or analyze specific stocks that catch your interest

### 2. **Find the Correct Stock Symbol**
   - **US Stocks:** Use the ticker symbol directly (e.g., `AAPL`, `GOOGL`)
   - **International Stocks:** Include the exchange suffix
     - Tokyo Stock Exchange: `.T` (e.g., `7203.T` for Toyota)
     - Shanghai Stock Exchange: `.SS` (e.g., `600000.SS`)
     - Search on [Yahoo Finance](https://finance.yahoo.com/) to find the correct symbol

### 3. **Analyze the Stock**
   - Enter the symbol and click "Run"
   - Review the comprehensive visualizations and metrics
   - Adjust valuation parameters based on your investment thesis
   - If the stock price is still substantially lower than the estimated fair prices under "unrealistically strict" parameters (e.g., a 2% growth rate), it might be an investment opportunity.

### 4. **Generate AI-Powered Reports** (Optional)
   - Locate the latest 10-K or 10-Q reports from the company's investor relations page
   - Add the PDF URLs to the "Fiscal Report URLs" field
   - Click "Generate Prompt"
   - Use the prompt with your preferred AI assistant (Gemini 2.5 Pro/Flash recommended)
   - Enable reasoning and web search for comprehensive analysis
   - 

## 💡 Valuation Models

The dashboard employs seven industry-standard valuation models:

1. **Price Earnings Multiple (PEM)** - Relative valuation based on earnings
2. **1-Stage Discounted Cash Flow (DCF-1)** - Single-stage growth DCF model
3. **2-Stage Discounted Cash Flow (DCF-2)** - Two-stage growth DCF model
4. **Return on Equity (ROE)** - Profitability-based valuation
5. **2-Stage Discounted Dividend Model (DDM)** - Dividend-focused valuation
6. **Excess Return (ER)** - Economic value added approach
7. **Graham Number (GN)** - Benjamin Graham's value formula

> Detailed formulas available in `constants.py` under the `VALUATION` variable

## ✅ Comprehensive Evaluation Framework

Stocks are evaluated across six dimensions:

- **Past Performance** - Historical growth and consistency
- **Current Position** - Present financial key ratios
- **Future Prospects** - The recent financial momentum vs average yearly growth
- **Financial Health** - Balance sheet strength and risk metrics
- **Dividend Policy** - Dividend streak and stability
- **Macroeconomic Context** - Economic environment and region trends

When fiscal report URLs are provided, a seventh dimension is added:
- **Qualitative Analysis** - AI-powered assessment of business strategy, competitive advantages, and management quality

> Evaluation criteria details in `evaluation.py` under the `CRITERION` variable

## 📚 Understanding Value Investing

New to value investing? Start with the [fundamental concepts](https://en.wikipedia.org/wiki/Value_investing) pioneered by Benjamin Graham and Warren Buffett.

## ⚠️ Disclaimer

This dashboard is provided strictly for **educational and informational purposes** and does not constitute financial, investment, legal, tax, or other professional advice. It is not a recommendation or solicitation to buy or sell any security.

**Important Notice:**
- Data and calculations may be incomplete, delayed, or inaccurate
- All content is provided "as is" without warranties of any kind
- You are solely responsible for your investment decisions
- Past performance does not indicate future results
- Investing involves risk, including possible loss of principal

The developers, contributors, and affiliates disclaim all liability for any damages arising from the use of this dashboard. **Always consult a licensed financial professional before making investment decisions.**

---

*By using this dashboard, you acknowledge and agree to these terms.*