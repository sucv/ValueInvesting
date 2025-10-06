WORLD_BANK_INDEX = {
    "real_gdp_growth": "NY.GDP.MKTP.KD.ZG",         # GDP growth (annual %)
    "inflation_cpi": "FP.CPI.TOTL.ZG",              # Inflation, consumer prices (annual %)
    "lending_rate": "FR.INR.LEND",                  # Lending interest rate (%)
    "fx_lcu_per_usd": "PA.NUS.FCRF",                # Official exchange rate (LCU per USD)
    "current_account_gdp": "BN.CAB.XOKA.GD.ZS",     # Current account balance (% of GDP)
    "gov_debt_gdp": "GC.DOD.TOTL.GD.ZS",            # Central government debt, total (% of GDP)
    "fiscal_balance_gdp": "GC.NLD.TOTL.GD.ZS",      # Net lending(+)/borrowing(-), % of GDP
}


STOCK_INFO = [
    {"alias": "ticker",                     "source": "symbol",               "fancy_name": "Ticker"},
    {"alias": "name",                       "source": "shortName",            "fancy_name": "Company Name"},
    {"alias": "country",                    "source": "country",              "fancy_name": "Country"},
    {"alias": "region",                     "source": "region",               "fancy_name": "Region"},
    {"alias": "currency",                   "source": "currency",             "fancy_name": "Currency"},
    {"alias": "industry",                   "source": "industry",             "fancy_name": "Industry"},
    {"alias": "sector",                     "source": "sector",               "fancy_name": "Sector"},
    {"alias": "company_summary",            "source": "longBusinessSummary",  "fancy_name": "Company Summary"},
    {"alias": "beta",                       "source": "beta",                 "fancy_name": "Beta"},
    {"alias": "fifty_two_week_low",         "source": "fiftyTwoWeekLow",      "fancy_name": "52-Week Low"},
    {"alias": "fifty_two_week_high",        "source": "fiftyTwoWeekHigh",     "fancy_name": "52-Week High"},
    {"alias": "fifty_two_week_change",      "source": "52WeekChange",         "fancy_name": "52-Week Change"},
    {"alias": "total_contractual_obligations","source": "totalDebt",          "fancy_name": "Total Contractual Obligations"},
]



FINANCIALS = {
    # Balance Sheet
    "total_equity": {
        "source": "balance_sheet",
        "fields": ["Common Stock Equity", "Total Equity Gross Minority Interest", "Stockholders Equity"],
        "fancy_name": "Total Equity",
    },
    "total_liabilities": {
        "source": "balance_sheet",
        "fields": ["Total Liabilities Net Minority Interest", "Total Liabilities"],
        "fancy_name": "Total Liabilities",
    },
    "current_liabilities": {
        "source": "balance_sheet",
        "fields": ["Current Liabilities"],
        "fancy_name": "Current Liabilities",
    },
    "long_liabilities": {
        "source": "balance_sheet",
        "fields": [
            "Total Non Current Liabilities Net Minority Interest",
            "Long Term Debt And Capital Lease Obligation",
            "Long Term Debt",
        ],
        "fancy_name": "Non-Current Liabilities",
    },
    "long_debt": {
        "source": "balance_sheet",
        "fields": ["Long Term Debt"],
        "fancy_name": "Long-Term Debt",
    },
    "current_assets": {
        "source": "balance_sheet",
        "fields": ["Current Assets"],
        "fancy_name": "Current Assets",
    },
    "cash_and_equivalents": {
        "source": "balance_sheet",
        "fields": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
        "fancy_name": "Cash & Cash Equivalents",
    },
    "shares_outstanding": {
        "source": "balance_sheet",
        "fields": ["Ordinary Shares Number", "Share Issued", "Common Stock Shares Outstanding"],
        "fancy_name": "Shares Outstanding",
    },
    "total_assets": {
        "source": "balance_sheet",
        "fields": ["Total Assets"],
        "fancy_name": "Total Assets",
    },
    "net_ppe": {
        "source": "balance_sheet",
        "fields": ["Net PPE", "Property Plant Equipment Net"],
        "fancy_name": "Net Property, Plant & Equipment (PP&E)",
    },
    "other_properties": {
        "source": "balance_sheet",
        "fields": ["Other Properties"],
        "fancy_name": "Other Properties",
    },
    "total_debt": {
        "source": "balance_sheet",
        "fields": ["Total Debt"],
        "fancy_name": "Total Debt",
    },
    "short_term_debt_and_capital_obligation": {
        "source": "balance_sheet",
        "fields": ["Current Debt And Capital Lease Obligation"],
        "fancy_name": "Current Debt & Capital Lease Obligations",
    },
    "long_term_debt_and_capital_obligation": {
        "source": "balance_sheet",
        "fields": ["Long Term Debt And Capital Lease Obligation"],
        "fancy_name": "Long-Term Debt & Capital Lease Obligations",
    },
    "retained_earnings": {
        "source": "balance_sheet",
        "fields": ["Retained Earnings"],
        "fancy_name": "Retained Earnings",
    },
    "working_capital": {
        "source": "balance_sheet",
        "fields": ["Working Capital"],
        "fancy_name": "Working Capital",
    },
    "accounts_receivable": {
        "source": "balance_sheet",
        "fields": ["Accounts Receivable", "Receivables"],
        "fancy_name": "Accounts Receivable",
    },

    # Income Statement
    "net_income": {
        "source": "income_statement",
        "fields": ["Net Income Common Stockholders", "Net Income"],
        "fancy_name": "Net Income",
    },
    "total_revenue": {
        "source": "income_statement",
        "fields": ["Total Revenue", "Operating Revenue"],
        "fancy_name": "Total Revenue",
    },
    "ebit": {
        "source": "income_statement",
        "fields": ["EBIT", "Operating Income", "Total Operating Income As Reported", "Pretax Income"],
        "fancy_name": "EBIT (Operating Income)",
    },
    "gross_profit": {
        "source": "income_statement",
        "fields": ["Gross Profit"],
        "fancy_name": "Gross Profit",
    },
    "sga": {
        "source": "income_statement",
        "fields": ["Selling General And Administration", "Selling General Administrative Expense"],
        "fancy_name": "Selling, General & Administrative (SG&A)",
    },
    "interest_expense": {
        "source": "income_statement",
        "fields": ["Interest Expense"],
        "fancy_name": "Interest Expense",
    },
    "diluted_eps": {
        "source": "income_statement",
        "fields": ["Diluted EPS", "Basic EPS", "DilutedEPS"],
        "fancy_name": "Earnings Per Share (Diluted)",
    },
    "cost_of_goods": {
        "source": "income_statement",
        "fields": ["Cost of Revenue"],
        "fancy_name": "Cost of Revenue (COGS)",
    },
    "tax_provision": {
        "source": "income_statement",
        "fields": ["Tax Provision"],
        "fancy_name": "Tax Provision",
    },
    "pretax_income": {
        "source": "income_statement",
        "fields": ["Pretax Income"],
        "fancy_name": "Pre-Tax Income",
    },

    # Cash Flow
    "free_cashflow": {
        "source": "cash_flow",
        "fields": ["Free Cash Flow"],
        "fancy_name": "Free Cash Flow (FCF)",
    },
    "operating_cashflow": {
        "source": "cash_flow",
        "fields": ["Operating Cash Flow", "Total Cash From Operating Activities"],
        "fancy_name": "Operating Cash Flow (OCF)",
    },
    "capex": {
        "source": "cash_flow",
        "fields": ["Capital Expenditure", "Purchase Of PPE", "Capital Expenditures"],
        "fancy_name": "Capital Expenditures (CapEx)",
    },
    "dividends_paid": {
        "source": "cash_flow",
        "fields": ["Cash Dividends Paid", "Common Stock Dividends Paid", "Dividends Paid"],
        "fancy_name": "Dividends Paid",
    },
    "depreciation_amortization_depletion": {
        "source": "cash_flow",
        "fields": [
            "Depreciation And Amortization In Income Statement",
            "Depreciation Amortization Depletion Income Statement",
            "Depreciation Amortization Depletion",
        ],
        "fancy_name": "Depreciation & Amortization & Depletion",
    },
}


DERIVED_METRICS = {
    # --- Scalars ---
    "beta":                               {"fancy_name": "Beta",                               "kind": "scalar"},
    "risk_free_rate":                     {"fancy_name": "Risk-Free Rate",                     "kind": "scalar"},
    "next_year_growth_estimates":         {"fancy_name": "Next Year Growth Estimate",          "kind": "scalar"},
    "net_insider_purchases":              {"fancy_name": "Net Insider Purchases",              "kind": "scalar"},
    "current_price":                      {"fancy_name": "Current Price",                      "kind": "scalar"},
    "dividend_per_share_cagr":            {"fancy_name": "Dividend Per Share CAGR",            "kind": "scalar"},

    # --- Series ---
    "stock_prices_atm":                   {"fancy_name": "Price at Report Date",                     "kind": "series"},
    "debt_to_equity":                     {"fancy_name": "Debt to Equity",                     "kind": "series"},
    "net_profit_margin":                  {"fancy_name": "Net Profit Margin",                  "kind": "series"},
    "return_on_equity":                   {"fancy_name": "Return on Equity",                   "kind": "series"},
    "current_ratio":                      {"fancy_name": "Current Ratio",                      "kind": "series"},

    "earning_yoy_growth":                 {"fancy_name": "Earnings YoY Growth",                "kind": "series"},
    "market_cap":                         {"fancy_name": "Market Capitalization",              "kind": "series"},

    "price_to_book":                      {"fancy_name": "Price to Book",                      "kind": "series"},
    "book_value_per_share":               {"fancy_name": "Book Value Per Share",               "kind": "series"},
    "earning_per_share":                  {"fancy_name": "Earnings Per Share",                 "kind": "series"},
    "price_to_earning":                   {"fancy_name": "Price to Earnings",                  "kind": "series"},
    "trailing_peg_ratio":                 {"fancy_name": "Trailing PEG Ratio",                 "kind": "series"},
    "enterprise_profit":                  {"fancy_name": "Enterprise Profit",                  "kind": "series"},

    "beneish_m":                          {"fancy_name": "Beneish M-Score",                    "kind": "series"},
    "altman_z":                           {"fancy_name": "Altman Z-Score",                     "kind": "series"},

    "dividend_per_share_history":         {"fancy_name": "Dividend Per Share",                 "kind": "series"},
    "dividend_payout_ratio":              {"fancy_name": "Dividend Payout Ratio",              "kind": "series"},
    "price_at_dividend":                  {"fancy_name": "Price at Dividend",                  "kind": "series"},
    "dividend_yield":                     {"fancy_name": "Dividend Yield",                     "kind": "series"},
    "dividend_per_share_yoy_growth":      {"fancy_name": "Dividend Per Share YoY Growth",      "kind": "series"},

    "tax_rate":                           {"fancy_name": "Tax Rate",                           "kind": "series"},
}


# --- NEW: central definition of the overview “Key Ratios” ---
KEY_RATIO_DICT = {
    # Scalars
    "current_price": {
        "attr": "current_price",
        "kind": "scalar",
        "fancy_name": "Current Price",
        "format": "money",
    },
    "fifty_two_week_change": {
        "attr": "fifty_two_week_change",
        "kind": "scalar",
        "fancy_name": "52-Week Change",
        "format": "ratio",
    },
    "beta": {
        "attr": "beta",
        "kind": "scalar",
        "fancy_name": "Beta",
        "format": "raw",
    },

    # Series (we’ll take the latest available value)
    "price_to_earning": {
        "attr": "price_to_earning",
        "kind": "series_latest",
        "fancy_name": "P/E",
        "format": "ratio",
    },
    "trailing_peg_ratio": {
        "attr": "trailing_peg_ratio",
        "kind": "series_latest",
        "fancy_name": "Trailing PEG",
        "format": "ratio",
    },
    "price_to_book": {
        "attr": "price_to_book",
        "kind": "series_latest",
        "fancy_name": "P/B",
        "format": "ratio",
    },
    "return_on_equity": {
        "attr": "return_on_equity",
        "kind": "series_latest",
        "fancy_name": "ROE",
        "format": "ratio",
    },
    "net_profit_margin": {
        "attr": "net_profit_margin",
        "kind": "series_latest",
        "fancy_name": "Net Margin",
        "format": "ratio",
    },
    "debt_to_equity": {
        "attr": "debt_to_equity",
        "kind": "series_latest",
        "fancy_name": "Debt to Equity",
        "format": "ratio",
    },
    "dividend_yield": {
        "attr": "dividend_yield",
        "kind": "series_latest",
        "fancy_name": "Dividend Yield",
        "format": "ratio",
    },
    "current_ratio": {
        "attr": "current_ratio",
        "kind": "series_latest",
        "fancy_name": "Current Ratio",
        "format": "ratio",
    },
}


DEFAULT_PARAM_DICT = {
    "discount_rate": 0.09,
    "margin_of_safety": 0.25,
    "decline_rate": 0.05,
    "n_years1": 10,
    "n_years2": 10,
    "growth_rate": 0.05,
    "terminal_growth_rate": 0.02,
    "risk_free_rate": 0.03,
    "average_market_return": 0.09
}


# Base canonical map (add as needed)
_COUNTRY_ISO3_BASE = {
    "UNITED STATES": "USA", "US": "USA", "U.S.": "USA", "USA": "USA",
    "UNITED STATES OF AMERICA": "USA", "AMERICA": "USA",
    "SINGAPORE": "SGP", "SG": "SGP",
    "INDONESIA": "IDN", "ID": "IDN",
    "UNITED KINGDOM": "GBR", "UK": "GBR", "U.K.": "GBR", "BRITAIN": "GBR", "GREAT BRITAIN": "GBR",
    "JAPAN": "JPN", "JP": "JPN",
    "CHINA": "CHN", "CN": "CHN", "PEOPLE'S REPUBLIC OF CHINA": "CHN", "PEOPLES REPUBLIC OF CHINA": "CHN", "PRC": "CHN",
    "HONG KONG": "HKG", "HK": "HKG",
    "CANADA": "CAN", "CA": "CAN",
    "AUSTRALIA": "AUS", "AU": "AUS",
    "INDIA": "IND", "IN": "IND",
    "GERMANY": "DEU", "DE": "DEU", "FEDERAL REPUBLIC OF GERMANY": "DEU",
    "FRANCE": "FRA", "FR": "FRA",
    "SPAIN": "ESP", "ES": "ESP",
    "ITALY": "ITA", "IT": "ITA",
    "NETHERLANDS": "NLD", "HOLLAND": "NLD",
    "SWITZERLAND": "CHE",
    "SWEDEN": "SWE",
    "DENMARK": "DNK",
    "NORWAY": "NOR",
    "FINLAND": "FIN",
    "BELGIUM": "BEL",
    "IRELAND": "IRL",
    "AUSTRIA": "AUT",
    "PORTUGAL": "PRT",
    "GREECE": "GRC",
    "POLAND": "POL",
    "CZECH REPUBLIC": "CZE", "CZECHIA": "CZE",
    "HUNGARY": "HUN",
    "TURKEY": "TUR", "TÜRKIYE": "TUR",
    "RUSSIAN FEDERATION": "RUS", "RUSSIA": "RUS",
    "BRAZIL": "BRA",
    "ARGENTINA": "ARG",
    "MEXICO": "MEX",
    "CHILE": "CHL",
    "COLOMBIA": "COL",
    "PERU": "PER",
    "VENEZUELA": "VEN",
    "SOUTH AFRICA": "ZAF",
    "EGYPT": "EGY",
    "SAUDI ARABIA": "SAU",
    "UNITED ARAB EMIRATES": "ARE", "UAE": "ARE",
    "QATAR": "QAT",
    "KUWAIT": "KWT",
    "ISRAEL": "ISR",
    "KOREA, REPUBLIC OF": "KOR", "REPUBLIC OF KOREA": "KOR", "SOUTH KOREA": "KOR", "KOREA": "KOR",
    "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": "PRK", "NORTH KOREA": "PRK",
    "TAIWAN": "TWN",
    "VIET NAM": "VNM", "VIETNAM": "VNM",
    "THAILAND": "THA",
    "MALAYSIA": "MYS",
    "PHILIPPINES": "PHL",
    "INDONESIA": "IDN",
    "NEW ZEALAND": "NZL",
}

def _norm_country(s: str) -> str:
    return "".join(ch for ch in s.upper().strip() if ch.isalnum() or ch.isspace())

# Build a normalized key map (spaces preserved for readability, but we compare normalized)
COUNTRY_ISO3 = { _norm_country(k): v for k, v in _COUNTRY_ISO3_BASE.items() }

def try_iso3(country: str | None) -> str | None:
    """
    Robust resolver:
    - Normalize punctuation/case (e.g., 'United States of America' → 'UNITED STATES OF AMERICA')
    - Direct dictionary hit on many common synonyms
    - If already looks like ISO3 (len==3 & A-Z), return as-is
    - Fallback: try prefix/contains matches on known keys
    """
    if not country:
        return None
    c_raw = str(country).strip()
    c_norm = _norm_country(c_raw)

    # Already ISO-3?
    if len(c_norm) == 3 and c_norm.isalpha():
        return c_norm

    # Direct match
    hit = COUNTRY_ISO3.get(c_norm)
    if hit:
        return hit

    # Heuristic: startswith/contains against known keys
    for k_norm, iso in COUNTRY_ISO3.items():
        if c_norm == k_norm:
            return iso
        if c_norm.startswith(k_norm) or k_norm.startswith(c_norm):
            return iso
        if k_norm in c_norm:
            return iso

    return None


# As of Oct 2025: https://worldperatio.com/sp-500-sectors/ convert to yahoo finance naming: https://finance.yahoo.com/sectors/
SECTOR_PE_RATIO = {
    "Technology": 38.50,
    "Real Estate": 35.28,
    "Consumer Cyclical": 29.69,
    "Basic Materials": 26.98,
    "Industrials": 26.84,
    "Healthcare": 24.43,
    "Consumer Defensive": 22.73,
    "Utilities": 21.74,
    "Financial Services": 19.64,
    "Communication Services": 19.35,
    "Energy": 17.64,
}

#As of Sep 2025: https://fullratio.com/profit-margin-by-industry
INDUSTRIAL_NPM_RATIO = {
    "Advertising Agencies": {"net_margin": -0.025, "count": 27},
    "Aerospace & Defense": {"net_margin": 0.064, "count": 57},
    "Agricultural Inputs": {"net_margin": 0.012, "count": 11},
    "Airlines": {"net_margin": 0.011, "count": 13},
    "Airports & Air Services": {"net_margin": None, "count": 5},
    "Aluminum": {"net_margin": 0.038, "count": 4},
    "Apparel Manufacturing": {"net_margin": 0.026, "count": 15},
    "Apparel Retail": {"net_margin": 0.025, "count": 29},
    "Asset Management": {"net_margin": 0.218, "count": 83},
    "Auto Manufacturers": {"net_margin": 0.047, "count": 17},
    "Auto Parts": {"net_margin": 0.028, "count": 44},
    "Auto & Truck Dealerships": {"net_margin": 0.006, "count": 20},
    "Banks - Diversified": {"net_margin": 0.296, "count": 5},
    "Banks - Regional": {"net_margin": 0.242, "count": 288},
    "Beverages - Non-Alcoholic": {"net_margin": 0.097, "count": 12},
    "Beverages - Wineries & Distilleries": {"net_margin": 0.04, "count": 6},
    "Biotechnology": {"net_margin": -1.697, "count": 476},
    "Broadcasting": {"net_margin": 0.038, "count": 10},
    "Building Materials": {"net_margin": 0.144, "count": 10},
    "Building Products & Equipment": {"net_margin": 0.066, "count": 27},
    "Business Equipment & Supplies": {"net_margin": 0.04, "count": 5},
    "Capital Markets": {"net_margin": 0.15, "count": 48},
    "Chemicals": {"net_margin": -0.038, "count": 15},
    "Coking Coal": {"net_margin": 0.006, "count": 5},
    "Communication Equipment": {"net_margin": -0.015, "count": 43},
    "Computer Hardware": {"net_margin": -0.038, "count": 28},
    "Conglomerates": {"net_margin": -0.002, "count": 15},
    "Consulting Services": {"net_margin": 0.068, "count": 14},
    "Consumer Electronics": {"net_margin": -0.057, "count": 8},
    "Copper": {"net_margin": None, "count": 4},
    "Credit Services": {"net_margin": 0.18, "count": 40},
    "Diagnostics & Research": {"net_margin": -0.464, "count": 46},
    "Discount Stores": {"net_margin": 0.017, "count": 8},
    "Drug Manufacturers - General": {"net_margin": -0.006, "count": 14},
    "Drug Manufacturers - Specialty & Generic": {"net_margin": -0.285, "count": 48},
    "Education & Training Services": {"net_margin": 0.082, "count": 19},
    "Electrical Equipment & Parts": {"net_margin": 0.046, "count": 39},
    "Electronic Components": {"net_margin": 0.024, "count": 35},
    "Electronic Gaming & Multimedia": {"net_margin": -0.033, "count": 12},
    "Electronics & Computer Distribution": {"net_margin": 0.004, "count": 9},
    "Engineering & Construction": {"net_margin": 0.044, "count": 36},
    "Entertainment": {"net_margin": 0.009, "count": 35},
    "Farm & Heavy Construction Machinery": {"net_margin": 0.05, "count": 19},
    "Farm Products": {"net_margin": 0.008, "count": 15},
    "Financial Data & Stock Exchanges": {"net_margin": 0.326, "count": 11},
    "Food Distribution": {"net_margin": 0.007, "count": 11},
    "Footwear & Accessories": {"net_margin": 0.066, "count": 9},
    "Furnishings, Fixtures & Appliances": {"net_margin": 0.002, "count": 25},
    "Gambling": {"net_margin": 0.074, "count": 9},
    "Gold": {"net_margin": 0.16, "count": 31},
    "Grocery Stores": {"net_margin": 0.023, "count": 9},
    "Healthcare Plans": {"net_margin": 0.001, "count": 11},
    "Health Information Services": {"net_margin": -0.191, "count": 40},
    "Home Improvement Retail": {"net_margin": 0.028, "count": 8},
    "Household & Personal Products": {"net_margin": 0.043, "count": 24},
    "Industrial Distribution": {"net_margin": 0.049, "count": 17},
    "Information Technology Services": {"net_margin": 0.049, "count": 49},
    "Insurance Brokers": {"net_margin": 0.08, "count": 13},
    "Insurance - Diversified": {"net_margin": 0.114, "count": 9},
    "Insurance - Life": {"net_margin": 0.067, "count": 15},
    "Insurance - Property & Casualty": {"net_margin": 0.105, "count": 36},
    "Insurance - Reinsurance": {"net_margin": 0.082, "count": 8},
    "Insurance - Specialty": {"net_margin": 0.187, "count": 20},
    "Integrated Freight & Logistics": {"net_margin": 0.009, "count": 17},
    "Internet Content & Information": {"net_margin": -0.015, "count": 45},
    "Internet Retail": {"net_margin": 0.038, "count": 26},
    "Leisure": {"net_margin": 0.005, "count": 23},
    "Lodging": {"net_margin": 0.079, "count": 8},
    "Luxury Goods": {"net_margin": 0.0, "count": 8},
    "Marine Shipping": {"net_margin": 0.131, "count": 24},
    "Medical Care Facilities": {"net_margin": 0.004, "count": 38},
    "Medical Devices": {"net_margin": -0.51, "count": 110},
    "Medical Distribution": {"net_margin": -0.048, "count": 6},
    "Medical Instruments & Supplies": {"net_margin": -0.146, "count": 42},
    "Metal Fabrication": {"net_margin": 0.046, "count": 15},
    "Mortgage Finance": {"net_margin": 0.135, "count": 15},
    "Oil & Gas Drilling": {"net_margin": -0.01, "count": 8},
    "Oil & Gas E&P": {"net_margin": 0.109, "count": 60},
    "Oil & Gas Equipment & Services": {"net_margin": 0.038, "count": 42},
    "Oil & Gas Integrated": {"net_margin": 0.07, "count": 6},
    "Oil & Gas Midstream": {"net_margin": 0.177, "count": 36},
    "Oil & Gas Refining & Marketing": {"net_margin": 0.013, "count": 17},
    "Other Industrial Metals & Mining": {"net_margin": -0.043, "count": 17},
    "Other Precious Metals & Mining": {"net_margin": -0.081, "count": 10},
    "Packaged Foods": {"net_margin": 0.027, "count": 46},
    "Packaging & Containers": {"net_margin": 0.037, "count": 20},
    "Paper & Paper Products": {"net_margin": 0.021, "count": 4},
    "Personal Services": {"net_margin": 0.091, "count": 10},
    "Pollution & Treatment Controls": {"net_margin": 0.076, "count": 12},
    "Publishing": {"net_margin": -0.012, "count": 7},
    "Railroads": {"net_margin": 0.13, "count": 8},
    "Real Estate - Development": {"net_margin": 0.169, "count": 8},
    "Real Estate - Diversified": {"net_margin": 0.09, "count": 4},
    "Real Estate Services": {"net_margin": 0.0, "count": 30},
    "Recreational Vehicles": {"net_margin": 0.011, "count": 11},
    "REIT - Diversified": {"net_margin": 0.129, "count": 16},
    "REIT - Healthcare Facilities": {"net_margin": 0.131, "count": 16},
    "REIT - Hotel & Motel": {"net_margin": 0.016, "count": 14},
    "REIT - Industrial": {"net_margin": 0.278, "count": 17},
    "REIT - Mortgage": {"net_margin": 0.3, "count": 40},
    "REIT - Office": {"net_margin": -0.057, "count": 22},
    "REIT - Residential": {"net_margin": 0.102, "count": 20},
    "REIT - Retail": {"net_margin": 0.197, "count": 26},
    "REIT - Specialty": {"net_margin": 0.184, "count": 19},
    "Rental & Leasing Services": {"net_margin": 0.071, "count": 18},
    "Residential Construction": {"net_margin": 0.091, "count": 22},
    "Resorts & Casinos": {"net_margin": 0.021, "count": 16},
    "Restaurants": {"net_margin": 0.031, "count": 43},
    "Scientific & Technical Instruments": {"net_margin": 0.117, "count": 24},
    "Security & Protection Services": {"net_margin": 0.079, "count": 15},
    "Semiconductor Equipment & Materials": {"net_margin": 0.023, "count": 27},
    "Semiconductors": {"net_margin": -0.016, "count": 60},
    "Software - Application": {"net_margin": -0.009, "count": 169},
    "Software - Infrastructure": {"net_margin": 0.009, "count": 119},
    "Solar": {"net_margin": -0.117, "count": 19},
    "Specialty Business Services": {"net_margin": 0.043, "count": 31},
    "Specialty Chemicals": {"net_margin": 0.032, "count": 50},
    "Specialty Industrial Machinery": {"net_margin": 0.096, "count": 68},
    "Specialty Retail": {"net_margin": 0.021, "count": 36},
    "Staffing & Employment Services": {"net_margin": 0.025, "count": 21},
    "Steel": {"net_margin": 0.009, "count": 11},
    "Telecom Services": {"net_margin": -0.02, "count": 33},
    "Thermal Coal": {"net_margin": 0.065, "count": 6},
    "Tobacco": {"net_margin": None, "count": 8},
    "Tools & Accessories": {"net_margin": 0.075, "count": 9},
    "Travel Services": {"net_margin": 0.093, "count": 12},
    "Trucking": {"net_margin": 0.027, "count": 13},
    "Uranium": {"net_margin": None, "count": 5},
    "Utilities - Diversified": {"net_margin": 0.112, "count": 10},
    "Utilities - Regulated Electric": {"net_margin": 0.128, "count": 32},
    "Utilities - Regulated Gas": {"net_margin": 0.112, "count": 16},
    "Utilities - Regulated Water": {"net_margin": 0.176, "count": 13},
    "Utilities - Renewable": {"net_margin": 0.077, "count": 15},
    "Waste Management": {"net_margin": 0.021, "count": 13},
}


# As of 28-Sep-2025
# https://www.worldgovernmentbonds.com/
# 10 year bond yield
RISK_FREE_RATE = {
    "Switzerland": 0.00219,
    "Taiwan": 0.01372,
    "Japan": 0.01659,
    "China": 0.01914,
    "Singapore": 0.01938,
    "Denmark": 0.02579,
    "Sweden": 0.02674,
    "Germany": 0.02744,
    "Morocco": 0.02876,
    "Netherlands": 0.02901,
    "South Korea": 0.02943,
    "Ireland": 0.02988,
    "Austria": 0.03048,
    "Croatia": 0.03066,
    "Slovenia": 0.03088,
    "Hong Kong": 0.03103,
    "Cyprus": 0.03112,
    "Finland": 0.03123,
    "Portugal": 0.03185,
    "Canada": 0.03228,
    "Belgium": 0.03300,
    "Spain": 0.03320,
    "Malta": 0.03439,
    "Greece": 0.03462,
    "Malaysia": 0.03471,
    "Slovakia": 0.03493,
    "France": 0.03572,
    "Italy": 0.03612,
    "Lithuania": 0.03678,
    "Vietnam": 0.03759,
    "Bulgaria": 0.03850,
    "Norway": 0.04088,
    "United States": 0.04187,
    "Israel": 0.04193,
    "New Zealand": 0.04257,
    "Qatar": 0.04296,
    "Australia": 0.04392,
    "Czech Republic": 0.04540,
    "United Kingdom": 0.04747,
    "Peru": 0.05293,
    "Serbia": 0.05315,
    "Poland": 0.05550,
    "Chile": 0.05580,
    "Mauritius": 0.05640,
    "Philippines": 0.06025,
    "Bahrain": 0.06063,
    "Indonesia": 0.06431,
    "India": 0.06517,
    "Iceland": 0.06787,
    "Hungary": 0.06920,
    "Romania": 0.07330,
    "Jordan": 0.08501,
    "Mexico": 0.08550,
    "South Africa": 0.09165,
    "Botswana": 0.09199,
    "Bangladesh": 0.09890,
    "Namibia": 0.10422,
    "Colombia": 0.11293,
    "Sri Lanka": 0.11519,
    "Pakistan": 0.12002,
    "Kenya": 0.13430,
    "Brazil": 0.13667,
    "Russia": 0.14735,
    "Nigeria": 0.16643,
    "Kazakhstan": 0.16746,
    "Uganda": 0.16927,
    "Zambia": 0.19500,
    "Ukraine": 0.20410,
    "Egypt": 0.21760,
    "Turkey": 0.29500,
}



ETF_DICT = {
    # North America
    "United States": "VOO",        # Vanguard S&P 500 ETF
    "Canada": "EWC",               # iShares MSCI Canada ETF
    "Mexico": "EWW",               # iShares MSCI Mexico ETF

    # Europe
    "Germany": "EWG",              # iShares MSCI Germany ETF
    "United Kingdom": "EWU",       # iShares MSCI UK ETF
    "France": "EWQ",               # iShares MSCI France ETF
    "Switzerland": "EWL",          # iShares MSCI Switzerland ETF
    "Netherlands": "EWN",          # iShares MSCI Netherlands ETF
    "Spain": "EWP",                # iShares MSCI Spain ETF
    "Italy": "EWI",                # iShares MSCI Italy ETF
    "Sweden": "EWD",               # iShares MSCI Sweden ETF

    # Asia-Pacific
    "Japan": "EWJ",                # iShares MSCI Japan ETF
    "China": "MCHI",               # iShares MSCI China ETF
    "Hong Kong": "EWH",            # iShares MSCI Hong Kong ETF
    "Taiwan": "EWT",               # iShares MSCI Taiwan ETF
    "South Korea": "EWY",          # iShares MSCI Korea ETF
    "India": "INDA",               # iShares MSCI India ETF
    "Australia": "EWA",            # iShares MSCI Australia ETF

    # South America
    "Brazil": "EWZ",               # iShares MSCI Brazil ETF
    "Chile": "ECH",                # iShares MSCI Chile ETF
    "Peru": "EPU",                 # iShares MSCI Peru ETF
    "Colombia": "GXG",             # Global X MSCI Colombia ETF

    # Other / Emerging
    "South Africa": "EZA",         # iShares MSCI South Africa ETF
    "Turkey": "TUR",               # iShares MSCI Turkey ETF
}


CRITERION: dict = {
    "past": {
        "free_cashflow": {
            "fancy_name": "Free Cash Flow Stable & Increasing",
            "description": "Stable and increasing free cash flow strengthens a company’s ability to self-fund operations and strategic initiatives. It reduces reliance on external financing, improving resilience across market cycles. A clear uptrend also supports dividend capacity, buybacks, or deleveraging without compromising growth. Investors view persistent growth in free cash flow as evidence of disciplined capital allocation and durable economics. Sustained improvement typically correlates with higher valuation certainty and lower downside risk.",
            "inputs": None,
            "method": "Mann–Kendall trend test on the free cash flow series.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        },
        "cash_and_equivalents": {
            "fancy_name": "Cash and Cash Equivalents Stable & Increasing",
            "description": "Rising cash and equivalents indicate building liquidity and strategic flexibility. A healthy cash buffer allows the firm to withstand shocks, negotiate from strength, and pursue value-accretive opportunities. Consistent accumulation suggests prudent working capital discipline and measured reinvestment. It can also lower financing costs by improving perceived credit quality. A clear upward trend is a supportive backdrop for future capital deployment.",
            "inputs": None,
            "method": "Mann–Kendall trend test on the cash and cash equivalents series.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        },
        "earning_per_share": {
            "fancy_name": "EPS Stable & Increasing",
            "description": "A persistent rise in earnings per share signals improving profitability per unit of ownership. It often reflects growth in revenues, margin expansion, and thoughtful capital allocation. Compounding EPS tends to compress perceived risk and can justify higher multiples. Stable trajectories are preferred over volatile spikes, as they are easier to underwrite. Sustained increases typically align with stronger competitive positioning and execution.",
            "inputs": None,
            "method": "Mann–Kendall trend test on EPS.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        },
        "book_value_per_share": {
            "fancy_name": "BVPS Stable & Increasing",
            "description": "Growing book value per share indicates net assets accruing to shareholders over time. It captures the compounding effect of retained earnings and prudent balance-sheet management. A steady climb suggests that intrinsic value is accumulating even when market prices fluctuate. This measure is particularly useful for capital-intensive or asset-heavy businesses. Persistent BVPS growth supports long-term return potential and downside protection.",
            "inputs": None,
            "method": "Mann–Kendall trend test on BVPS.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        },
        "net_profit_margin": {
            "fancy_name": "Net Profit Margin Stable & Increasing",
            "description": "Improving net profit margins demonstrate operating leverage and cost discipline. Margin expansion often reflects pricing power, mix shift, or structural efficiency gains. Durable margin increases enhance cash generation and reinvestment capacity. They also buffer volatility during demand slowdowns. Consistent upward movement reinforces quality of earnings and business resilience.",
            "inputs": None,
            "method": "Mann–Kendall trend test on net profit margin.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        },
        "return_on_equity": {
            "fancy_name": "Return on Equity Stable & Increasing",
            "description": "Rising ROE indicates increasingly efficient conversion of equity into profits. It often captures better utilization of assets, stronger margins, or improved capital structure. Persistent improvement compounds shareholder value and can justify premium valuations. Stability is important, as erratic ROE can reflect transient accounting or leverage effects. A clean, positive trend supports the thesis of a strengthening franchise.",
            "inputs": None,
            "method": "Mann–Kendall trend test on ROE.",
            "criteria": "Positive Kendall’s tau > 0 and p-value < 0.10."
        }
    },

    "present": {
        "enterprise_profits": {
            "fancy_name": "Enterprise Profit Threshold",
            "description": "Enterprise profit gauges operating earning power relative to the full asset base employed. A sufficiently high level suggests that the firm clears its opportunity cost with a robust margin of safety. Passing the threshold today indicates competitive strength rather than cyclical luck. This constraint also filters out businesses that rely on leverage or accounting quirks to appear profitable. Meeting a demanding bar now sets a high-quality baseline for forward returns.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Enterprise Profit must be ≥ 0.18."
        },
        "price_to_book": {
            "fancy_name": "Price-to-Book Discipline",
            "description": "A bounded price-to-book multiple enforces valuation discipline against balance-sheet value. It reduces downside from sentiment swings and exuberant expectations. Reasonable PB levels are especially relevant in asset-heavy or financial businesses. Capping the multiple helps keep expectations aligned with tangible compounding. This rule is a practical guardrail when earnings are temporarily noisy.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "0 < PB ≤ 3."
        },
        "peg_ratio": {
            "fancy_name": "PEG Reasonableness",
            "description": "The PEG ratio relates valuation to expected earnings growth, helping to avoid paying too much for momentum. A ceiling encourages investors to require growth at a fair price rather than any price. It is a coarse tool, but practical for quickly screening. Keeping PEG in check reduces reliance on flawless execution to earn acceptable returns. This constraint complements other quality and profitability gates.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "0 < PEG ≤ 1."
        },
        "return_on_equity": {
            "fancy_name": "Minimum Return on Equity",
            "description": "A minimum ROE ensures the business generates attractive profits relative to shareholder capital. High ROE firms can reinvest internally at compelling rates or return capital efficiently. This threshold also screens out low-quality franchises masquerading behind leverage. Sustained ROE above the bar is a hallmark of durable advantages or superior execution. It aligns today’s profitability with the compounding you expect tomorrow.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "ROE ≥ 0.15."
        },
        "price_earning": {
            "fancy_name": "PE Versus Industry",
            "description": "Comparing PE to the industry keeps valuation anchored to peers facing similar economics. It helps avoid overpaying during hot cycles or thematic manias. Staying below the sector bar leaves room for multiple expansion if execution proves out. It also mitigates the risk of regime shifts that compress high multiples. The rule balances absolute prudence with relative realism.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "0 < PE < industry average PE."
        },
        "net_profit_margin": {
            "fancy_name": "Net Margin Versus Industry",
            "description": "A margin above industry norms implies stronger pricing power, mix, or efficiency. It hints at differentiation that competitors find hard to copy. Superior margins translate into more self-funded growth and better shock absorption. It also reduces the dependence on leverage or aggressive accounting to hit targets. Exceeding the peer bar today supports confidence in forward economics.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "NPM > industry average net margin."
        }
    },

    "future": {
        "free_cashflow": {
            "fancy_name": "Free Cash Flow Momentum",
            "description": "A latest growth rate above the historical average indicates improving momentum. It suggests that recent execution or market dynamics are turning more favorable. Positive momentum increases the likelihood that near-term forecasts will be met or exceeded. This supports higher confidence in capital deployment and valuation. It is a pragmatic check that recent data are trending in the right direction.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        },
        "cash_and_equivalents": {
            "fancy_name": "Cash and Equivalents Momentum",
            "description": "An accelerating growth rate in cash builds optionality for investment and defense. It often reflects operational discipline and prudent capital planning. Momentum here can foreshadow buybacks, acquisitions, or deleveraging. It also cushions volatility in working capital and macro shocks. Stronger recent growth versus average is a constructive signal.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        },
        "earning_per_share": {
            "fancy_name": "EPS Momentum",
            "description": "EPS growth running above its average hints at improving profitability dynamics. This may stem from mix, pricing, or scale benefits coming through more strongly. Momentum increases the chance of positive revisions and sentiment follow-through. It can also validate the sustainability of earlier efficiency gains. Surpassing the historical average is a practical forward-tilted confirmation.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        },
        "book_value_per_share": {
            "fancy_name": "BVPS Momentum",
            "description": "When BVPS growth exceeds its average, retained value accumulation is accelerating. This indicates stronger earnings retention or fewer charges eroding equity. Faster compounding improves long-term intrinsic value trajectories. It also supports more self-financed reinvestment. Momentum above average is an encouraging forward signal.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        },
        "net_profit_margin": {
            "fancy_name": "Margin Momentum",
            "description": "Recent margin gains above average imply durable operational improvements are taking hold. This could reflect better mix, productivity, or pricing discipline. Elevated momentum improves cash conversion and cushions cyclical episodes. It supports more confident reinvestment and competitive responses. Exceeding the historical mean underscores strengthening unit economics.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        },
        "return_on_equity": {
            "fancy_name": "ROE Momentum",
            "description": "An ROE growth rate that outpaces its average suggests improving capital efficiency. It points to better asset turns, margins, or optimization of the capital stack. Persistent momentum reduces reliance on external capital for growth. It also enhances the durability of compounding when reinvested. Beating the average signals forward improvement rather than mere mean reversion.",
            "inputs": None,
            "method": "Compare latest YoY growth to the mean of YoY growth history.",
            "criteria": "Latest YoY growth > mean YoY growth."
        }
    },

    "health": {
        "current_ratio": {
            "fancy_name": "Short-Term Liquidity Buffer",
            "description": "A strong current ratio indicates the ability to cover near-term obligations comfortably. It reduces refinancing risk and supply-chain fragility. Healthy liquidity also creates room to act on tactical opportunities. It typically correlates with more stable operations through cycles. Maintaining a robust buffer is a hallmark of prudent financial management.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Current ratio ≥ 1.5."
        },
        "debt_to_equity": {
            "fancy_name": "Leverage Prudence",
            "description": "Moderate leverage limits downside in cyclical or shock scenarios. Lower debt loads preserve strategic flexibility and reduce interest burden. A conservative capital structure also cushions covenant pressure. It improves survivability during liquidity squeezes. Keeping D/E in check aligns with durable compounding.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Debt-to-equity ≤ 0.5."
        },
        "beneish_m": {
            "fancy_name": "Earnings Quality Screen (Beneish M-Score)",
            "description": "The Beneish M-Score flags patterns consistent with aggressive accounting. A sufficiently low score reduces the probability of manipulation risk. This serves as a protective filter before deeper diligence. Passing the bar does not prove innocence but lowers suspicion. It complements other quality and consistency checks.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Beneish M-Score ≤ −2.22."
        },
        "altman_z": {
            "fancy_name": "Financial Distress Risk (Altman Z-Score)",
            "description": "The Altman Z-Score summarizes balance-sheet and profitability signals into a distress probability proxy. Higher scores generally imply lower bankruptcy risk. Clearing the threshold provides a baseline of solvency comfort. It helps compare firms across sectors and cycles with a consistent yardstick. This safeguard pairs well with liquidity and leverage checks.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Altman Z-Score ≥ 1.80."
        },
        "net_insider_purchases": {
            "fancy_name": "Insider Trading Balance  (%)",
            "description": "Net insider buying can signal management’s confidence in intrinsic value. Selling is not always negative, but persistent net selling can be a caution. Observing the balance over time contextualizes valuation and outlook. This indicator complements fundamental metrics with behavioral evidence. A neutral-to-positive tilt supports alignment with shareholders.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Net insider purchases ≥ −0.10 (i.e., not materially negative)."
        },
        "debt_coverage": {
            "fancy_name": "Operating Cash Flow to Debt Coverage",
            "description": "Strong operating cash flow relative to debt indicates manageable balance-sheet pressure. It implies the firm can service obligations from core operations. This reduces dependence on capital markets during stress. Higher coverage also supports optionality for growth. A clear cushion lowers financial risk and improves durability.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Operating cash flow > 20% of total liabilities."
        }
    },

    "dividend": {
        "dividend": {
            "fancy_name": "Dividend Presence Over Recent Years",
            "description": "A consistent dividend record signals a shareholder-friendly capital policy. It indicates confidence in recurring cash generation. Even modest, steady payments can discipline capital allocation. The presence or absence of dividends should be judged alongside reinvestment opportunities. The goal is sustainability rather than cosmetic yield.",
            "inputs": None,
            "method": "All-zero check across a 5 years' window.",
            "criteria": "All five most recent annual DPS values are non-zero (or per your boolean condition)."
        },
        "dividend_yield": {
            "fancy_name": "Minimum Dividend Yield  (%)",
            "description": "A baseline yield ensures a tangible cash return while you wait for compounding. It can cushion drawdowns and smooth total returns. Yield should be supported by underlying free cash flow rather than financial engineering. Excessive yield may signal risk, so a modest floor is prudent. The aim is adequate payout without starving growth.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Dividend yield > 1.5%."
        },
        "dividend_streak": {
            "fancy_name": "Dividend Continuity",
            "description": "A clean dividend streak reflects discipline and visibility into cash flows. Breaks or cuts can indicate stress or shifting priorities. However, pauses may be rational if reinvestment is superior. Context matters, but sustained continuity generally deserves credit. Monitoring the streak helps balance income and growth objectives.",
            "inputs": None,
            "method": "Presence of any zeros across the history window.",
            "criteria": "No zero-payment years within the evaluated window."
        },
        "dividend_volatile": {
            "fancy_name": "Dividend Volatility Check  (%)",
            "description": "Large dividend drops can undermine income reliability and signal deeper issues. Stability supports investor confidence and valuation resilience. Occasional adjustments are acceptable if tied to disciplined capital allocation. The focus is avoiding repeated or severe cuts inconsistent with fundamentals. A low incidence of large declines is preferred.",
            "inputs": None,
            "method": "Detect any YoY DPS drop ≥ 10%.",
            "criteria": "No YoY DPS decline of 10% or more in the lookback."
        },
        "dividend_trend": {
            "fancy_name": "Dividend Stable & Increasing",
            "description": "A positive long-term trend in dividends per share indicates a company’s growing and repeatable cash distribution capacity. It often reflects expanding free cash flow, disciplined capital allocation, and healthy competitive positioning. A statistically meaningful uptrend helps distinguish durable improvement from noise or one-off policy changes. This confidence supports a steadier income profile and can bolster valuation resilience. Clear upward momentum in the dividend record is therefore an encouraging sign for long-term shareholders.",
            "inputs": None,
            "method": "Mann–Kendall trend test on dividends per share (tau and p-value reported together).",
            "criteria": "Positive Kendall’s tau and p-value < 0.10."
        },
        "dividend_payout_ratio": {
            "fancy_name": "Payout Sustainability",
            "description": "A moderate payout ratio balances income today with reinvestment for tomorrow. It reduces the risk of forced cuts during soft patches. Sustainable payouts are typically backed by recurring free cash flow, not leverage. A sensible ceiling leaves room for growth capex and buybacks. The aim is endurance rather than maximum distribution.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "0 < payout ratio < 0.60."
        }
    },

    "macroeconomics": {
        "momentum": {
            "fancy_name": "Real GDP Growth Momentum",
            "description": "Macroeconomic tailwinds improve demand visibility and pricing conditions. A country growing faster than its long-term trend or the world average is supportive for corporate fundamentals. Positive momentum reduces the likelihood of broad-based revenue shocks. It also raises the base rate for investment and employment. Favorable growth regimes compound business quality advantages.",
            "inputs": None,
            "method": "Deterministic comparative rule.",
            "criteria": "3-yr avg ≥ world avg (or country 10-yr avg) AND last year ≥ 0."
        },
        "inflation_stability": {
            "fancy_name": "Inflation Level and Stability",
            "description": "Benign inflation preserves real purchasing power and planning certainty. Excess volatility distorts pricing, margins, and working capital. A contained level with low variability supports steady multiples. It also reduces policy shock risk that can hit growth assets disproportionately. Stability enables quality businesses to compound quietly.",
            "inputs": None,
            "method": "Deterministic thresholds on level and variability.",
            "criteria": "Latest CPI ≤ 5% AND 5-yr std-dev ≤ 3 percentage points."
        },
        "real_interest_rate": {
            "fancy_name": "Real Rate Sanity Range (%)",
            "description": "Real rates summarize policy stance and credit conditions after inflation. Extremely negative real rates can mask fragility, while very high rates can choke growth. A middle range supports balanced incentives for saving and investment. It helps avoid boom-bust dynamics harmful to equity cash flows. Staying within a sane band reduces macro downside skew.",
            "inputs": None,
            "method": "Deterministic band rule.",
            "criteria": "−2% < real rate < 6%."
        },
        "fx_trend": {
            "fancy_name": "FX Trend versus Base Currency  (%)",
            "description": "Persistent currency depreciation erodes foreign returns and may signal structural imbalances. A modest pace is tolerable, especially if offset by strong local returns. Limiting depreciation risk avoids over-reliance on multiple expansion. It also simplifies underwriting of long-dated cash flows. A contained trend keeps macro headwinds manageable.",
            "inputs": None,
            "method": "Deterministic ceiling on FX depreciation CAGR.",
            "criteria": "FX depreciation CAGR ≤ 5% per year."
        },
        "external_balance": {
            "fancy_name": "External Balance Health  (%)",
            "description": "A manageable current account deficit reduces vulnerability to external funding shocks. Improvements relative to recent history are particularly constructive. Healthier balances typically translate into more stable policy and FX. They also reflect competitiveness and balanced domestic demand. This backdrop lowers macro tail-risk for corporates.",
            "inputs": None,
            "method": "Deterministic threshold and improvement rule.",
            "criteria": "Latest ≥ −3% of GDP AND ≥ 5-yr average."
        },
        "fiscal_sustainability": {
            "fancy_name": "Public Debt Sustainability  (%)",
            "description": "Lower public debt burdens reduce the need for distortionary taxes or austerity. It leaves room for counter-cyclical policy during downturns. Sustainable fiscal metrics support lower risk premia across the economy. They also stabilize investor expectations and capital flows. A prudent fiscal stance is a quiet tailwind for equities.",
            "inputs": None,
            "method": "Deterministic threshold rule.",
            "criteria": "Debt ≤ 80% of GDP."
        }
    }
}



VALUATION: dict = {
    "price_earning_multiples": {
        "fancy_name": "Price-to-Earnings Multiples Method",
        "description": "This method estimates fair value by applying a representative P/E multiple to earnings per share, then projecting forward with conservative growth assumptions. The projected value is discounted back to present value using an appropriate discount rate. This approach mirrors how market participants benchmark similar companies and is intuitive for companies with stable, predictable earnings.",
        "feasibility": "Works best for companies with stable, repeatable earnings and clear peer comparables. Less reliable for cyclical businesses, early-stage companies, or when the market multiple is undergoing structural shifts. Requires confidence in both earnings quality and the sustainability of the chosen multiple.",
        "inputs": [
            "Earnings Per Share (3-year median)",
            "Price-to-Earnings Multiple (representative or median)",
            "Conservative Growth Rate",
            "Discount Rate",
            "Projection Years"
        ],
    },

    "discounted_cash_flow_one_stage": {
        "fancy_name": "Discounted Cash Flow (One-Stage, Declining Growth)",
        "description": "This DCF variant projects free cash flow through a single stage where growth declines steadily each year. Each year's cash flow is discounted to present value, and a terminal value captures the business's perpetual worth using a conservative multiple. The model is transparent and captures the natural fade of growth rates over time as businesses mature.",
        "feasibility": "Suitable when free cash flow is stable and meaningful, and when a declining growth pattern reasonably reflects business maturity. Less effective for highly volatile cash flows or businesses undergoing structural shifts in capital intensity. The terminal multiple should be validated against market comparables.",
        "inputs": [
            "Free Cash Flow (3-year median)",
            "Initial Growth Rate",
            "Annual Growth Decline Rate",
            "Discount Rate",
            "Projection Years",
            "Shares Outstanding",
            "Terminal Multiple (typically 10-15x)"
        ],
    },

    "discounted_cash_flow_two_stage": {
        "fancy_name": "Discounted Cash Flow (Two-Stage Model)",
        "description": "A more sophisticated DCF that splits projections into two phases: an initial high-growth stage with declining growth, followed by a stable-growth stage. Terminal value is calculated using the Gordon Growth Model. This structure explicitly models the transition from growth to maturity, making it ideal for companies in transition phases.",
        "feasibility": "Well-suited for companies transitioning from high growth to maturity. Requires careful estimation of when the transition occurs and what stable growth rate is sustainable long-term. Terminal growth should not exceed long-run GDP growth. The model is sensitive to the relationship between discount rate and terminal growth.",
        "inputs": [
            "Free Cash Flow (3-year median)",
            "Initial Growth Rate",
            "Growth Decline Rate",
            "Terminal Growth Rate (typically 2-3%)",
            "Discount Rate",
            "Stage 1 Years",
            "Stage 2 Years",
            "Shares Outstanding"
        ],
    },

    "discounted_dividend_two_stage": {
        "fancy_name": "Dividend Discount Model (Two-Stage)",
        "description": "This model values equity based solely on future dividend payments to shareholders. Dividends are projected through a high-growth stage and a stable-growth stage, then discounted using the cost of equity. Terminal value captures all dividends beyond the projection period. The method directly focuses on cash returned to shareholders.",
        "feasibility": "Best for mature companies with consistent dividend policies and predictable payout patterns. Less suitable for companies retaining most earnings for reinvestment or those with sporadic dividend policies. The relationship between cost of equity and terminal growth is critical—small changes can dramatically affect valuation.",
        "inputs": [
            "Dividend Per Share (3-year median)",
            "Initial Dividend Growth Rate",
            "Terminal Dividend Growth Rate",
            "Cost of Equity",
            "Stage 1 Years",
            "Stage 2 Years"
        ],
    },

    "return_on_equity": {
        "fancy_name": "Return on Equity Capitalization Method",
        "description": "This approach values the company based on its ability to generate returns on shareholders' equity. It projects both book value and dividends forward, then capitalizes terminal earnings using an earnings yield based on market returns. The method ties valuation directly to profitability on the equity base rather than absolute cash flows.",
        "feasibility": "Most effective for established companies where ROE is stable and meaningful. Can be misleading if leverage is changing rapidly or if ROE is artificially inflated by one-time items. The earnings yield assumption should align with the company's risk profile and the broader market environment.",
        "inputs": [
            "Return on Equity (3-year median)",
            "Book Value Per Share (3-year median)",
            "Dividend Per Share (3-year median)",
            "Growth Rate",
            "Discount Rate",
            "Average Market Return (earnings yield proxy)",
            "Projection Years"
        ],
    },

    "excess_return": {
        "fancy_name": "Residual Income (Excess Return) Model",
        "description": "This model focuses on value creation above the cost of capital. It calculates the perpetuity value of returns exceeding the required return on equity, then adds this to current book value. The approach emphasizes economic profit rather than accounting profit, making it useful when traditional cash flow measures don't fully capture value creation.",
        "feasibility": "Works well when ROE and cost of equity are reliably estimable and when accounting accurately reflects economic reality. Less reliable when there's significant divergence between accounting and economic earnings, or when book values are distorted. Highly sensitive when growth approaches the cost of equity.",
        "inputs": [
            "Return on Equity (3-year median)",
            "Cost of Equity",
            "Growth Rate",
            "Total Equity (3-year median)",
            "Shares Outstanding"
        ],
    },

    "graham_number": {
        "fancy_name": "Graham Number (Conservative Valuation Anchor)",
        "description": "Benjamin Graham's classic formula combines earnings and book value into a single valuation benchmark. The constant 22.5 implicitly assumes a P/E of 15 and a P/B of 1.5—conservative multiples for a fairly-valued stock. This is not a precise valuation model but rather a quick sanity check and screening tool.",
        "feasibility": "Most useful as a preliminary screen for established, profitable companies with tangible assets. Far less informative for asset-light businesses, high-growth companies, or those with negative earnings. Should be used alongside more comprehensive valuation methods rather than as a standalone measure.",
        "inputs": [
            "Earnings Per Share (3-year median)",
            "Book Value Per Share (3-year median)"
        ],
    },
}

