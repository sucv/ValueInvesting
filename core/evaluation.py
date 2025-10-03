# core/evaluation.py
from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd

from core.constants import SECTOR_PE_RATIO, INDUSTRIAL_NPM_RATIO, CRITERION
from core.stock import Stock
from core.macros import MacroEconomic
from utils.stock import _safe_yoy_growth  # Series-first version
from utils.evaluation import _mann_kendall  # Series-first Mann–Kendall


class Evaluator:
    """
    Evaluator computes checklist-aligned signals, formats them using the CRITERION
    metadata, and returns a uniform result dictionary for each category.

    Conventions:
      - All financial series are ordered latest → older.
      - Each check produces:
          {
            ...<CRITERION fields>...,
            "category": "<category_name>",
            "name": "<signal_key>",
            "outputs": {... user-facing scalar values ...},
            "check": 1.0 or 0.0,
          }
    """

    def __init__(self, stock: Stock, macros: MacroEconomic):
        self.stock = stock
        self.macros = macros

    # -------------------------
    # Internal small utilities
    # -------------------------
    @staticmethod
    def _safe_latest_scalar_from_series(pandas_series: pd.Series) -> float:
        """
        Return the first element of a Series safely.
        If the series is None, empty, or cannot be indexed with .iloc[0], return np.nan.
        Using .iloc[0] avoids the 'label 0' vs 'position 0' ambiguity that crashes when
        the index contains no label 0 or when the series length is 0.
        """
        try:
            if isinstance(pandas_series, pd.Series) and not pandas_series.empty:
                return pandas_series.iloc[0]
        except Exception:
            pass
        return np.nan

    def _make_result(
        self,
        category_key: str,
        signal_key: str,
        outputs: Dict[str, Any],
        check_float: float,
    ) -> Dict[str, Any]:
        result_template = CRITERION[category_key][signal_key].copy()
        result_template.update(
            {
                "category": category_key,
                "name": signal_key,
                "outputs": outputs,
                "check": float(check_float),
            }
        )
        return result_template

    # -------------
    # PAST (trends)
    # -------------
    def past_check(self) -> Dict[str, Dict[str, Any]]:
        category = "past"
        results: Dict[str, Dict[str, Any]] = {}

        tau, p_value = _mann_kendall(self.stock.free_cashflow)
        results["free_cashflow"] = self._make_result(
            category,
            "free_cashflow",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        tau, p_value = _mann_kendall(self.stock.cash_and_equivalents)
        results["cash_and_equivalents"] = self._make_result(
            category,
            "cash_and_equivalents",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        tau, p_value = _mann_kendall(self.stock.earning_per_share)
        results["earning_per_share"] = self._make_result(
            category,
            "earning_per_share",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        tau, p_value = _mann_kendall(self.stock.book_value_per_share)
        results["book_value_per_share"] = self._make_result(
            category,
            "book_value_per_share",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        tau, p_value = _mann_kendall(self.stock.net_profit_margin)
        results["net_profit_margin"] = self._make_result(
            category,
            "net_profit_margin",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        tau, p_value = _mann_kendall(self.stock.return_on_equity)
        results["return_on_equity"] = self._make_result(
            category,
            "return_on_equity",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        return results

    # ----------------
    # PRESENT (levels)
    # ----------------
    def present_check(self) -> Dict[str, Dict[str, Any]]:
        category = "present"
        results: Dict[str, Dict[str, Any]] = {}

        enterprise_profit_latest_value = self._safe_latest_scalar_from_series(self.stock.enterprise_profit)
        results["enterprise_profits"] = self._make_result(
            category,
            "enterprise_profits",
            {"Enterprise Profit": enterprise_profit_latest_value},
            1.0 if (enterprise_profit_latest_value > 0 and enterprise_profit_latest_value >= 0.18) else 0.0,
        )

        current_price_value = self.stock.current_price
        book_value_per_share_latest_value = self._safe_latest_scalar_from_series(self.stock.book_value_per_share)
        price_to_book_value = (
            (current_price_value / book_value_per_share_latest_value)
            if (isinstance(book_value_per_share_latest_value, (int, float)) and np.isfinite(book_value_per_share_latest_value) and book_value_per_share_latest_value != 0)
            else np.nan
        )
        results["price_to_book"] = self._make_result(
            category,
            "price_to_book",
            {
                "Price To Book": price_to_book_value,
                "Current Price": current_price_value,
                "Book Value Per Share": book_value_per_share_latest_value,
            },
            1.0 if (isinstance(price_to_book_value, (int, float)) and price_to_book_value > 0 and price_to_book_value <= 3.0) else 0.0,
        )

        peg_ratio_latest_value = self._safe_latest_scalar_from_series(self.stock.trailing_peg_ratio)
        results["peg_ratio"] = self._make_result(
            category,
            "peg_ratio",
            {"PEG Ratio": peg_ratio_latest_value},
            1.0 if (isinstance(peg_ratio_latest_value, (int, float)) and peg_ratio_latest_value > 0 and peg_ratio_latest_value <= 1.0) else 0.0,
        )

        return_on_equity_latest_value = self._safe_latest_scalar_from_series(self.stock.return_on_equity)
        results["return_on_equity"] = self._make_result(
            category,
            "return_on_equity",
            {"Return On Equity": return_on_equity_latest_value},
            1.0 if (isinstance(return_on_equity_latest_value, (int, float)) and return_on_equity_latest_value >= 0.15) else 0.0,
        )

        industry_pe_cap_value = SECTOR_PE_RATIO[self.stock.sector]
        price_to_earning_latest_value = self._safe_latest_scalar_from_series(self.stock.price_to_earning)
        results["price_earning"] = self._make_result(
            category,
            "price_earning",
            {"Price To Earnings": price_to_earning_latest_value, "Industry Benchmark PE": industry_pe_cap_value},
            1.0 if (isinstance(price_to_earning_latest_value, (int, float)) and price_to_earning_latest_value > 0 and price_to_earning_latest_value < industry_pe_cap_value) else 0.0,
        )

        industry_net_profit_margin_floor_value = INDUSTRIAL_NPM_RATIO[self.stock.industry]["net_margin"]
        net_profit_margin_latest_value = self._safe_latest_scalar_from_series(self.stock.net_profit_margin)
        results["net_profit_margin"] = self._make_result(
            category,
            "net_profit_margin",
            {"Net Profit Margin": net_profit_margin_latest_value, "Industry Average Net Margin": industry_net_profit_margin_floor_value},
            1.0 if (isinstance(net_profit_margin_latest_value, (int, float)) and net_profit_margin_latest_value > industry_net_profit_margin_floor_value) else 0.0,
        )

        return results

    # ----------------------------
    # FUTURE (momentum vs average)
    # ----------------------------
    def future_check(self) -> Dict[str, Dict[str, Any]]:
        category = "future"
        results: Dict[str, Dict[str, Any]] = {}

        def compute_momentum(pandas_series: pd.Series, signal_key: str, pretty_label: str) -> None:
            yoy_growth_series = _safe_yoy_growth(pandas_series)
            latest_growth_value = self._safe_latest_scalar_from_series(yoy_growth_series)
            average_growth_value = float(yoy_growth_series.mean()) if isinstance(yoy_growth_series, pd.Series) and not yoy_growth_series.empty else np.nan
            results[signal_key] = self._make_result(
                category,
                signal_key,
                {"Latest YoY Growth": latest_growth_value, "Average YoY Growth": average_growth_value},
                1.0 if (isinstance(latest_growth_value, (int, float)) and isinstance(average_growth_value, (int, float)) and latest_growth_value > average_growth_value) else 0.0,
            )

        compute_momentum(self.stock.free_cashflow, "free_cashflow", "Free Cash Flow")
        compute_momentum(self.stock.cash_and_equivalents, "cash_and_equivalents", "Cash And Cash Equivalents")
        compute_momentum(self.stock.earning_per_share, "earning_per_share", "Earnings Per Share")
        compute_momentum(self.stock.book_value_per_share, "book_value_per_share", "Book Value Per Share")
        compute_momentum(self.stock.net_profit_margin, "net_profit_margin", "Net Profit Margin")
        compute_momentum(self.stock.return_on_equity, "return_on_equity", "Return On Equity")

        return results

    # -------------
    # HEALTH (risk)
    # -------------
    def health_check(self) -> Dict[str, Dict[str, Any]]:
        category = "health"
        results: Dict[str, Dict[str, Any]] = {}

        current_ratio_latest_value = self._safe_latest_scalar_from_series(self.stock.current_ratio)
        results["current_ratio"] = self._make_result(
            category,
            "current_ratio",
            {"Current Ratio": current_ratio_latest_value},
            1.0 if (isinstance(current_ratio_latest_value, (int, float)) and current_ratio_latest_value >= 1.5) else 0.0,
        )

        debt_to_equity_latest_value = self._safe_latest_scalar_from_series(self.stock.debt_to_equity)
        results["debt_to_equity"] = self._make_result(
            category,
            "debt_to_equity",
            {"Debt To Equity": debt_to_equity_latest_value},
            1.0 if (isinstance(debt_to_equity_latest_value, (int, float)) and debt_to_equity_latest_value <= 0.5) else 0.0,
        )

        beneish_m_latest_value = self._safe_latest_scalar_from_series(self.stock.beneish_m)
        results["beneish_m"] = self._make_result(
            category,
            "beneish_m",
            {"Beneish M Score": beneish_m_latest_value},
            1.0 if (isinstance(beneish_m_latest_value, (int, float)) and beneish_m_latest_value <= -2.22) else 0.0,
        )

        altman_z_latest_value = self._safe_latest_scalar_from_series(self.stock.altman_z)
        results["altman_z"] = self._make_result(
            category,
            "altman_z",
            {"Altman Z Score": altman_z_latest_value},
            1.0 if (isinstance(altman_z_latest_value, (int, float)) and altman_z_latest_value >= 1.80) else 0.0,
        )

        net_insider_purchases_value = self.stock.net_insider_purchases
        results["net_insider_purchases"] = self._make_result(
            category,
            "net_insider_purchases",
            {"Net Insider Purchases": net_insider_purchases_value},
            1.0 if net_insider_purchases_value >= -0.10 else 0.0,
        )

        operating_cashflow_latest_value = self._safe_latest_scalar_from_series(self.stock.operating_cashflow)
        total_liabilities_latest_value = self._safe_latest_scalar_from_series(self.stock.total_liabilities)
        results["debt_coverage"] = self._make_result(
            category,
            "debt_coverage",
            {"Operating Cash Flow": operating_cashflow_latest_value, "Total Liabilities": total_liabilities_latest_value},
            1.0 if (
                isinstance(operating_cashflow_latest_value, (int, float)) and
                isinstance(total_liabilities_latest_value, (int, float)) and
                operating_cashflow_latest_value > (0.20 * total_liabilities_latest_value)
            ) else 0.0,
        )

        return results

    # ----------------
    # DIVIDEND (policy)
    # ----------------
    def dividend_check(self) -> Dict[str, Dict[str, Any]]:
        category = "dividend"
        results: Dict[str, Dict[str, Any]] = {}

        dividend_per_share_series = self.stock.dividend_per_share_history

        last_five_non_zero = (dividend_per_share_series.iloc[:5] != 0).all() if isinstance(dividend_per_share_series, pd.Series) else False
        results["dividend"] = self._make_result(
            category,
            "dividend",
            {"Dividends Paid In Last Five Years": bool(last_five_non_zero)},
            1.0 if last_five_non_zero else 0.0,
        )

        dividend_yield_latest_value = self._safe_latest_scalar_from_series(self.stock.dividend_yield)
        results["dividend_yield"] = self._make_result(
            category,
            "dividend_yield",
            {"Dividend Yield": dividend_yield_latest_value},
            1.0 if (isinstance(dividend_yield_latest_value, (int, float)) and dividend_yield_latest_value > 0.015) else 0.0,
        )

        has_any_zero_year = (dividend_per_share_series == 0).any() if isinstance(dividend_per_share_series, pd.Series) else True
        dividend_streak_ok = not has_any_zero_year
        results["dividend_streak"] = self._make_result(
            category,
            "dividend_streak",
            {"Any Zero Dividend Year": bool(has_any_zero_year)},
            1.0 if dividend_streak_ok else 0.0,
        )

        yoy_dividend_series = _safe_yoy_growth(dividend_per_share_series)
        has_drop_ge_10pct = (yoy_dividend_series <= -0.10).any() if isinstance(yoy_dividend_series, pd.Series) else True
        results["dividend_volatile"] = self._make_result(
            category,
            "dividend_volatile",
            {"Any Dividend Drop At Least 10 Percent": bool(has_drop_ge_10pct)},
            1.0 if (not has_drop_ge_10pct and last_five_non_zero) else 0.0,
        )

        tau, p_value = _mann_kendall(dividend_per_share_series)
        results["dividend_trend"] = self._make_result(
            category,
            "dividend_trend",
            {"Kendall Tau": tau, "P Value": p_value},
            1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        payout_ratio_median_value = self.stock.dividend_payout_ratio.median()
        results["dividend_payout_ratio"] = self._make_result(
            category,
            "dividend_payout_ratio",
            {"Median Payout Ratio": payout_ratio_median_value},
            1.0 if (isinstance(payout_ratio_median_value, (int, float)) and payout_ratio_median_value > 0.0 and payout_ratio_median_value < 0.60) else 0.0,
        )

        return results

    # ------------
    # MACRO (host)
    # ------------
    def macro_economic_check(self) -> Dict[str, Dict[str, Any]]:
        category = "macroeconomics"
        results: Dict[str, Dict[str, Any]] = {}

        average_three_year_country_gdp = self.macros.ave3_country_gdp
        average_ten_year_country_gdp = self.macros.ave10_country_gdp
        average_three_year_world_gdp = self.macros.ave3_world_gdp
        latest_country_gdp = self.macros.latest_country_gdp
        momentum_baseline = max(average_ten_year_country_gdp, average_three_year_world_gdp)
        momentum_ok = (average_three_year_country_gdp >= momentum_baseline) and (latest_country_gdp >= 0.0)
        results["momentum"] = self._make_result(
            category,
            "momentum",
            {
                "Country Three Year Average Real GDP Growth": average_three_year_country_gdp,
                "Baseline Comparator Growth": momentum_baseline,
                "Latest Real GDP Growth": latest_country_gdp,
            },
            1.0 if momentum_ok else 0.0,
        )

        latest_cpi = self.macros.latest_inflation_cpi
        std_dev_five_year_cpi = self.macros.stdev5_country_inflation_cpi
        inflation_ok = (latest_cpi <= 0.05) and (std_dev_five_year_cpi <= 3.0)
        results["inflation_stability"] = self._make_result(
            category,
            "inflation_stability",
            {"Latest CPI Inflation": latest_cpi, "Five Year Standard Deviation Of CPI": std_dev_five_year_cpi},
            1.0 if inflation_ok else 0.0,
        )

        check_float_value = 0.0
        real_rate_value = self.macros.country_real_interests
        if real_rate_value is not None:
            real_rate_ok = (-2.0 < real_rate_value < 6.0)
            if real_rate_ok:
                check_float_value = 1.0
        results["real_interest_rate"] = self._make_result(
            category,
            "real_interest_rate",
            {"Real Interest Rate": real_rate_value},
            check_float_value,
        )

        fx_cagr_percent_per_year = self.macros.yearly_country_fx_cagr
        fx_ok = fx_cagr_percent_per_year <= 5.0
        results["fx_trend"] = self._make_result(
            category,
            "fx_trend",
            {"Three Year FX CAGR Percent Per Year": fx_cagr_percent_per_year},
            1.0 if fx_ok else 0.0,
        )

        latest_current_account = self.macros.latest_country_current_account
        average_five_year_current_account = self.macros.ave5_country_current_account
        external_ok = (latest_current_account >= -3.0) and (latest_current_account >= average_five_year_current_account)
        results["external_balance"] = self._make_result(
            category,
            "external_balance",
            {"Latest Current Account Balance": latest_current_account, "Five Year Average Current Account Balance": average_five_year_current_account},
            1.0 if external_ok else 0.0,
        )

        latest_debt = self.macros.latest_country_debt
        fiscal_ok = latest_debt <= 0.80
        results["fiscal_sustainability"] = self._make_result(
            category,
            "fiscal_sustainability",
            {"Latest Government Debt To GDP": latest_debt},
            1.0 if fiscal_ok else 0.0,
        )

        return results

    # ----------------
    # Convenience API
    # ----------------
    def run_all(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        return {
            "past": self.past_check(),
            "present": self.present_check(),
            "future": self.future_check(),
            "health": self.health_check(),
            "dividend": self.dividend_check(),
            "macroeconomics": self.macro_economic_check(),
        }
