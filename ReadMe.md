## Overview
[Streamlit Host](https://valueinvest.streamlit.app)

This is my personal dashboard for value investment. It is inspired or built upon the following resources:

- The free Python library `yfinance`for accessing the internatial market data which are usually not free.
- The Worldbank API for the Macroeconomics  evaluation.
- The wonderful Udemy course [Value Investing Bootcamp: How to Invest Wisely](https://www.udemy.com/course/value-investing-bootcamp-how-to-invest-wisely/) and their materials.
- The wonderful Udemy course [The Complete Financial Analyst Training & Investing Course](https://www.udemy.com/course/the-complete-financial-analyst-training-and-investing-course) and their materials.
- The [GuruFocus](https://www.gurufocus.com/) and [Morningstar](https://www.morningstar.com/) for cross-validating my data and valuation results.
- ChatGPT for polishing my code.

## Local Install and Run
```bash
pip install streamlit yfinance pandas numpy plotly
streamlit run app.py 
```

## Standard Workflow

0. Understand what is [Value Investment](https://en.wikipedia.org/wiki/Value_investing).
1. Find the stock you want
   + Via a Screener, e.g., the [Yahoo Finance Screener](https://finance.yahoo.com/research-hub/screener/), with certain criteria you preferred, e.g., PE, market cap, 52-week loser, etc.
   + You happen to be interested on some stocks and want to get a preliminary check.
2. Get the stock's symbol in Yahoo Finance's standards.
    + US stocks are usually the symbol directly
    + Non-us stocks have suffix, for example, stocks from Tokye Stock Exchange (TSE) are usually xxxx.T, with a suffix of `.T`, stocks from Shanghai SE are usually xxxxxx.SS, with a suffix of `.SS`.
    + You may identify the proper suffix by querying your stock in [Yahoo Finance](https://finance.yahoo.com/).
3. Input the symbol and click the Run button. Then enjoy the visualization.
4. (Optional) Tweak the valuation parameters to whatever you see fit.
5. (If you want to generate a report using your AI):
   + Find the latest 10-K or 10-Q pdf urls from the target stock's investor relation page. 
   + Put the url in the Fiscal Report URLs fields.
   + Click Generate Prompt
   + Copy/Paste the prompt to your AI.
   + Enable reasoning and web search (Or even the deep research), and let your AI generate the report.
     + Gemini 2.5 Pro is highly recommended. The report generated is much better than that from GPT5-Thinking (both not using deep research).

## Valuation Models

There are 7 valuation models, including the Price Earning Multiple (PEM), 1-Stage Discounted Cash Flow (DCF-1), 2-Stage Discounted Cash Flow (DCF-2), Return on Equity (ROE), 2-Stage Discounted Dividend Model (DDM), Excess Return (ER), and Graham Number (GN). See in the app or  the `VALUATION` variable from the `constants.py` for formula.

## Evaluation Checklist

The app evaluate a stock from 6 aspects, including Past, Current, Feature, Health, Dividend, and Macroeconomics. If you provided the 10-K/10-Q urls, the 7th aspects shall be evaluated using your AI with the generated prompt. See in the app or the `CRITERION` variable from the `evaluation.py` for actual criteria.


## Disclaimer
This dashboard is provided strictly for educational and informational purposes and does not constitute financial, investment, legal, tax, or other professional advice, a recommendation, or a solicitation to buy or sell any security. Data and calculations may be incomplete, delayed, or inaccurate, and all content is provided on an “as is” and “as available” basis without warranties of any kind. You are solely responsible for your investment decisions and for independently verifying any information before acting. Past performance is not indicative of future results; investing involves risk, including the possible loss of principal. To the fullest extent permitted by applicable law, the developer, contributors, and affiliates disclaim all liability for any direct, indirect, incidental, consequential, or special damages (including trading losses or lost profits) arising from or related to your access to or use of this dashboard. By using this dashboard, you acknowledge and agree to these terms and should consult a licensed financial professional before making any investment decisions.”