from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple, Literal
from datetime import datetime, date, timezone
import logging
import numpy as np
import pandas as pd
import yfinance as yf

from utils.stock import (
    _safe_minus,
    _safe_shift,
    _safe_cagr,
    _get_price_at,
    _extract_close_series,
    _infer_fye_month,
    _extract_news,
    _extract_officers,
    _safe_yoy_growth,
    _safe_div,
    _safe_mul,
    _safe_add,
    _winsorize,
    _annual_dps_complete_years,
    _pct_ret,
    _slice_ticker_block,
    _safe_sign_adjust,
    _build_zero_dividends_series_for_recent_years,
    _select_close_volume,
    _coerce_datetime_columns,
    _zeros_like_series,
    _ensure_list,
    get_current_timestamp,
    _dates_within,
    _infer_reporting_interval_days,
    _k_for_reporting_frequency,
    _latest_quarter_end,
    is_balance_sheet_stale,
    _safe_statement_init,
)

from core.constants import FINANCIALS, STOCK_INFO, RISK_FREE_RATE, ETF_DICT, DERIVED_METRICS

logger = logging.getLogger(__name__)

Statement = Literal["balance_sheet", "cash_flow", "income_statement"]
Freq = Literal["ANNUAL", "QUARTERLY", "TTM"]
REPORTING_SEMIANNUAL_CUTOFF_DAYS = 135


class Stock:
    def __init__(
        self,
        data: pd.DataFrame,
        prices: pd.DataFrame,
        as_of: Optional[date] = None,
    ) -> None:
        self.data = data
        self.prices = _select_close_volume(prices)
        self.current_price = self.data.info["previousClose"]  # preserve behavior
        self._as_of = as_of or pd.Timestamp.utcnow().date()

        self.ticker = self.data.ticker
        self.country = self.data.info["country"]

        self.news = self.get_news()
        self.officers = self.get_officers()

        self.next_year_growth_estimates: Optional[Any]
        growth_estimates = self.data.growth_estimates
        self.next_year_growth_estimates = growth_estimates.loc["+1y", "stockTrend"]

        self.net_insider_purchases = self.data.insider_purchases.fillna(-1).loc[4, "Shares"]

        # === Statements (guard TTM frames) ===
        self.annual_income_statement = _safe_statement_init(
            self.get_financial_statements("income_statement", "ANNUAL"),
        )
        self.annual_balance_sheet = _safe_statement_init(
            self.get_financial_statements("balance_sheet", "ANNUAL"),
        )
        self.annual_cash_flow = _safe_statement_init(
            self.get_financial_statements("cash_flow", "ANNUAL"),
        )

        self.quarterly_income_statement = _safe_statement_init(
            self.get_financial_statements("income_statement", "QUARTERLY"),
        )
        self.quarterly_balance_sheet = _safe_statement_init(
            self.get_financial_statements("balance_sheet", "QUARTERLY"),
        )
        self.quarterly_cash_flow = _safe_statement_init(
            self.get_financial_statements("cash_flow", "QUARTERLY"),
        )

        self.ttm_income_statement = _safe_statement_init(
            self.get_financial_statements("income_statement", "TTM"),
        )
        self.ttm_cash_flow = _safe_statement_init(
            self.get_financial_statements("cash_flow", "TTM"),
        )

        # Per-alias Series
        self.statement_points: Dict[str, pd.Series] = {}

        # === info fields ===
        self.info_fields: Dict[str, Any] = {}
        for entry in STOCK_INFO:
            alias = entry.get("alias")
            source_key = entry.get("source")
            val = self.data.info.get(source_key, None)
            self.info_fields[alias] = val
            setattr(self, alias, val)

        # === Build alias points (as Series) — new FINANCIALS schema ===
        for alias_name, alias_mapping in FINANCIALS.items():
            # Expecting: {"source": <statement>, "fields": [..], "fancy_name": "..."}
            if not isinstance(alias_mapping, dict):
                empty_series = pd.Series(dtype=float, name=alias_name)
                self.statement_points[alias_name] = empty_series
                setattr(self, alias_name, empty_series)
                continue

            statement_name: str = str(alias_mapping.get("source", "")).lower()
            # Keep original rule: balance sheet uses averaged snapshots
            use_average_for_balance_sheet = (statement_name == "balance_sheet")

            series_points_for_alias = self.get_statement_item_points(
                alias_mapping=alias_mapping,
                average=use_average_for_balance_sheet,
                tolerance_days=5,
            )

            self.statement_points[alias_name] = series_points_for_alias
            setattr(self, alias_name, series_points_for_alias)

        # === Risk/return metrics ===
        self.beta: Optional[float] = None
        self.beta = self.get_beta()

        # === Derived metrics (Series) ===
        self.debt_to_equity = _safe_div(self.total_liabilities, self.total_equity).rename("debt_to_equity")
        self.net_profit_margin = _safe_div(self.net_income, self.total_revenue).rename("net_profit_margin")
        self.return_on_equity = _safe_div(self.net_income, self.total_equity).rename("return_on_equity")
        self.current_ratio = _safe_div(self.current_assets, self.current_liabilities).rename("current_ratio")

        self.earning_yoy_growth = _safe_yoy_growth(self.total_revenue).rename("earning_yoy_growth")
        self.price_at = _get_price_at(self.total_equity, self.prices).rename("price_at")

        self.market_cap = _safe_mul(self.price_at, self.shares_outstanding).rename("market_cap")

        # NOTE: Preserve original behavior
        self.book_value_per_share = _safe_div(self.total_equity, self.shares_outstanding).rename("book_value_per_share")
        self.price_to_book = _safe_div(self.price_at, self.book_value_per_share).rename("price_to_book")

        self.earning_per_share = _safe_div(self.net_income, self.shares_outstanding).rename("earning_per_share")
        self.price_to_earning = _safe_div(self.price_at, self.earning_per_share).rename("price_to_earning")
        self.trailing_peg_ratio = _safe_div(
            self.price_to_earning,
            _safe_yoy_growth(self.earning_per_share) * 100.0,
        ).rename("trailing_peg_ratio")

        self.enterprise_profit = _safe_div(self.ebit, self.total_assets).rename("enterprise_profit")

        self.beneish_m = self.compute_beneish_m().rename("beneish_m")
        self.altman_z = self.compute_altman_z().rename("altman_z")

        self.dividend_per_share_history = self.get_dividend_annual_series()

        self.dividend_payout_ratio = _safe_div(
            _safe_sign_adjust(self.dividends_paid, mode="neg_to_pos"),
            self.net_income,
        ).rename("dividend_payout_ratio")

        self.price_at_dividend = _get_price_at(self.dividend_per_share_history, self.prices).rename("price_at_dividend")
        self.dividend_yield = _safe_div(self.dividend_per_share_history, self.price_at_dividend).rename("dividend_yield")

        self.dividend_per_share_yoy_growth = _safe_yoy_growth(
            self.dividend_per_share_history
        ).rename("dividend_per_share_yoy_growth")

        self.dividend_per_share_cagr = _safe_cagr(self.dividend_per_share_history, 10)

        self.risk_free_rate = RISK_FREE_RATE.get(self.country, RISK_FREE_RATE.get("USA", 0.03))

        self.tax_rate = _safe_div(self.tax_provision, self.pretax_income).rename("tax_rate")

    # -----------------------------
    # Public getters / utilities
    # -----------------------------
    def get_prices_series(self) -> pd.DataFrame:
        return self.prices[["Close", "Volume"]]

    def get_financial_statements(self, name: Statement, frequency: Freq = "ANNUAL") -> pd.DataFrame:
        if name == "balance_sheet":
            if frequency == "ANNUAL":
                return getattr(self.data, "balance_sheet", pd.DataFrame())
            elif frequency == "QUARTERLY":
                return getattr(self.data, "quarterly_balance_sheet", pd.DataFrame())
            else:
                raise ValueError("Balance sheet must be 'QUARTERLY' or 'ANNUAL'")

        elif name == "cash_flow":
            if frequency == "ANNUAL":
                return getattr(self.data, "cash_flow", pd.DataFrame())
            elif frequency == "QUARTERLY":
                return getattr(self.data, "quarterly_cash_flow", pd.DataFrame())
            elif frequency == "TTM":
                return getattr(self.data, "ttm_cash_flow", pd.DataFrame())
            else:
                raise ValueError("Cash flow must be 'QUARTERLY' or 'ANNUAL' or 'TTM'")

        elif name == "income_statement":
            if frequency == "ANNUAL":
                return getattr(self.data, "income_stmt", pd.DataFrame())
            elif frequency == "QUARTERLY":
                return getattr(self.data, "quarterly_income_stmt", pd.DataFrame())
            elif frequency == "TTM":
                return getattr(self.data, "ttm_income_stmt", pd.DataFrame())
            else:
                raise ValueError("Income statement must be 'ANNUAL' or 'QUARTERLY' or 'TTM'")

        else:
            raise ValueError("name must be 'balance_sheet' or 'cash_flow' or 'income_statement'")

    def get_fiscal_years_month(self) -> int:
        balance_sheet = self.get_financial_statements("balance_sheet", frequency="ANNUAL")
        return _infer_fye_month(balance_sheet)

    def get_dividend_annual_series(self) -> pd.Series:
        dividends_series = getattr(self.data, "dividends", None)

        if dividends_series is None or len(dividends_series) == 0:
            dividends_series = _build_zero_dividends_series_for_recent_years(
                as_of_timestamp=self._as_of,
                number_of_calendar_years=10,
                quarterly_payment_months=[2, 5, 8, 11],
                day_of_month=15,
            )

        fiscal_year_end_month = self.get_fiscal_years_month()
        return _annual_dps_complete_years(
            dividends=dividends_series,
            fye_month=fiscal_year_end_month,
            as_of=self._as_of,
        )

    def get_news(self) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
        return _extract_news(self.data)

    def get_officers(self) -> list[dict[str, Any]]:
        info = getattr(self.data, "info", {})
        return _extract_officers(info)

    # ============================================================
    # Helpers for BS “LTM-like” (averaged snapshots) and staleness
    # ============================================================
    def _quarterly_item_series(self, item: str) -> pd.Series:
        quarterly_balance_sheet_df = _coerce_datetime_columns(self.quarterly_balance_sheet)
        if quarterly_balance_sheet_df.empty or item not in quarterly_balance_sheet_df.index:
            return _zeros_like_series(quarterly_balance_sheet_df.columns, item)
        series_out = quarterly_balance_sheet_df.loc[item]
        series_out.name = item
        return series_out

    def _annual_item_series(self, item: str) -> pd.Series:
        annual_balance_sheet_df = _coerce_datetime_columns(self.annual_balance_sheet)
        if annual_balance_sheet_df.empty or item not in annual_balance_sheet_df.index:
            return _zeros_like_series(annual_balance_sheet_df.columns, item)
        series_out = annual_balance_sheet_df.loc[item]
        series_out.name = item
        return series_out

    def _latest_col_date(self, statement: str, freq: str) -> Optional[pd.Timestamp]:
        df = self._get_statement_df(statement, freq)
        if df is None or df.empty:
            return None
        df = _coerce_datetime_columns(df)
        return df.columns[0] if df.shape[1] else None

    def is_financials_stale(
        self,
        asof: Optional[date] = None,
        tolerance_days: int = 5,
        require_distinct_from_annual: bool = True,
    ) -> bool:
        gap_ok = is_balance_sheet_stale(
            self.quarterly_balance_sheet,
            asof=asof or self._as_of,
            tolerance_days=tolerance_days,
        )

        q_is = self._latest_col_date("income_statement", "QUARTERLY")
        a_is = self._latest_col_date("income_statement", "ANNUAL")
        q_cf = self._latest_col_date("cash_flow", "QUARTERLY")
        a_cf = self._latest_col_date("cash_flow", "ANNUAL")

        is_equal = _dates_within(q_is, a_is, tolerance_days)
        cf_equal = _dates_within(q_cf, a_cf, tolerance_days)
        equal_any = is_equal or cf_equal

        if require_distinct_from_annual:
            return bool(gap_ok and (not equal_any))
        else:
            return bool(gap_ok and equal_any)

    def _get_statement_df(self, statement: Statement, freq: Freq) -> pd.DataFrame:
        statement = statement.lower()
        freq = freq.upper()
        if statement == "balance_sheet":
            return self.annual_balance_sheet if freq == "ANNUAL" else self.quarterly_balance_sheet
        elif statement == "cash_flow":
            if freq == "ANNUAL":
                return self.annual_cash_flow
            if freq == "QUARTERLY":
                return self.quarterly_cash_flow
            if freq == "TTM":
                return self.ttm_cash_flow
        elif statement == "income_statement":
            if freq == "ANNUAL":
                return self.annual_income_statement
            if freq == "QUARTERLY":
                return self.quarterly_income_statement
            if freq == "TTM":
                return self.ttm_income_statement
        raise ValueError(
            "statement must be one of: 'balance_sheet', 'cash_flow', 'income_statement' and freq in {'ANNUAL','QUARTERLY','TTM'}"
        )

    def _k_for_reporting_frequency(self) -> int:
        return _k_for_reporting_frequency(self.quarterly_balance_sheet, REPORTING_SEMIANNUAL_CUTOFF_DAYS)

    def _average_last_k_quarterly(self, item: str) -> float:
        k = self._k_for_reporting_frequency()
        s = self._quarterly_item_series(item).iloc[:k].dropna()
        if s.size < 2:
            return float("nan")
        return float(s.mean())

    def _latest_quarterly_value(self, item: str) -> float:
        s = self._quarterly_item_series(item).dropna()
        return float(s.iloc[0]) if s.size > 0 else float("nan")

    def bs_item_value(self, item: str, average: bool = True) -> float:
        return self._average_last_k_quarterly(item) if average else self._latest_quarterly_value(item)

    def bs_item_points(self, item: str, average: bool = True, tolerance_days: int = 0) -> pd.Series:
        s_annual = self._annual_item_series(item).dropna()
        if s_annual.empty:
            ltm_val = self.bs_item_value(item, average=average)
            as_of_date = get_current_timestamp(self._as_of)
            if np.isnan(ltm_val):
                return pd.Series(dtype=float, name=item)
            return pd.Series([ltm_val], index=pd.Index([as_of_date]), name=item)

        s_annual = s_annual.iloc[:4]
        out = s_annual.copy()
        if self.is_financials_stale(tolerance_days=tolerance_days, require_distinct_from_annual=True):
            ltm_val = self.bs_item_value(item, average=average)
            as_of_date = get_current_timestamp(self._as_of)
            if not np.isnan(ltm_val):
                out = pd.concat([pd.Series([ltm_val], index=[as_of_date], name=item), out])
        out.name = item
        return out

    def _annual_item_series_generic(self, statement: Statement, item: str) -> pd.Series:
        df = self._get_statement_df(statement, "ANNUAL")
        df = _coerce_datetime_columns(df)
        if df.empty or item not in df.index:
            return pd.Series(dtype=float, name=item)
        s = df.loc[item].dropna().iloc[:4]
        s.name = item
        return s

    def _pick_item_from_alias(self, statement: Statement, candidates: List[str]) -> Optional[str]:
        statement_name = statement.lower()
        df_ann = _coerce_datetime_columns(self._get_statement_df(statement_name, "ANNUAL"))
        for candidate_row_name in candidates:
            if not df_ann.empty and candidate_row_name in df_ann.index:
                return candidate_row_name
        return None

    def _ttm_item_value(self, statement: Statement, item: str) -> float:
        st = statement.lower()
        if st == "balance_sheet":
            return float("nan")

        ttm_dataframe = self._get_statement_df(st, "TTM")
        ttm_dataframe = _coerce_datetime_columns(ttm_dataframe) if not ttm_dataframe.empty else ttm_dataframe
        if ttm_dataframe.empty or item not in ttm_dataframe.index:
            return 0.0
        row = ttm_dataframe.loc[item].dropna()
        return float(row.iloc[0]) if not row.empty else 0.0

    def get_statement_item_points(self, alias_mapping: dict, average: bool = True, tolerance_days: int = 0) -> pd.Series:
        """
        Resolve an alias mapping from FINANCIALS:
          alias_mapping = {"source": <statement>, "fields": [candidate rows], "fancy_name": "..."}
        Build a short Series of annual points (optionally prepending a “LTM-like” point when stale).
        """
        statement_name = str(alias_mapping.get("source", "")).lower()
        candidate_row_names = _ensure_list(alias_mapping.get("fields", []))

        if not statement_name or not candidate_row_names:
            fallback_name = candidate_row_names[0] if candidate_row_names else "UNKNOWN_ITEM"
            return pd.Series(dtype=float, name=fallback_name)

        resolved_row_name = self._pick_item_from_alias(statement_name, candidate_row_names)
        if resolved_row_name is None:
            fallback_name = candidate_row_names[0]
            return pd.Series(dtype=float, name=fallback_name)

        if statement_name == "balance_sheet":
            return self.bs_item_points(item=resolved_row_name, average=average, tolerance_days=tolerance_days)

        s_annual = self._annual_item_series_generic(statement_name, resolved_row_name).fillna(0)
        if s_annual.empty:
            return pd.Series(dtype=float, name=resolved_row_name)

        out = s_annual.copy()
        if self.is_financials_stale(tolerance_days=tolerance_days, require_distinct_from_annual=True):
            ttm_val = self._ttm_item_value(statement_name, resolved_row_name)
            if not np.isnan(ttm_val):
                as_of_date = get_current_timestamp(self._as_of)
                out = pd.concat([pd.Series([ttm_val], index=[as_of_date], name=resolved_row_name), out])

        out.name = resolved_row_name
        return out

    # ============================================================
    # Metrics (Series outputs)
    # ============================================================
    def get_beta(self) -> Optional[float]:
        if self.beta is not None:
            return self.beta

        from core.constants import ETF_DICT
        if self.country not in ETF_DICT:
            etf_ticker = "VOO"
        else:
            etf_ticker = ETF_DICT[self.country]

        paired_price = yf.download(
            tickers=[self.ticker, etf_ticker],
            interval="1mo",
            period="5y",
            progress=False,
        )

        stock_block = _slice_ticker_block(paired_price, self.ticker)
        etf_block = _slice_ticker_block(paired_price, etf_ticker)

        stock_close = _extract_close_series(stock_block)
        etf_close = _extract_close_series(etf_block)

        stock_ret = _pct_ret(stock_close)
        etf_ret = _pct_ret(etf_close)

        aligned = pd.concat(
            [stock_ret.rename("stock"), etf_ret.rename("etf")],
            axis=1,
        ).dropna()

        aligned = aligned[np.isfinite(aligned["stock"]) & np.isfinite(aligned["etf"])]

        if aligned.shape[0] < 12:
            self.beta = None
            return None

        aligned["stock"] = _winsorize(aligned["stock"])
        aligned["etf"] = _winsorize(aligned["etf"])

        var_etf = aligned["etf"].var(ddof=1)
        cov_se = aligned[["stock", "etf"]].cov(ddof=1).iloc[0, 1]

        beta = float(cov_se / var_etf)
        self.beta = beta
        return beta

    def compute_beneish_m(self) -> pd.Series:
        columns = self.total_assets.index

        if len(columns) == 0:
            return pd.Series(dtype=float, name="beneish_m")

        pre_accounts_receivable = _safe_shift(self.accounts_receivable, n=-1)
        pre_total_revenue = _safe_shift(self.total_revenue, n=-1)
        nom = _safe_div(self.accounts_receivable, self.total_revenue)
        denom = _safe_div(pre_accounts_receivable, pre_total_revenue)
        dsri = _safe_div(nom, denom)

        gross_margin = _safe_div(self.gross_profit, self.total_revenue)
        pre_gross_margin = _safe_shift(gross_margin, n=-1)
        gmi = _safe_div(pre_gross_margin, gross_margin)

        asset_quality = 1 - _safe_div(
            _safe_minus(_safe_add(self.current_assets, self.net_ppe), self.other_properties),
            self.total_assets,
        )
        pre_asset_quality = _safe_shift(asset_quality, n=-1)
        aqi = _safe_div(asset_quality, pre_asset_quality)

        sgi = _safe_div(self.total_revenue, pre_total_revenue)

        depreciation_rate = _safe_div(
            self.depreciation_amortization_depletion,
            _safe_minus(_safe_add(self.depreciation_amortization_depletion, self.net_ppe), self.other_properties),
        )
        pre_depreciation_rate = _safe_shift(depreciation_rate, n=-1)
        depi = _safe_div(depreciation_rate, pre_depreciation_rate)

        nom = _safe_div(self.sga, self.total_revenue)
        pre_sga_expense = _safe_shift(self.sga, n=-1)
        denom = _safe_div(pre_sga_expense, pre_total_revenue)
        sgai = _safe_div(nom, denom)

        leverage = _safe_div(_safe_add(self.current_liabilities, self.long_debt), self.total_assets)
        pre_leverage = _safe_shift(leverage, n=-1)
        lvgi = _safe_div(leverage, pre_leverage)

        tata = _safe_div(_safe_minus(self.net_income, self.operating_cashflow), self.total_assets)

        beneish_m = (
            -4.84
            + 0.920 * dsri
            + 0.528 * gmi
            + 0.404 * aqi
            + 0.892 * sgi
            + 0.115 * depi
            - 0.172 * sgai
            + 4.679 * tata
            - 0.327 * lvgi
        ).rename("beneish_m")

        if len(beneish_m) > 0:
            beneish_m.iloc[-1] = np.nan

        return beneish_m

    def compute_altman_z(self) -> pd.Series:
        columns = self.total_assets.index

        if len(columns) == 0:
            return pd.Series(dtype=float, name="altman_z")

        X1 = _safe_div(self.working_capital, self.total_assets)
        X2 = _safe_div(self.retained_earnings, self.total_assets)
        X3 = _safe_div(self.ebit, self.total_assets)
        X4 = _safe_div(self.market_cap, self.total_liabilities)
        X5 = _safe_div(self.total_revenue, self.total_assets)

        altman_z = (1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5).rename("altman_z")
        return altman_z

    def to_payload(self) -> Dict[str, Any]:
        """
        Build a single payload dict aggregating:
          - basic_information (per STOCK_INFO aliases)
          - prices (date, close, volume)
          - financial_points (per FINANCIALS aliases)
          - derived_metrics (all computed series + relevant scalars)
          - key_ratios (pre-baked overview card entries)
          - news
          - officers
        """
        from core.constants import DERIVED_METRICS, FINANCIALS, STOCK_INFO, KEY_RATIO_DICT

        def series_to_mapping(s: pd.Series) -> Dict[str, float]:
            if isinstance(s.index, pd.DatetimeIndex):
                return {ts.date().isoformat(): float(v) for ts, v in s.items()}
            return {str(idx): float(v) for idx, v in s.items()}

        # --- basic information (as defined by STOCK_INFO) ---
        basic_information = {entry["alias"]: self.info_fields.get(entry["alias"]) for entry in STOCK_INFO}

        # --- prices (Close, Volume) ---
        price_rows = []
        for dt, row in self.prices.iterrows():
            price_rows.append(
                {
                    "date": (dt.date().isoformat() if isinstance(dt, (pd.Timestamp,)) else str(dt)),
                    "close": float(row.get("Close", np.nan)),
                    "volume": float(row.get("Volume", np.nan)),
                }
            )

        # --- financial_points (alias -> {date: value}) ---
        financial_points: Dict[str, Dict[str, float]] = {}
        for alias_name in FINANCIALS.keys():
            points_series = self.statement_points.get(alias_name, pd.Series(dtype=float, name=alias_name))
            financial_points[alias_name] = series_to_mapping(points_series)

        # --- derived metrics (build from metadata for consistency) ---
        derived_metrics: Dict[str, Any] = {}
        for var_name, meta in DERIVED_METRICS.items():
            kind = meta.get("kind", "scalar")
            if kind == "series":
                series_obj = getattr(self, var_name, None)
                derived_metrics[var_name] = series_to_mapping(series_obj) if isinstance(series_obj, pd.Series) else {}
            else:
                if var_name == "dividend_per_share_cagr":
                    value = float(self.dividend_per_share_cagr) if self.dividend_per_share_cagr is not None else None
                else:
                    value = getattr(self, var_name, None)
                derived_metrics[var_name] = value

        # --- key ratios (drives the “Key Ratio” card in the UI) ---
        key_ratios: list[dict[str, Any]] = []
        for alias_name, meta in KEY_RATIO_DICT.items():
            attr = meta.get("attr")
            kind = meta.get("kind", "scalar")
            fancy_name = meta.get("fancy_name", alias_name)
            fmt = meta.get("format", "raw")

            raw_value: Any = None
            if kind == "scalar":
                raw_value = getattr(self, attr, None)
            elif kind == "series_latest":
                series_obj = getattr(self, attr, None)
                if isinstance(series_obj, pd.Series) and not series_obj.dropna().empty:
                    raw_value = float(series_obj.dropna().iloc[0])
                else:
                    raw_value = np.nan
            else:
                raw_value = getattr(self, attr, None)

            key_ratios.append(
                {
                    "key": alias_name,
                    "fancy_name": fancy_name,
                    "value": raw_value,
                    "format": fmt,  # money | ratio | raw
                }
            )

        # --- assemble payload ---
        payload: Dict[str, Any] = {
            "as_of": self._as_of.isoformat(),
            "basic_information": basic_information,
            "prices": price_rows,
            "financial_points": financial_points,
            "derived_metrics": derived_metrics,
            "key_ratios": key_ratios,
            "news": self.news,
            "officers": self.officers,
        }
        return payload

