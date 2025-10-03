#valuation.py
# core/valuation.py
# (Series-first version; VALUATION-integrated outputs)
from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

from core.constants import DEFAULT_PARAM_DICT, VALUATION
from core.stock import Stock
from utils.stock import (
    _safe_mean,
    _safe_median,
    _safe_div,
    _safe_add,
)

class Valuation:
    def __init__(self, stock: Stock):
        self.stock = stock
        try:
            if isinstance(stock.prices, pd.DataFrame) and "Close" in stock.prices.columns and len(stock.prices) > 0:
                self.price_now = float(pd.to_numeric(stock.prices["Close"].iloc[-1], errors="coerce"))
            elif isinstance(stock.prices, pd.DataFrame) and stock.prices.shape[1] > 0 and len(stock.prices) > 0:
                self.price_now = float(pd.to_numeric(stock.prices.iloc[-1, 0], errors="coerce"))
            else:
                self.price_now = float("nan")
        except Exception:
            self.price_now = float("nan")

    def price_earning_multiples(self, conservative_growth_rate, discount_rate, n_years):
        earning_per_share = _safe_mean(self.stock.earning_per_share, n=1)
        price_earning_median = _safe_median(self.stock.price_to_earning, n=3)
        target_value = earning_per_share * price_earning_median * (1.0 + conservative_growth_rate) ** max(1, n_years)
        fair_price = target_value / ((1.0 + discount_rate) ** max(1, n_years))
        return fair_price

    def discounted_cash_flow_one_stage(self, conservative_growth_rate, discount_rate, decline_rate, n_years):
        free_cash_flow_median = _safe_median(self.stock.free_cashflow, n=3)
        shares_outstanding = _safe_median(self.stock.shares_outstanding, n=3)
        cash_and_cash_equivalent = _safe_median(self.stock.cash_and_equivalents, n=3)
        total_liabilities = _safe_median(self.stock.total_liabilities, n=3)

        total_discounted_free_cash_flow = 0.0
        last_discounted_free_cash_flow = 0.0
        free_cash_flow_last = free_cash_flow_median

        for i in range(n_years):
            free_cash_flow_input = free_cash_flow_last
            growth_this_year = conservative_growth_rate * (1.0 - decline_rate) ** i
            free_cash_flow_last = free_cash_flow_input * (1.0 + growth_this_year)

            present_value_free_cash_flow = free_cash_flow_last / (1.0 + discount_rate) ** (i + 1)
            total_discounted_free_cash_flow += present_value_free_cash_flow
            last_discounted_free_cash_flow = present_value_free_cash_flow

        terminal_value = last_discounted_free_cash_flow * 12
        equity_value = total_discounted_free_cash_flow + terminal_value
        if shares_outstanding is None or not np.isfinite(shares_outstanding) or shares_outstanding <= 0:
            return float("nan")
        fair_price = equity_value / shares_outstanding
        return fair_price

    def discounted_cash_flow_two_stage(
        self,
        conservative_growth_rate,
        discount_rate,
        decline_rate,
        n_years1,
        n_years2,
        terminal_growth
    ):
        free_cash_flow_median = _safe_median(self.stock.free_cashflow, n=3)
        shares_outstanding = _safe_median(self.stock.shares_outstanding, n=3)
        cash_and_cash_equivalent = _safe_median(self.stock.cash_and_equivalents, n=3)
        total_liabilities = _safe_median(self.stock.total_liabilities, n=3)

        present_value_stage1 = 0.0
        present_value_stage2 = 0.0
        free_cash_flow_last = free_cash_flow_median

        for i in range(n_years1):
            growth_this_year = conservative_growth_rate * (1.0 - decline_rate) ** i
            free_cash_flow_last = free_cash_flow_last * (1.0 + growth_this_year)
            discounted_cash_flow = free_cash_flow_last / (1.0 + discount_rate) ** (i + 1)
            present_value_stage1 += discounted_cash_flow

        for k in range(n_years2):
            free_cash_flow_last = free_cash_flow_last * (1.0 + terminal_growth)
            discounted_cash_flow = free_cash_flow_last / (1.0 + discount_rate) ** (n_years1 + k + 1)
            present_value_stage2 += discounted_cash_flow

        free_cash_flow_next = free_cash_flow_last * (1.0 + terminal_growth)
        denom = (discount_rate - terminal_growth)
        if denom is None or not np.isfinite(denom) or denom <= 0:
            terminal_value = float("nan")
        else:
            terminal_value = free_cash_flow_next / denom
        present_terminal_value = terminal_value / (1.0 + discount_rate) ** (n_years1 + n_years2)

        equity_value = present_value_stage1 + present_value_stage2 + present_terminal_value
        if shares_outstanding is None or not np.isfinite(shares_outstanding) or shares_outstanding <= 0:
            return float("nan")
        fair_price = equity_value / shares_outstanding
        return fair_price

    def discounted_dividend_two_stage(self, conservative_growth_rate, cost_of_equity, n_years1, n_years2, terminal_growth):
        dividend_median = _safe_median(self.stock.dividend_per_share_history, n=3)

        present_value_stage1 = 0.0
        present_value_stage2 = 0.0
        dividend_last = dividend_median

        for i in range(n_years1):
            growth_this_year = conservative_growth_rate
            dividend_last = dividend_last * (1.0 + growth_this_year)
            discounted_dividend = dividend_last / (1.0 + cost_of_equity) ** (i + 1)
            present_value_stage1 += discounted_dividend

        for k in range(n_years2):
            dividend_last = dividend_last * (1.0 + terminal_growth)
            discounted_dividend = dividend_last / (1.0 + cost_of_equity) ** (n_years1 + k + 1)
            present_value_stage2 += discounted_dividend

        dividend_next = dividend_last * (1.0 + terminal_growth)
        denom = (cost_of_equity - terminal_growth)
        if denom is None or not np.isfinite(denom) or denom <= 0:
            terminal_value = float("nan")
        else:
            terminal_value = dividend_next / denom
        present_terminal_value = terminal_value / (1.0 + cost_of_equity) ** (n_years1 + n_years2)

        fair_price = present_value_stage1 + present_value_stage2 + present_terminal_value
        return fair_price

    def return_on_equity(self, conservative_growth_rate, discount_rate, average_market_return, n_years):
        return_on_equity = _safe_median(self.stock.return_on_equity, n=3)
        dividend_per_share = _safe_mean(self.stock.dividend_per_share_history, n=3)

        bvps_series = _safe_div(self.stock.total_equity, self.stock.shares_outstanding)
        book_value_per_share = _safe_mean(bvps_series, n=3)

        present_value_of_dividends = 0.0
        last_book_value_per_share = book_value_per_share
        last_dividend_per_share = dividend_per_share

        for i in range(n_years):
            last_book_value_per_share = last_book_value_per_share * (1.0 + conservative_growth_rate)
            last_dividend_per_share = last_dividend_per_share * (1.0 + conservative_growth_rate)

            discounted_dividend = last_dividend_per_share / (1.0 + discount_rate) ** (i + 1)
            present_value_of_dividends += discounted_dividend

        final_net_income_per_share = last_book_value_per_share * return_on_equity
        if average_market_return is None or not np.isfinite(average_market_return) or average_market_return <= 0:
            terminal_value_at_horizon = float("nan")
        else:
            terminal_value_at_horizon = final_net_income_per_share / average_market_return
        present_value_of_terminal = terminal_value_at_horizon / (1.0 + discount_rate) ** n_years

        fair_price = present_value_of_dividends + present_value_of_terminal
        return fair_price

    def excess_return(self, conservative_growth_rate, cost_of_equity):
        return_on_equity = _safe_median(self.stock.return_on_equity, n=3)
        total_equity = _safe_median(self.stock.total_equity, n=3)
        shares_outstanding = _safe_median(self.stock.shares_outstanding, n=3)
        excess_return = (return_on_equity - cost_of_equity) * total_equity

        denom = (cost_of_equity - conservative_growth_rate)
        if denom is None or not np.isfinite(denom) or denom <= 0:
            terminal_value = float("nan")
        else:
            terminal_value = excess_return / denom
        present_terminal_value = terminal_value + total_equity

        if shares_outstanding is None or not np.isfinite(shares_outstanding) or shares_outstanding <= 0:
            return float("nan")
        fair_price = present_terminal_value / shares_outstanding
        return fair_price

    def graham_number(self):
        earning_per_share = _safe_median(self.stock.earning_per_share, n=3)
        book_value_per_share = _safe_median(
            _safe_div(self.stock.total_equity, self.stock.shares_outstanding),
            n=3
        )
        product = 22.5 * earning_per_share * book_value_per_share
        fair_price = math.sqrt(max(float(product), 0.0)) if np.isfinite(product) else float("nan")
        return fair_price

    def get_valuation_params(
            self,
            *,
            margin_of_safety: Optional[float] = None,
            growth_rate: Optional[float] = None,
            risk_free_rate: Optional[float] = None,
            discount_rate: Optional[float] = None,
            decline_rate: Optional[float] = None,
            average_market_return: Optional[float] = None,
            n_years1: Optional[int] = None,
            n_years2: Optional[int] = None,
            terminal_growth_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        # Keep estimates None unless computed
        earning_growth_estimates = None
        conservative_growth_on_earning = None
        growth_estimates_from_dividend = None
        conservative_growth_on_dividend = None

        if margin_of_safety is None:
            margin_of_safety = DEFAULT_PARAM_DICT["margin_of_safety"]

        if growth_rate is None:
            earning_growth_estimates, conservative_growth_on_earning = self.estimate_earning_growth_rate(margin_of_safety)

        if risk_free_rate is None:
            risk_free_rate = getattr(self.stock, "risk_free_rate", None)
            if risk_free_rate is None:
                risk_free_rate = DEFAULT_PARAM_DICT["risk_free_rate"]

        if discount_rate is None:
            discount_rate = self.get_discount_rate(discount_rate, risk_free_rate, average_market_return)
            if discount_rate is None:
                discount_rate = DEFAULT_PARAM_DICT["discount_rate"]

        if decline_rate is None:
            decline_rate = DEFAULT_PARAM_DICT["decline_rate"]

        if average_market_return is None:
            average_market_return = DEFAULT_PARAM_DICT["average_market_return"]

        if n_years1 is None:
            n_years1 = DEFAULT_PARAM_DICT["n_years1"]

        if n_years2 is None:
            n_years2 = DEFAULT_PARAM_DICT["n_years2"]

        if terminal_growth_rate is None:
            terminal_growth_rate = getattr(self.stock, "risk_free_rate", None)
            if terminal_growth_rate is None:
                terminal_growth_rate = DEFAULT_PARAM_DICT["terminal_growth_rate"]

        return {
            "margin_of_safety": margin_of_safety,
            "growth_rate": earning_growth_estimates,
            "risk_free_rate": risk_free_rate,
            "discount_rate": discount_rate,
            "decline_rate": decline_rate,
            "average_market_return": average_market_return,
            "n_years1": n_years1,
            "n_years2": n_years2,
            "terminal_growth_rate": terminal_growth_rate,
        }

    def valuate(
        self,
        margin_of_safety=None,
        growth_rate=None,
        discount_rate=None,
        risk_free_rate=None,
        average_market_return=None,
        decline_rate=None,
        n_years1=None,
        n_years2=None,
        terminal_growth_rate=None,
    ) -> Dict[str, Dict[str, Any]]:
        if margin_of_safety is None:
            margin_of_safety = DEFAULT_PARAM_DICT["margin_of_safety"]

        if growth_rate is None:
            earning_growth_estimates, conservative_growth_on_earning = self.estimate_earning_growth_rate(margin_of_safety)
        else:
            earning_growth_estimates = growth_rate
            conservative_growth_on_earning = growth_rate * (1 - margin_of_safety)


        if risk_free_rate is None:
            risk_free_rate = self.stock.risk_free_rate
            if risk_free_rate is None:
                risk_free_rate = DEFAULT_PARAM_DICT["risk_free_rate"]

        if discount_rate is None:
            discount_rate = self.get_discount_rate(discount_rate, risk_free_rate, average_market_return)
            if discount_rate is None:
                discount_rate = DEFAULT_PARAM_DICT["discount_rate"]

        if decline_rate is None:
            decline_rate = DEFAULT_PARAM_DICT["decline_rate"]

        if average_market_return is None:
            average_market_return = DEFAULT_PARAM_DICT["average_market_return"]

        if n_years1 is None:
            n_years1 = DEFAULT_PARAM_DICT["n_years1"]

        if n_years2 is None:
            n_years2 = DEFAULT_PARAM_DICT["n_years2"]

        if terminal_growth_rate is None:
            terminal_growth_rate = self.stock.risk_free_rate
            if terminal_growth_rate is None:
                terminal_growth_rate = DEFAULT_PARAM_DICT["terminal_growth_rate"]

        growth_estimates_from_dividend, conservative_growth_on_dividend = self.estimate_dividend_growth_rate(margin_of_safety)

        # --- Compute each model’s fair value ---
        fair_price_PEM = self.price_earning_multiples(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            n_years=n_years1,
        )

        fair_price_DCF_1 = self.discounted_cash_flow_one_stage(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            decline_rate=decline_rate,
            n_years=n_years1,
        )

        fair_price_DCF_2 = self.discounted_cash_flow_two_stage(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            decline_rate=decline_rate,
            n_years1=n_years1,
            n_years2=n_years2,
            terminal_growth=terminal_growth_rate,
        )

        fair_price_ROE = self.return_on_equity(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            average_market_return=average_market_return,
            n_years=n_years1,
        )

        fair_price_DDM = self.discounted_dividend_two_stage(
            conservative_growth_rate=conservative_growth_on_dividend,
            cost_of_equity=self.stock.cost_of_equity,
            n_years1=n_years1,
            n_years2=n_years2,
            terminal_growth=terminal_growth_rate,
        )

        fair_price_ER = self.excess_return(
            conservative_growth_rate=conservative_growth_on_earning,
            cost_of_equity=self.stock.cost_of_equity,
        )

        fair_price_GRAHAM = self.graham_number()

        # --- Package results: follow your PEM example for all models with human-friendly outputs ---
        results: Dict[str, Dict[str, Any]] = {}

        r_pem = VALUATION["price_earning_multiples"].copy()
        r_pem["outputs"] = {"Fair Value": fair_price_PEM}
        results["price_earning_multiples"] = r_pem

        r_dcf1 = VALUATION["discounted_cash_flow_one_stage"].copy()
        r_dcf1["outputs"] = {"Fair Value": fair_price_DCF_1}
        results["discounted_cash_flow_one_stage"] = r_dcf1

        r_dcf2 = VALUATION["discounted_cash_flow_two_stage"].copy()
        r_dcf2["outputs"] = {"Fair Value": fair_price_DCF_2}
        results["discounted_cash_flow_two_stage"] = r_dcf2

        r_roe = VALUATION["return_on_equity"].copy()
        r_roe["outputs"] = {"Fair Value": fair_price_ROE}
        results["return_on_equity"] = r_roe

        r_ddm = VALUATION["discounted_dividend_two_stage"].copy()
        r_ddm["outputs"] = {"Fair Value": fair_price_DDM}
        results["discounted_dividend_two_stage"] = r_ddm

        r_er = VALUATION["excess_return"].copy()
        r_er["outputs"] = {"Fair Value": fair_price_ER}
        results["excess_return"] = r_er

        r_gn = VALUATION["graham_number"].copy()
        r_gn["outputs"] = {"Fair Value": fair_price_GRAHAM}
        results["graham_number"] = r_gn

        results['params'] = {
            "margin_of_safety": margin_of_safety,
            "growth_rate": growth_rate,
            "risk_free_rate": risk_free_rate,
            "discount_rate": discount_rate,
            "decline_rate": decline_rate,
            "average_market_return": average_market_return,
            "n_years1": n_years1,
            "n_years2": n_years2,
            "terminal_growth_rate": terminal_growth_rate,
            "earning_growth_estimates": earning_growth_estimates,
            "conservative_growth_on_earning": conservative_growth_on_earning,
            "growth_estimates_from_dividend": growth_estimates_from_dividend,
            "conservative_growth_on_dividend": conservative_growth_on_dividend,
        }
        return results

    def estimate_earning_growth_rate(self, margin_of_safety):
        growth_estimates_from_analyst = self.stock.next_year_growth_estimates
        growth_estimates_from_yoy_earning_median = _safe_median(self.stock.earning_yoy_growth, n=3)

        if not np.isnan(growth_estimates_from_analyst) and not np.isnan(growth_estimates_from_yoy_earning_median):
            earning_growth_estimates = min(growth_estimates_from_analyst, growth_estimates_from_yoy_earning_median)
        else:
            if np.isnan(growth_estimates_from_analyst) and not np.isnan(growth_estimates_from_yoy_earning_median):
                earning_growth_estimates = growth_estimates_from_yoy_earning_median
            elif not np.isnan(growth_estimates_from_analyst) and np.isnan(growth_estimates_from_yoy_earning_median):
                earning_growth_estimates = growth_estimates_from_analyst
            else:
                earning_growth_estimates = float("nan")

        if np.isnan(earning_growth_estimates):
            earning_growth_estimates = DEFAULT_PARAM_DICT["growth_estimates"]

        conservative_growth_on_earning = earning_growth_estimates * (1.0 - margin_of_safety)

        return earning_growth_estimates, conservative_growth_on_earning

    def estimate_dividend_growth_rate(self, margin_of_safety):

        growth_estimates_from_dividend = _safe_median(self.stock.dividend_per_share_yoy_growth, n=5)
        if np.isnan(growth_estimates_from_dividend):
            return np.nan, np.nan

        conservative_growth_on_dividend = growth_estimates_from_dividend * (1.0 - margin_of_safety)

        return growth_estimates_from_dividend, conservative_growth_on_dividend

    def get_discount_rate(self, discount_rate: float | None, risk_free_rate=None, average_market_return=None) -> float | None:
        if discount_rate is not None:
            return discount_rate

        if risk_free_rate is None:
            risk_free_rate = self.stock.risk_free_rate
            if risk_free_rate is None:
                risk_free_rate = DEFAULT_PARAM_DICT["risk_free_rate"]

        if average_market_return is None:
            average_market_return = DEFAULT_PARAM_DICT["average_market_return"]

        self.stock.cost_of_equity = (
            risk_free_rate + self.stock.beta * (average_market_return - risk_free_rate)
            if self.stock.beta is not None
            else np.nan
        )

        self.stock.book_value_of_debt = _safe_add(
            self.stock.short_term_debt_and_capital_obligation,
            self.stock.long_term_debt_and_capital_obligation,
        )
        self.stock.cost_of_debt = _safe_mean(
            _safe_div(self.stock.interest_expense, self.stock.book_value_of_debt),
            n=1,
        )

        self.stock.weight_of_equity = _safe_mean(
            _safe_div(self.stock.market_cap, _safe_add(self.stock.market_cap, self.stock.book_value_of_debt)),
            n=1,
        )
        self.stock.weight_of_debt = _safe_mean(
            _safe_div(self.stock.book_value_of_debt, _safe_add(self.stock.market_cap, self.stock.book_value_of_debt)),
            n=1,
        )

        tax_rate_scalar = _safe_mean(self.stock.tax_rate, n=1)

        discount_rate = (
            self.stock.weight_of_equity * self.stock.cost_of_equity
            + self.stock.weight_of_debt * self.stock.cost_of_debt * (1 - tax_rate_scalar)
        )

        if discount_rate is None or np.isnan(discount_rate):
            return DEFAULT_PARAM_DICT["discount_rate"]

        return discount_rate