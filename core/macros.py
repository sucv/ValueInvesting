from __future__ import annotations

from core.constants import try_iso3, WORLD_BANK_INDEX
from typing import Dict, Optional, List, Any
import numpy as np
import pandas as pd

from utils.stock import (
    _safe_minus,
    _safe_cagr,
    _safe_div,
    _safe_mean,
    _convert_year_value_list_to_series,
)

from utils.world_bank import wb_client

class MacroEconomic:
    """
    Series-native macro fetcher/aggregator.

    Contract:
      - All macro series are stored as pd.Series:
          name   = indicator_key (e.g., 'real_gdp_growth')
          index  = years as ints, ordered latest → older
          values = floats (NaN allowed)
    Public methods return floats / Optional[float] consistent with prior behavior.
    """

    def __init__(
        self,
        base_currency_country: str,
        country: str,
        macro_years: int,
        fx_years: int,
        current_account_years: int,
        inflation_years: int,
    ) -> None:
        self.base_currency_country = (base_currency_country or "").upper()
        self.country = country
        self.macro_years = max(5, int(macro_years))
        self.fx_years = int(fx_years)
        self.current_account_years = int(current_account_years)
        self.inflation_years = int(inflation_years)

        # Fetch then CONVERT list[(year, value)] -> Series (latest → older)
        self.country_macro: Dict[str, pd.Series] = self._fetch_and_convert_country_macro()
        self.world_macro: Dict[str, pd.Series] = self._fetch_and_convert_world_macro()

        # Payload
        self.latest_country_gdp = self.get_latest_country_gdp()
        self.ave3_country_gdp = self.get_ave3_country_gdp()
        self.ave3_world_gdp = self.get_ave3_world_gdp()
        self.ave10_country_gdp = self.get_ave10_country_gdp()

        self.latest_inflation_cpi = self.get_latest_country_inflation_cpi()
        self.stdev5_country_inflation_cpi = self.get_std5_country_inflation_cpi()

        self.country_real_interests = self.get_country_real_interests()

        self.yearly_country_fx_cagr = self.get_yearly_country_fx_cagr()

        self.latest_country_current_account = self.get_latest_country_current_account()
        self.ave5_country_current_account = self.get_ave5_country_current_account()

        self.latest_country_debt = self.get_latest_country_debt()
        self.latest_country_fiscal_balance = self.get_latest_country_fiscal_balance()

        self.count_debt_downtrend_flag = self.get_country_debt_downtrend_flag()

    # ---------------------------
    # ISO3
    # ---------------------------
    def get_country_iso3(self) -> Optional[str]:
        if self.country is None:
            return None
        iso3_code = try_iso3(self.country)
        if iso3_code is None:
            return None
        return iso3_code.upper()

    # ---------------------------
    # Fetchers with conversion to Series
    # ---------------------------
    def _fetch_and_convert_country_macro(self) -> Dict[str, pd.Series]:
        country_iso3_code = self.get_country_iso3()
        if not country_iso3_code:
            return {}

        indicator_keys_to_request = [
            WORLD_BANK_INDEX["real_gdp_growth"],
            WORLD_BANK_INDEX["inflation_cpi"],
            WORLD_BANK_INDEX["lending_rate"],
            WORLD_BANK_INDEX["fx_lcu_per_usd"],
            WORLD_BANK_INDEX["current_account_gdp"],
            WORLD_BANK_INDEX["gov_debt_gdp"],
            WORLD_BANK_INDEX["fiscal_balance_gdp"],
        ]

        raw_country_macros = wb_client(country_iso3_code, indicator_keys_to_request, mrv=self.macro_years)

        converted: Dict[str, pd.Series] = {}
        for indicator_key in indicator_keys_to_request:
            year_value_list = raw_country_macros.get(indicator_key, [])
            converted[indicator_key] = _convert_year_value_list_to_series(
                indicator_key=indicator_key,
                year_value_list=year_value_list,
                maximum_points=self.macro_years,
            )
        return converted

    def _fetch_and_convert_world_macro(self) -> Dict[str, pd.Series]:
        indicator_keys_to_request = [WORLD_BANK_INDEX["real_gdp_growth"]]
        raw_world_macros = wb_client("WLD", indicator_keys_to_request, mrv=self.macro_years)

        converted: Dict[str, pd.Series] = {}
        for indicator_key in indicator_keys_to_request:
            year_value_list = raw_world_macros.get(indicator_key, [])
            converted[indicator_key] = _convert_year_value_list_to_series(
                indicator_key=indicator_key,
                year_value_list=year_value_list,
                maximum_points=self.macro_years,
            )
        return converted

    # ---------------------------
    # Raw series getters (return Series)
    # ---------------------------
    def get_country_gdp(self) -> pd.Series:
        key = WORLD_BANK_INDEX["real_gdp_growth"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_country_inflation_cpi(self) -> pd.Series:
        key = WORLD_BANK_INDEX["inflation_cpi"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_country_lending_rate(self) -> pd.Series:
        key = WORLD_BANK_INDEX["lending_rate"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_country_fx_lcu_per_usd(self) -> pd.Series:
        key = WORLD_BANK_INDEX["fx_lcu_per_usd"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_base_country_fx_lcu_per_usd(self) -> pd.Series:
        """
        For non-USD base currency, fetch and convert base country's FX series to a Series.
        For USA base, return an empty Series.
        """
        key = WORLD_BANK_INDEX["fx_lcu_per_usd"]
        if self.base_currency_country == "USA":
            return pd.Series(dtype=float, name=key)

        raw_base_macros = wb_client(self.base_currency_country, [key], mrv=self.macro_years)
        base_year_value_list = raw_base_macros.get(key, [])
        base_fx_series = _convert_year_value_list_to_series(
            indicator_key=key,
            year_value_list=base_year_value_list,
            maximum_points=self.macro_years,
        )
        return base_fx_series

    def get_country_current_account_gdp(self) -> pd.Series:
        key = WORLD_BANK_INDEX["current_account_gdp"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_country_gov_debt_gdp(self) -> pd.Series:
        key = WORLD_BANK_INDEX["gov_debt_gdp"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_country_fiscal_balance_gdp(self) -> pd.Series:
        key = WORLD_BANK_INDEX["fiscal_balance_gdp"]
        return self.country_macro.get(key, pd.Series(dtype=float, name=key))

    def get_world_gdp(self) -> pd.Series:
        key = WORLD_BANK_INDEX["real_gdp_growth"]
        return self.world_macro.get(key, pd.Series(dtype=float, name=key))

    # ---------------------------
    # GDP summaries (reuse helpers directly)
    # ---------------------------
    def get_latest_country_gdp(self) -> float:
        return _safe_mean(self.get_country_gdp(), n=1)

    def get_ave3_country_gdp(self) -> float:
        s = self.get_country_gdp().iloc[:3]
        return _safe_mean(s, n=3)

    def get_ave3_world_gdp(self) -> float:
        s = self.get_world_gdp().iloc[:3]
        return _safe_mean(s, n=3)

    def get_ave10_country_gdp(self) -> float:
        s = self.get_country_gdp().iloc[:10]
        return _safe_mean(s, n=10)

    # ---------------------------
    # Inflation & rate summaries
    # ---------------------------
    def get_latest_country_inflation_cpi(self) -> float:
        return _safe_mean(self.get_country_inflation_cpi(), n=1)

    def get_std5_country_inflation_cpi(self) -> float:
        s = self.get_country_inflation_cpi().iloc[:5]
        arr = s.to_numpy()
        if arr.size == 0:
            return float("nan")
        return float(np.nanstd(arr))

    def get_country_real_interests(self) -> Optional[float]:
        """
        Latest (lending_rate - inflation_cpi) from Series helpers.
        """
        lending = self.get_country_lending_rate()
        infl = self.get_country_inflation_cpi()
        if lending.empty or infl.empty:
            return None
        real_rate = _safe_minus(lending, infl)
        latest = _safe_mean(real_rate, n=1)
        return None if np.isnan(latest) else float(latest)

    # ---------------------------
    # FX series & CAGR
    # ---------------------------
    def get_country_fx_series(self) -> pd.Series:
        """
        Return FX series as a Series:
          - If base currency is USA, return country FX LCU per USD as-is.
          - Otherwise, return (country_fx / base_fx) using _safe_div (index-aligned).
        """
        country_fx = self.get_country_fx_lcu_per_usd()
        if self.base_currency_country == "USA":
            return country_fx

        base_fx = self.get_base_country_fx_lcu_per_usd()
        if base_fx.empty:
            return country_fx

        fx_ratio = _safe_div(country_fx, base_fx)
        fx_ratio.name = "fx_cty_over_base"
        return fx_ratio

    def get_yearly_country_fx_cagr(self) -> Optional[float]:
        """
        CAGR of FX ratio (or FX vs USD) over self.fx_years, as percentage per year.
        """
        fx = self.get_country_fx_series()
        if fx.empty:
            return None
        cagr_decimal = _safe_cagr(fx, n_year=self.fx_years)
        if np.isnan(cagr_decimal):
            return None
        return float(cagr_decimal * 100.0)

    # ---------------------------
    # Current account, debt, fiscal balance
    # ---------------------------
    def get_latest_country_current_account(self) -> float:
        return _safe_mean(self.get_country_current_account_gdp(), n=1)

    def get_ave5_country_current_account(self) -> float:
        s = self.get_country_current_account_gdp().iloc[: self.current_account_years]
        return _safe_mean(s, n=self.current_account_years)

    def get_latest_country_debt(self) -> float:
        return _safe_mean(self.get_country_gov_debt_gdp(), n=1)

    def get_latest_country_fiscal_balance(self) -> float:
        return _safe_mean(self.get_country_fiscal_balance_gdp(), n=1)

    def get_country_debt_downtrend_flag(self) -> Optional[float]:
        """
        Return 1.0 if latest debt is lower than debt ~3 years ago, else 0.0.
        Return None if not computable.

        Index are years (int) ordered latest → older.
        """
        debt = self.get_country_gov_debt_gdp()
        if debt.empty or debt.size < 2:
            return None

        latest_value = _safe_mean(debt, n=1)
        if np.isnan(latest_value):
            return None

        year_index_desc: List[int] = list(debt.index)
        latest_year: int = int(year_index_desc[0])

        older_idx_pos: Optional[int] = None
        for pos in range(1, len(year_index_desc)):
            candidate_year = int(year_index_desc[pos])
            if candidate_year <= latest_year - 3:
                older_idx_pos = pos
                break

        if older_idx_pos is None and len(year_index_desc) >= 4:
            older_idx_pos = 3

        if older_idx_pos is None:
            return None

        older_value = float(debt.iloc[older_idx_pos])
        if np.isnan(older_value):
            return None

        return 1.0 if float(latest_value) < float(older_value) else 0.0

    def to_payload(self) -> Dict[str, Any]:
        """
        Build a macro payload with:
          - meta: basic identifiers and configuration horizons
          - series: raw country/world macro series (year->value)
          - derived_metrics: summarized scalars and derived series
        """
        def series_to_year_mapping(s: pd.Series) -> Dict[str, float]:
            # index is year (int) ordered latest → older
            return {str(idx): float(val) for idx, val in s.items()}

        # --- meta ---
        payload_meta: Dict[str, Any] = {
            "country": self.country,
            "country_iso3": self.get_country_iso3(),
            "base_currency_country": self.base_currency_country,
            "macro_years": self.macro_years,
            "fx_years": self.fx_years,
            "current_account_years": self.current_account_years,
            "inflation_years": self.inflation_years,
        }

        # --- raw country series ---
        real_gdp_growth_cty = self.get_country_gdp()
        inflation_cpi_cty = self.get_country_inflation_cpi()
        lending_rate_cty = self.get_country_lending_rate()
        fx_lcu_per_usd_cty = self.get_country_fx_lcu_per_usd()
        current_account_cty = self.get_country_current_account_gdp()
        gov_debt_gdp_cty = self.get_country_gov_debt_gdp()
        fiscal_balance_gdp_cty = self.get_country_fiscal_balance_gdp()

        series_country: Dict[str, Dict[str, float]] = {
            "real_gdp_growth": series_to_year_mapping(real_gdp_growth_cty),
            "inflation_cpi": series_to_year_mapping(inflation_cpi_cty),
            "lending_rate": series_to_year_mapping(lending_rate_cty),
            "fx_lcu_per_usd": series_to_year_mapping(fx_lcu_per_usd_cty),
            "current_account_gdp": series_to_year_mapping(current_account_cty),
            "gov_debt_gdp": series_to_year_mapping(gov_debt_gdp_cty),
            "fiscal_balance_gdp": series_to_year_mapping(fiscal_balance_gdp_cty),
        }

        # --- raw world series ---
        real_gdp_growth_world = self.get_world_gdp()
        series_world: Dict[str, Dict[str, float]] = {
            "real_gdp_growth": series_to_year_mapping(real_gdp_growth_world),
        }

        # --- derived series (FX ratio vs base) ---
        fx_ratio_series = self.get_country_fx_series()

        # --- derived metrics (scalars) ---
        derived_metrics: Dict[str, Any] = {
            # GDP summaries
            "latest_country_gdp": self.latest_country_gdp,
            "average_three_year_country_gdp": self.ave3_country_gdp,
            "average_three_year_world_gdp": self.ave3_world_gdp,
            "average_ten_year_country_gdp": self.ave10_country_gdp,

            # Inflation & rate summaries
            "latest_inflation_cpi": self.latest_inflation_cpi,
            "five_year_std_dev_inflation_cpi": self.stdev5_country_inflation_cpi,
            "real_interest_rate": self.country_real_interests,

            # FX
            "fx_cagr_percent_per_year": self.yearly_country_fx_cagr,
            "fx_ratio_series": series_to_year_mapping(fx_ratio_series),

            # External balance, fiscal, debt
            "latest_country_current_account": self.latest_country_current_account,
            "average_five_year_country_current_account": self.ave5_country_current_account,
            "latest_country_debt_gdp": self.latest_country_debt,
            "latest_country_fiscal_balance_gdp": self.latest_country_fiscal_balance,
            "debt_downtrend_flag": self.count_debt_downtrend_flag,
        }

        # --- assemble ---
        payload: Dict[str, Any] = {
            "meta": payload_meta,
            "series": {
                "country": series_country,
                "world": series_world,
            },
            "derived_metrics": derived_metrics,
        }
        return payload
