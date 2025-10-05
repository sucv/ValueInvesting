from __future__ import annotations

from typing import Dict, Any
import numpy as np
import pandas as pd

from core.constants import SECTOR_PE_RATIO, INDUSTRIAL_NPM_RATIO, CRITERION
from core.stock import Stock
from core.macros import MacroEconomic
from utils.stock import _safe_yoy_growth, _safe_cagr, _safe_mean, _safe_minus, _safe_div
from utils.evaluation import _mann_kendall


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
            "inputs": <pd.Series or pd.DataFrame>,  # NEW: raw input data
            "outputs": {... user-facing scalar values ...},
            "check": 1.0 or 0.0,
          }
    """

    def __init__(self, stock: Stock, macros: MacroEconomic):
        self.stock = stock
        self.macros = macros

    # -------------------------
    # Internal utilities
    # -------------------------
    @staticmethod
    def _safe_latest_scalar_from_series(pandas_series: pd.Series) -> float:
        """Return the first element of a Series safely."""
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
            inputs: Any,  # NEW: can be Series or DataFrame
            outputs: Dict[str, Any],
            check_float: float,
    ) -> Dict[str, Any]:
        result_template = CRITERION[category_key][signal_key].copy()
        result_template.update(
            {
                "category": category_key,
                "name": signal_key,
                "inputs": inputs,  # NEW
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

        # Free cash flow
        tau, p_value = _mann_kendall(self.stock.free_cashflow)
        results["free_cashflow"] = self._make_result(
            category,
            "free_cashflow",
            inputs=self.stock.free_cashflow,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # Cash and equivalents
        tau, p_value = _mann_kendall(self.stock.cash_and_equivalents)
        results["cash_and_equivalents"] = self._make_result(
            category,
            "cash_and_equivalents",
            inputs=self.stock.cash_and_equivalents,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # EPS
        tau, p_value = _mann_kendall(self.stock.earning_per_share)
        results["earning_per_share"] = self._make_result(
            category,
            "earning_per_share",
            inputs=self.stock.earning_per_share,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # BVPS
        tau, p_value = _mann_kendall(self.stock.book_value_per_share)
        results["book_value_per_share"] = self._make_result(
            category,
            "book_value_per_share",
            inputs=self.stock.book_value_per_share,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # Net profit margin
        tau, p_value = _mann_kendall(self.stock.net_profit_margin)
        results["net_profit_margin"] = self._make_result(
            category,
            "net_profit_margin",
            inputs=self.stock.net_profit_margin,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # ROE
        tau, p_value = _mann_kendall(self.stock.return_on_equity)
        results["return_on_equity"] = self._make_result(
            category,
            "return_on_equity",
            inputs=self.stock.return_on_equity,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        return results

    # ----------------
    # PRESENT (levels)
    # ----------------
    def present_check(self) -> Dict[str, Dict[str, Any]]:
        category = "present"
        results: Dict[str, Dict[str, Any]] = {}

        # Enterprise profit
        enterprise_profit_latest_value = self._safe_latest_scalar_from_series(self.stock.enterprise_profit)
        results["enterprise_profits"] = self._make_result(
            category,
            "enterprise_profits",
            inputs=self.stock.enterprise_profit,
            outputs={"Enterprise Profit": enterprise_profit_latest_value},
            check_float=1.0 if (enterprise_profit_latest_value > 0 and enterprise_profit_latest_value >= 0.18) else 0.0,
        )

        # Price to book
        price_to_book_latest_value = self._safe_latest_scalar_from_series(self.stock.price_to_book)

        results["price_to_book"] = self._make_result(
            category,
            "price_to_book",
            inputs=self.stock.price_to_book,
            outputs={"Price To Book": price_to_book_latest_value},
            check_float=1.0 if (isinstance(price_to_book_latest_value, (int, float)) and
                                0 < price_to_book_latest_value <= 3.0) else 0.0,
        )

        # PEG ratio
        peg_ratio_latest_value = self._safe_latest_scalar_from_series(self.stock.trailing_peg_ratio)
        results["peg_ratio"] = self._make_result(
            category,
            "peg_ratio",
            inputs=self.stock.trailing_peg_ratio,
            outputs={"PEG Ratio": peg_ratio_latest_value},
            check_float=1.0 if (isinstance(peg_ratio_latest_value, (int, float)) and
                                0 < peg_ratio_latest_value <= 1.0) else 0.0,
        )

        # ROE
        return_on_equity_latest_value = self._safe_latest_scalar_from_series(self.stock.return_on_equity)
        results["return_on_equity"] = self._make_result(
            category,
            "return_on_equity",
            inputs=self.stock.return_on_equity,
            outputs={"Return On Equity": return_on_equity_latest_value},
            check_float=1.0 if (isinstance(return_on_equity_latest_value, (int, float)) and
                                return_on_equity_latest_value >= 0.15) else 0.0,
        )

        # PE vs industry
        industry_pe_cap_value = SECTOR_PE_RATIO[self.stock.sector]
        price_to_earning_latest_value = self._safe_latest_scalar_from_series(self.stock.price_to_earning)
        results["price_earning"] = self._make_result(
            category,
            "price_earning",
            inputs=self.stock.price_to_earning,
            outputs={
                "Price To Earnings": price_to_earning_latest_value,
                "Industry Benchmark PE": industry_pe_cap_value
            },
            check_float=1.0 if (isinstance(price_to_earning_latest_value, (int, float)) and
                                0 < price_to_earning_latest_value < industry_pe_cap_value) else 0.0,
        )

        # Net profit margin vs industry
        industry_net_profit_margin_floor_value = INDUSTRIAL_NPM_RATIO[self.stock.industry]["net_margin"]
        net_profit_margin_latest_value = self._safe_latest_scalar_from_series(self.stock.net_profit_margin)
        results["net_profit_margin"] = self._make_result(
            category,
            "net_profit_margin",
            inputs=self.stock.net_profit_margin,
            outputs={
                "Net Profit Margin": net_profit_margin_latest_value,
                "Industry Average Net Margin": industry_net_profit_margin_floor_value
            },
            check_float=1.0 if (isinstance(net_profit_margin_latest_value, (int, float)) and
                                net_profit_margin_latest_value > industry_net_profit_margin_floor_value) else 0.0,
        )

        return results

    # ----------------------------
    # FUTURE (momentum vs average)
    # ----------------------------
    def future_check(self) -> Dict[str, Dict[str, Any]]:
        category = "future"
        results: Dict[str, Dict[str, Any]] = {}

        def compute_momentum(pandas_series: pd.Series, signal_key: str) -> None:
            yoy_growth_series = _safe_yoy_growth(pandas_series)
            latest_growth_value = self._safe_latest_scalar_from_series(yoy_growth_series)
            average_growth_value = float(yoy_growth_series.mean()) if isinstance(yoy_growth_series,
                                                                                 pd.Series) and not yoy_growth_series.empty else np.nan

            # Multi-input: original series + YoY growth
            momentum_inputs = pd.DataFrame({
                "original": pandas_series,
                "yoy_growth": yoy_growth_series,
            })

            results[signal_key] = self._make_result(
                category,
                signal_key,
                inputs=momentum_inputs,
                outputs={
                    "Latest YoY Growth": latest_growth_value,
                    "Average YoY Growth": average_growth_value
                },
                check_float=1.0 if (isinstance(latest_growth_value, (int, float)) and
                                    isinstance(average_growth_value, (int, float)) and
                                    latest_growth_value > average_growth_value) else 0.0,
            )

        compute_momentum(self.stock.free_cashflow, "free_cashflow")
        compute_momentum(self.stock.cash_and_equivalents, "cash_and_equivalents")
        compute_momentum(self.stock.earning_per_share, "earning_per_share")
        compute_momentum(self.stock.book_value_per_share, "book_value_per_share")
        compute_momentum(self.stock.net_profit_margin, "net_profit_margin")
        compute_momentum(self.stock.return_on_equity, "return_on_equity")

        return results

    # -------------
    # HEALTH (risk)
    # -------------
    def health_check(self) -> Dict[str, Dict[str, Any]]:
        category = "health"
        results: Dict[str, Dict[str, Any]] = {}

        # Current ratio
        current_ratio_latest_value = self._safe_latest_scalar_from_series(self.stock.current_ratio)
        results["current_ratio"] = self._make_result(
            category,
            "current_ratio",
            inputs=self.stock.current_ratio,
            outputs={"Current Ratio": current_ratio_latest_value},
            check_float=1.0 if (isinstance(current_ratio_latest_value, (int, float)) and
                                current_ratio_latest_value >= 1.5) else 0.0,
        )

        # Debt to equity
        debt_to_equity_latest_value = self._safe_latest_scalar_from_series(self.stock.debt_to_equity)
        results["debt_to_equity"] = self._make_result(
            category,
            "debt_to_equity",
            inputs=self.stock.debt_to_equity,
            outputs={"Debt To Equity": debt_to_equity_latest_value},
            check_float=1.0 if (isinstance(debt_to_equity_latest_value, (int, float)) and
                                debt_to_equity_latest_value <= 0.5) else 0.0,
        )

        # Beneish M
        beneish_m_latest_value = self._safe_latest_scalar_from_series(self.stock.beneish_m)
        results["beneish_m"] = self._make_result(
            category,
            "beneish_m",
            inputs=self.stock.beneish_m,
            outputs={"Beneish M Score": beneish_m_latest_value},
            check_float=1.0 if (isinstance(beneish_m_latest_value, (int, float)) and
                                beneish_m_latest_value <= -2.22) else 0.0,
        )

        # Altman Z
        altman_z_latest_value = self._safe_latest_scalar_from_series(self.stock.altman_z)
        results["altman_z"] = self._make_result(
            category,
            "altman_z",
            inputs=self.stock.altman_z,
            outputs={"Altman Z Score": altman_z_latest_value},
            check_float=1.0 if (isinstance(altman_z_latest_value, (int, float)) and
                                altman_z_latest_value >= 1.80) else 0.0,
        )

        # Net insider purchases (scalar, not series)
        net_insider_purchases_value = self.stock.net_insider_purchases
        results["net_insider_purchases"] = self._make_result(
            category,
            "net_insider_purchases",
            inputs=pd.Series([net_insider_purchases_value], name="net_insider_purchases"),
            outputs={"Net Insider Purchases": net_insider_purchases_value},
            check_float=1.0 if net_insider_purchases_value >= -0.10 else 0.0,
        )

        # Debt coverage (multi-input)
        operating_cashflow_latest_value = self._safe_latest_scalar_from_series(self.stock.operating_cashflow)
        total_liabilities_latest_value = self._safe_latest_scalar_from_series(self.stock.total_liabilities)
        debt_coverage_inputs = pd.DataFrame({
            "operating_cashflow": self.stock.operating_cashflow,
            "total_liabilities": self.stock.total_liabilities,
        })
        results["debt_coverage"] = self._make_result(
            category,
            "debt_coverage",
            inputs=debt_coverage_inputs,
            outputs={
                "Operating Cash Flow": operating_cashflow_latest_value,
                "Total Liabilities": total_liabilities_latest_value
            },
            check_float=1.0 if (
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

        # Dividend presence
        last_five_non_zero = (dividend_per_share_series.iloc[:5] != 0).all() if isinstance(dividend_per_share_series,
                                                                                           pd.Series) else False
        results["dividend"] = self._make_result(
            category,
            "dividend",
            inputs=dividend_per_share_series,
            outputs={"Dividends Paid In Last Five Years": bool(last_five_non_zero)},
            check_float=1.0 if last_five_non_zero else 0.0,
        )

        # Dividend yield
        dividend_yield_latest_value = self._safe_latest_scalar_from_series(self.stock.dividend_yield)
        results["dividend_yield"] = self._make_result(
            category,
            "dividend_yield",
            inputs=self.stock.dividend_yield,
            outputs={"Dividend Yield": dividend_yield_latest_value},
            check_float=1.0 if (isinstance(dividend_yield_latest_value, (int, float)) and
                                dividend_yield_latest_value > 0.015) else 0.0,
        )

        # Dividend streak
        has_any_zero_year = (dividend_per_share_series == 0).any() if isinstance(dividend_per_share_series,
                                                                                 pd.Series) else True
        dividend_streak_ok = not has_any_zero_year
        results["dividend_streak"] = self._make_result(
            category,
            "dividend_streak",
            inputs=dividend_per_share_series,
            outputs={"Any Zero Dividend Year": bool(has_any_zero_year)},
            check_float=1.0 if dividend_streak_ok else 0.0,
        )

        # Dividend volatility
        yoy_dividend_series = _safe_yoy_growth(dividend_per_share_series)
        has_drop_ge_10pct = (yoy_dividend_series <= -0.10).any() if isinstance(yoy_dividend_series, pd.Series) else True
        dividend_volatile_inputs = pd.DataFrame({
            "dividend_per_share": dividend_per_share_series,
            "yoy_growth": yoy_dividend_series,
        })
        results["dividend_volatile"] = self._make_result(
            category,
            "dividend_volatile",
            inputs=dividend_volatile_inputs,
            outputs={"Any Dividend Drop At Least 10 Percent": bool(has_drop_ge_10pct)},
            check_float=1.0 if (not has_drop_ge_10pct and last_five_non_zero) else 0.0,
        )

        # Dividend trend
        tau, p_value = _mann_kendall(dividend_per_share_series)
        results["dividend_trend"] = self._make_result(
            category,
            "dividend_trend",
            inputs=dividend_per_share_series,
            outputs={"Kendall Tau": tau, "P Value": p_value},
            check_float=1.0 if (tau > 0 and p_value < 0.10) else 0.0,
        )

        # Dividend payout ratio
        payout_ratio_median_value = self.stock.dividend_payout_ratio.median()
        results["dividend_payout_ratio"] = self._make_result(
            category,
            "dividend_payout_ratio",
            inputs=self.stock.dividend_payout_ratio,
            outputs={"Median Payout Ratio": payout_ratio_median_value},
            check_float=1.0 if (isinstance(payout_ratio_median_value, (int, float)) and
                                0.0 < payout_ratio_median_value < 0.60) else 0.0,
        )

        return results

        # ------------
        # MACRO (host)
        # ------------

    def macro_economic_check(self) -> Dict[str, Dict[str, Any]]:
        category = "macroeconomics"
        results: Dict[str, Dict[str, Any]] = {}

        # GDP momentum
        average_three_year_country_gdp = _safe_mean(self.macros.country_real_gdp_growth, n=3)
        average_ten_year_country_gdp = _safe_mean(self.macros.country_real_gdp_growth, n=10)
        average_three_year_world_gdp = _safe_mean(self.macros.world_real_gdp_growth, n=3)
        latest_country_gdp = _safe_mean(self.macros.country_real_gdp_growth, n=1)

        momentum_baseline = max(average_ten_year_country_gdp, average_three_year_world_gdp)
        momentum_ok = (average_three_year_country_gdp >= momentum_baseline) and (latest_country_gdp >= 0.0)

        # Multi-input: country and world GDP
        momentum_inputs = pd.DataFrame({
            "country_gdp": self.macros.country_real_gdp_growth,
            "world_gdp": self.macros.world_real_gdp_growth,
        })

        results["momentum"] = self._make_result(
            category,
            "momentum",
            inputs=momentum_inputs,
            outputs={
                "Country GDP Growth (Latest 3-yr)": average_three_year_country_gdp,
                "World GDP Growth (Latest 3-yr)": momentum_baseline,
                "Latest Real GDP Growth": latest_country_gdp,
            },
            check_float=1.0 if momentum_ok else 0.0,
        )

        # Inflation stability
        latest_cpi = _safe_mean(self.macros.country_inflation_cpi, n=1)
        cpi_5yr = self.macros.country_inflation_cpi.iloc[:5]
        std_dev_five_year_cpi = float(cpi_5yr.std()) if not cpi_5yr.empty else np.nan

        inflation_ok = (latest_cpi <= 0.05) and (std_dev_five_year_cpi <= 3.0)

        results["inflation_stability"] = self._make_result(
            category,
            "inflation_stability",
            inputs=self.macros.country_inflation_cpi,
            outputs={
                "Latest CPI Inflation": latest_cpi,
                "Standard Deviation Of CPI (Latest 5-yr)": std_dev_five_year_cpi
            },
            check_float=1.0 if inflation_ok else 0.0,
        )

        # Real interest rate
        real_rate_series = self.macros.country_real_interest_rate
        real_rate_value = _safe_mean(real_rate_series, n=1)

        check_float_value = 0.0
        if not np.isnan(real_rate_value):
            real_rate_ok = (-2.0 < real_rate_value < 6.0)
            if real_rate_ok:
                check_float_value = 1.0

        # Multi-input: lending rate and inflation (components of real rate)
        real_rate_inputs = pd.DataFrame({
            "lending_rate": self.macros.country_lending_rate,
            "inflation_cpi": self.macros.country_inflation_cpi,
            "real_rate": real_rate_series,
        }).sort_index(ascending=False)

        results["real_interest_rate"] = self._make_result(
            category,
            "real_interest_rate",
            inputs=real_rate_inputs,
            outputs={"Real Interest Rate": real_rate_value},
            check_float=check_float_value,
        )

        # FX trend
        fx_cagr_percent_per_year = _safe_cagr(self.macros.country_fx_ratio, n_year=3) * 100.0
        fx_ok = fx_cagr_percent_per_year <= 5.0

        results["fx_trend"] = self._make_result(
            category,
            "fx_trend",
            inputs=self.macros.country_fx_ratio,
            outputs={" FX CAGR Percent Per Year (Latest 3-yr)": fx_cagr_percent_per_year},
            check_float=1.0 if fx_ok else 0.0,
        )

        # External balance
        latest_current_account = _safe_mean(self.macros.country_current_account_gdp, n=1)
        average_five_year_current_account = _safe_mean(self.macros.country_current_account_gdp, n=5)

        external_ok = (latest_current_account >= -3.0) and (latest_current_account >= average_five_year_current_account)

        results["external_balance"] = self._make_result(
            category,
            "external_balance",
            inputs=self.macros.country_current_account_gdp,
            outputs={
                "Latest Current Account Balance": latest_current_account,
                "Average Current Account Balance (Latest 5-yr)": average_five_year_current_account
            },
            check_float=1.0 if external_ok else 0.0,
        )

        # Fiscal sustainability
        latest_debt = _safe_mean(self.macros.country_gov_debt_gdp, n=1)
        fiscal_ok = latest_debt <= 0.80

        results["fiscal_sustainability"] = self._make_result(
            category,
            "fiscal_sustainability",
            inputs=self.macros.country_gov_debt_gdp,
            outputs={"Latest Government Debt To GDP": latest_debt},
            check_float=1.0 if fiscal_ok else 0.0,
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