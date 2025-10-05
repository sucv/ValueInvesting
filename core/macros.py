from __future__ import annotations

from core.constants import try_iso3, WORLD_BANK_INDEX
from typing import Dict, Optional
import pandas as pd

from utils.stock import _safe_div, _convert_year_value_list_to_series
from utils.world_bank import wb_client


class MacroEconomic:
    """
    Series-native macro fetcher.

    Contract:
      - All macro series are stored as pd.Series:
          name   = indicator_key (e.g., 'real_gdp_growth')
          index  = years as ints, ordered latest → older
          values = floats (NaN allowed)
      - No aggregation methods - just raw series storage
    """

    def __init__(
            self,
            base_currency_country: str,
            country: str,
            macro_years: int = 10,
    ) -> None:
        self.base_currency_country = (base_currency_country or "").upper()
        self.country = country
        self.macro_years = max(10, int(macro_years))

        # Fetch and store raw series
        self._fetch_country_macro()
        self._fetch_world_macro()
        self._compute_fx_ratio()

    # ---------------------------
    # ISO3 helper
    # ---------------------------
    def get_country_iso3(self) -> Optional[str]:
        if self.country is None:
            return None
        iso3_code = try_iso3(self.country)
        if iso3_code is None:
            return None
        return iso3_code.upper()

    # ---------------------------
    # Fetch country macros
    # ---------------------------
    def _fetch_country_macro(self) -> None:
        country_iso3_code = self.get_country_iso3()
        if not country_iso3_code:
            # Initialize empty series
            self.country_real_gdp_growth = pd.Series(dtype=float, name="country_real_gdp_growth")
            self.country_inflation_cpi = pd.Series(dtype=float, name="country_inflation_cpi")
            self.country_lending_rate = pd.Series(dtype=float, name="country_lending_rate")
            self.country_fx_lcu_per_usd = pd.Series(dtype=float, name="country_fx_lcu_per_usd")
            self.country_current_account_gdp = pd.Series(dtype=float, name="country_current_account_gdp")
            self.country_gov_debt_gdp = pd.Series(dtype=float, name="country_gov_debt_gdp")
            self.country_fiscal_balance_gdp = pd.Series(dtype=float, name="country_fiscal_balance_gdp")
            return

        indicator_keys_to_request = [
            WORLD_BANK_INDEX["real_gdp_growth"],
            WORLD_BANK_INDEX["inflation_cpi"],
            WORLD_BANK_INDEX["lending_rate"],
            WORLD_BANK_INDEX["fx_lcu_per_usd"],
            WORLD_BANK_INDEX["current_account_gdp"],
            WORLD_BANK_INDEX["gov_debt_gdp"],
            WORLD_BANK_INDEX["fiscal_balance_gdp"],
        ]

        raw_country_macros = wb_client(
            country_iso3_code,
            indicator_keys_to_request,
            mrv=self.macro_years
        )

        # Convert to series and store as attributes
        self.country_real_gdp_growth = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["real_gdp_growth"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["real_gdp_growth"], []),
            maximum_points=self.macro_years,
        )
        self.country_real_gdp_growth.name = "country_real_gdp_growth"

        self.country_inflation_cpi = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["inflation_cpi"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["inflation_cpi"], []),
            maximum_points=self.macro_years,
        )
        self.country_inflation_cpi.name = "country_inflation_cpi"

        self.country_lending_rate = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["lending_rate"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["lending_rate"], []),
            maximum_points=self.macro_years,
        )
        self.country_lending_rate.name = "country_lending_rate"

        self.country_fx_lcu_per_usd = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["fx_lcu_per_usd"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["fx_lcu_per_usd"], []),
            maximum_points=self.macro_years,
        )
        self.country_fx_lcu_per_usd.name = "country_fx_lcu_per_usd"

        self.country_current_account_gdp = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["current_account_gdp"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["current_account_gdp"], []),
            maximum_points=self.macro_years,
        )
        self.country_current_account_gdp.name = "country_current_account_gdp"

        self.country_gov_debt_gdp = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["gov_debt_gdp"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["gov_debt_gdp"], []),
            maximum_points=self.macro_years,
        )
        self.country_gov_debt_gdp.name = "country_gov_debt_gdp"

        self.country_fiscal_balance_gdp = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["fiscal_balance_gdp"],
            year_value_list=raw_country_macros.get(WORLD_BANK_INDEX["fiscal_balance_gdp"], []),
            maximum_points=self.macro_years,
        )
        self.country_fiscal_balance_gdp.name = "country_fiscal_balance_gdp"

    # ---------------------------
    # Fetch world macros
    # ---------------------------
    def _fetch_world_macro(self) -> None:
        indicator_keys_to_request = [WORLD_BANK_INDEX["real_gdp_growth"]]
        raw_world_macros = wb_client("WLD", indicator_keys_to_request, mrv=self.macro_years)

        self.world_real_gdp_growth = _convert_year_value_list_to_series(
            indicator_key=WORLD_BANK_INDEX["real_gdp_growth"],
            year_value_list=raw_world_macros.get(WORLD_BANK_INDEX["real_gdp_growth"], []),
            maximum_points=self.macro_years,
        )
        self.world_real_gdp_growth.name = "world_real_gdp_growth"

    # ---------------------------
    # Compute FX ratio
    # ---------------------------
    def _compute_fx_ratio(self) -> None:
        """
        Compute FX ratio adjusted for base currency:
        - If base is USA, use country FX as-is
        - Otherwise, divide country FX by base country FX
        """
        if self.base_currency_country == "USA":
            self.country_fx_ratio = self.country_fx_lcu_per_usd.copy()
            self.country_fx_ratio.name = "country_fx_ratio"
            return

        # Fetch base country FX
        indicator_key = WORLD_BANK_INDEX["fx_lcu_per_usd"]
        raw_base_macros = wb_client(
            self.base_currency_country,
            [indicator_key],
            mrv=self.macro_years
        )

        base_fx_series = _convert_year_value_list_to_series(
            indicator_key=indicator_key,
            year_value_list=raw_base_macros.get(indicator_key, []),
            maximum_points=self.macro_years,
        )

        if base_fx_series.empty:
            self.country_fx_ratio = self.country_fx_lcu_per_usd.copy()
            self.country_fx_ratio.name = "country_fx_ratio"
            return

        # Compute ratio
        self.country_fx_ratio = _safe_div(self.country_fx_lcu_per_usd, base_fx_series)
        self.country_fx_ratio.name = "country_fx_ratio"

    # ---------------------------
    # Computed series: real interest rate
    # ---------------------------
    @property
    def country_real_interest_rate(self) -> pd.Series:
        """
        Real interest rate = lending rate - inflation CPI
        Computed on-the-fly from stored series
        """
        from utils.stock import _safe_minus
        real_rate = _safe_minus(self.country_lending_rate, self.country_inflation_cpi)
        real_rate.name = "country_real_interest_rate"
        return real_rate