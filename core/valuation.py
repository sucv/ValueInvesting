from __future__ import annotations
from typing import Dict, Any, Optional, List
import math
import numpy as np
import pandas as pd

from core.constants import DEFAULT_PARAM_DICT, VALUATION
from core.stock import Stock
from utils.stock import _safe_mean, _safe_median, _safe_div, _safe_cagr


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

    def _format_value(self, val: Any) -> str:
        """Format value for display in calculation logs."""
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "NaN"
        if isinstance(val, (int, float)):
            if np.isinf(val):
                return "Infinity" if val > 0 else "-Infinity"
            return f"{val:,.4f}"
        return str(val)

    def price_earning_multiples(self, conservative_growth_rate, discount_rate, n_years) -> tuple[
        float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Step 1: Get inputs
        earnings_per_share_median = _safe_mean(self.stock.earning_per_share, n=1)
        price_to_earnings_ratio_median = _safe_median(self.stock.price_to_earning, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather the fundamental inputs for the calculation",
            "input_table": {
                "EPS (3-year median)": self._format_value(earnings_per_share_median),
                "P/E Multiple (3-year median)": self._format_value(price_to_earnings_ratio_median),
                "Growth Rate (g)": self._format_value(conservative_growth_rate),
                "Discount Rate (r)": self._format_value(discount_rate),
                "Projection Years (N)": str(n_years)
            }
        })

        # Step 2: Project target value
        growth_factor_over_projection_period = (1.0 + conservative_growth_rate) ** max(1, n_years)
        target_value_at_end_of_projection = earnings_per_share_median * price_to_earnings_ratio_median * growth_factor_over_projection_period

        # Format values for explanation
        eps_formatted = self._format_value(earnings_per_share_median)
        pe_formatted = self._format_value(price_to_earnings_ratio_median)
        growth_factor_formatted = self._format_value(growth_factor_over_projection_period)
        target_value_formatted = self._format_value(target_value_at_end_of_projection)

        calculation_steps_list.append({
            "step": "Target Value Projection",
            "description": f"Project EPS forward {n_years} years using growth rate",
            "latex": rf"Target = EPS \times PE \times (1+g)^N = {target_value_formatted}",
            "explanation": f"where EPS = {eps_formatted}, PE = {pe_formatted}, (1+g)^N = {growth_factor_formatted}",
        })

        # Step 3: Discount to present
        discount_factor_over_projection_period = (1.0 + discount_rate) ** max(1, n_years)
        fair_price_per_share = target_value_at_end_of_projection / discount_factor_over_projection_period

        discount_factor_formatted = self._format_value(discount_factor_over_projection_period)
        fair_price_formatted = self._format_value(fair_price_per_share)

        calculation_steps_list.append({
            "step": "Present Value Calculation",
            "description": "Discount the target value back to present",
            "latex": rf"P_0 = \dfrac{{Target}}{{(1+r)^N}} = {fair_price_formatted}",
            "explanation": f"where Target = {target_value_formatted}, (1+r)^N = {discount_factor_formatted}",
        })

        return fair_price_per_share, calculation_steps_list

    def discounted_cash_flow_one_stage(
            self, conservative_growth_rate, discount_rate, decline_rate, n_years
    ) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        free_cash_flow_median = _safe_median(self.stock.free_cashflow, n=3)
        shares_outstanding_median = _safe_median(self.stock.shares_outstanding, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather fundamental inputs",
            "input_table": {
                "Free Cash Flow (3-year median)": self._format_value(free_cash_flow_median),
                "Shares Outstanding (3-year median)": self._format_value(shares_outstanding_median),
                "Initial Growth Rate (g)": self._format_value(conservative_growth_rate),
                "Annual Decline Rate (d)": self._format_value(decline_rate),
                "Discount Rate (r)": self._format_value(discount_rate),
                "Projection Years (N)": str(n_years)
            }
        })

        # Project cash flows with declining growth
        total_present_value_of_cash_flows = 0.0
        last_year_discounted_cash_flow = 0.0
        free_cash_flow_current_year = free_cash_flow_median

        yearly_projection_breakdown_data = []
        for year_index in range(n_years):
            growth_rate_this_year = conservative_growth_rate * (1.0 - decline_rate) ** year_index
            free_cash_flow_current_year = free_cash_flow_current_year * (1.0 + growth_rate_this_year)
            present_value_of_cash_flow_this_year = free_cash_flow_current_year / (1.0 + discount_rate) ** (
                        year_index + 1)
            total_present_value_of_cash_flows += present_value_of_cash_flow_this_year
            last_year_discounted_cash_flow = present_value_of_cash_flow_this_year

            yearly_projection_breakdown_data.append({
                "Year": f"Year {year_index + 1}",
                "Growth Rate": self._format_value(growth_rate_this_year),
                "FCF": self._format_value(free_cash_flow_current_year),
                "PV of FCF": self._format_value(present_value_of_cash_flow_this_year)
            })

        # Create DataFrame and add sum row
        yearly_projection_breakdown_df = pd.DataFrame(yearly_projection_breakdown_data).set_index("Year")
        sum_row_data = {
            "Growth Rate": "—",
            "FCF": "—",
            "PV of FCF": self._format_value(total_present_value_of_cash_flows)
        }
        yearly_projection_breakdown_df.loc["Sum"] = sum_row_data

        growth_rate_formatted = self._format_value(conservative_growth_rate)
        decline_rate_formatted = self._format_value(decline_rate)
        total_pv_formatted = self._format_value(total_present_value_of_cash_flows)

        calculation_steps_list.append({
            "step": "Cash Flow Projection (Declining Growth)",
            "description": "Project FCF with growth declining each year",
            "latex": r"g_t = g \times (1 - d)^{t-1}, \quad FCF_t = FCF_{t-1} \times (1 + g_t)",
            "explanation": f"where g = {growth_rate_formatted}, d = {decline_rate_formatted}",
            "details": {"yearly_table": yearly_projection_breakdown_df}
        })

        calculation_steps_list.append({
            "step": "Present Value Summation",
            "description": "Sum all discounted cash flows",
            "latex": rf"PV = \sum_{{t=1}}^{{N}} \dfrac{{FCF_t}}{{(1 + r)^t}} = {total_pv_formatted}",
            "explanation": f"Total PV of {n_years} years of cash flows = {total_pv_formatted}",
        })

        # Terminal value
        terminal_value_multiple = 12
        terminal_value_estimate = last_year_discounted_cash_flow * terminal_value_multiple

        last_pv_formatted = self._format_value(last_year_discounted_cash_flow)
        terminal_value_formatted = self._format_value(terminal_value_estimate)

        calculation_steps_list.append({
            "step": "Terminal Value",
            "description": "Apply terminal multiple to final discounted FCF",
            "latex": rf"TV = FCF_{{N,PV}} \times k = {terminal_value_formatted}",
            "explanation": f"where FCF_N,PV = {last_pv_formatted}, k = {terminal_value_multiple}",
        })

        # Equity value and fair price
        total_equity_value = total_present_value_of_cash_flows + terminal_value_estimate

        if shares_outstanding_median is None or not np.isfinite(
                shares_outstanding_median) or shares_outstanding_median <= 0:
            fair_price_per_share = float("nan")
            calculation_steps_list.append({
                "step": "ERROR",
                "description": "Cannot calculate fair price per share",
                "details": {"Issue": "Invalid shares outstanding"}
            })
        else:
            fair_price_per_share = total_equity_value / shares_outstanding_median

            equity_value_formatted = self._format_value(total_equity_value)
            shares_formatted = self._format_value(shares_outstanding_median)
            fair_price_formatted = self._format_value(fair_price_per_share)

            calculation_steps_list.append({
                "step": "Fair Price Per Share",
                "description": "Divide total equity value by shares outstanding",
                "latex": rf"P_0 = \dfrac{{PV + TV}}{{Shares}} = {fair_price_formatted}",
                "explanation": f"where PV + TV = {equity_value_formatted}, Shares = {shares_formatted}",
            })

        return fair_price_per_share, calculation_steps_list

    def discounted_cash_flow_two_stage(
            self, conservative_growth_rate, discount_rate, decline_rate, n_years1, n_years2, terminal_growth
    ) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        free_cash_flow_median = _safe_median(self.stock.free_cashflow, n=3)
        shares_outstanding_median = _safe_median(self.stock.shares_outstanding, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather fundamental inputs for two-stage model",
            "input_table": {
                "Free Cash Flow (3-year median)": self._format_value(free_cash_flow_median),
                "Shares Outstanding (3-year median)": self._format_value(shares_outstanding_median),
                "Stage 1 Growth Rate (g)": self._format_value(conservative_growth_rate),
                "Decline Rate (d)": self._format_value(decline_rate),
                "Terminal Growth Rate (g_term)": self._format_value(terminal_growth),
                "Discount Rate (r)": self._format_value(discount_rate),
                "Stage 1 Years (N1)": str(n_years1),
                "Stage 2 Years (N2)": str(n_years2)
            }
        })

        # Stage 1: Declining growth
        present_value_stage_one = 0.0
        free_cash_flow_current_year = free_cash_flow_median
        stage_one_yearly_breakdown_data = []

        for year_index in range(n_years1):
            growth_rate_this_year = conservative_growth_rate * (1.0 - decline_rate) ** year_index
            free_cash_flow_current_year = free_cash_flow_current_year * (1.0 + growth_rate_this_year)
            present_value_this_year = free_cash_flow_current_year / (1.0 + discount_rate) ** (year_index + 1)
            present_value_stage_one += present_value_this_year

            stage_one_yearly_breakdown_data.append({
                "Year": f"Year {year_index + 1}",
                "Growth Rate": self._format_value(growth_rate_this_year),
                "FCF": self._format_value(free_cash_flow_current_year),
                "PV": self._format_value(present_value_this_year)
            })

        # Add sum row for Stage 1
        stage_one_df = pd.DataFrame(stage_one_yearly_breakdown_data).set_index("Year")
        stage_one_df.loc["Sum"] = {
            "Growth Rate": "—",
            "FCF": "—",
            "PV": self._format_value(present_value_stage_one)
        }

        stage_one_pv_formatted = self._format_value(present_value_stage_one)

        calculation_steps_list.append({
            "step": "Stage 1 Projection (High Growth with Decline)",
            "description": f"High growth phase ({n_years1} years) with declining growth",
            "latex": rf"PV_1 = \sum_{{t=1}}^{{N_1}} \dfrac{{FCF_t}}{{(1 + r)^t}} = {stage_one_pv_formatted}",
            "explanation": f"Present value of Stage 1 cash flows = {stage_one_pv_formatted}",
            "details": {"yearly_table": stage_one_df}
        })

        # Stage 2: Stable growth
        present_value_stage_two = 0.0
        stage_two_yearly_breakdown_data = []

        for year_offset in range(n_years2):
            free_cash_flow_current_year = free_cash_flow_current_year * (1.0 + terminal_growth)
            present_value_this_year = free_cash_flow_current_year / (1.0 + discount_rate) ** (
                        n_years1 + year_offset + 1)
            present_value_stage_two += present_value_this_year

            stage_two_yearly_breakdown_data.append({
                "Year": f"Year {n_years1 + year_offset + 1}",
                "FCF": self._format_value(free_cash_flow_current_year),
                "PV": self._format_value(present_value_this_year)
            })

        # Add sum row for Stage 2
        stage_two_df = pd.DataFrame(stage_two_yearly_breakdown_data).set_index("Year")
        stage_two_df.loc["Sum"] = {
            "FCF": "—",
            "PV": self._format_value(present_value_stage_two)
        }

        stage_two_pv_formatted = self._format_value(present_value_stage_two)
        terminal_growth_formatted = self._format_value(terminal_growth)

        calculation_steps_list.append({
            "step": "Stage 2 Projection (Stable Growth)",
            "description": f"Stable growth phase ({n_years2} years) at terminal rate",
            "latex": rf"PV_2 = \sum_{{k=1}}^{{N_2}} \dfrac{{FCF_{{N_1+k}}}}{{(1 + r)^{{N_1+k}}}} = {stage_two_pv_formatted}",
            "explanation": f"where g_term = {terminal_growth_formatted}, PV of Stage 2 = {stage_two_pv_formatted}",
            "details": {"yearly_table": stage_two_df}
        })

        # Terminal value
        free_cash_flow_next_year = free_cash_flow_current_year * (1.0 + terminal_growth)
        discount_minus_growth_denominator = (discount_rate - terminal_growth)

        if discount_minus_growth_denominator is None or not np.isfinite(
                discount_minus_growth_denominator) or discount_minus_growth_denominator <= 0:
            terminal_value_perpetuity = float("nan")
            calculation_steps_list.append({
                "step": "Terminal Value Calculation",
                "description": "ERROR: Invalid denominator for Gordon Growth",
                "details": {
                    "Discount Rate - Terminal Growth": self._format_value(discount_minus_growth_denominator),
                    "Issue": "Denominator must be positive (r > g_term)"
                }
            })
        else:
            terminal_value_perpetuity = free_cash_flow_next_year / discount_minus_growth_denominator

            fcf_next_formatted = self._format_value(free_cash_flow_next_year)
            denominator_formatted = self._format_value(discount_minus_growth_denominator)
            terminal_value_formatted = self._format_value(terminal_value_perpetuity)

            calculation_steps_list.append({
                "step": "Terminal Value (Gordon Growth Model)",
                "description": "Perpetuity value beyond projection period",
                "latex": rf"TV = \dfrac{{FCF_{{final}} \times (1 + g_{{term}})}}{{r - g_{{term}}}} = {terminal_value_formatted}",
                "explanation": f"where FCF_final × (1+g_term) = {fcf_next_formatted}, (r - g_term) = {denominator_formatted}",
            })

        total_years_projection = n_years1 + n_years2
        present_value_of_terminal = terminal_value_perpetuity / (1.0 + discount_rate) ** total_years_projection

        pv_terminal_formatted = self._format_value(present_value_of_terminal)

        calculation_steps_list.append({
            "step": "Discount Terminal Value to Present",
            "description": "Bring terminal value to present",
            "latex": rf"PV_{{TV}} = \dfrac{{TV}}{{(1 + r)^{{N_1+N_2}}}} = {pv_terminal_formatted}",
            "explanation": f"where TV = {self._format_value(terminal_value_perpetuity)}, N1+N2 = {total_years_projection}",
        })

        # Fair price
        total_equity_value = present_value_stage_one + present_value_stage_two + present_value_of_terminal

        if shares_outstanding_median is None or not np.isfinite(
                shares_outstanding_median) or shares_outstanding_median <= 0:
            fair_price_per_share = float("nan")
            calculation_steps_list.append({
                "step": "ERROR",
                "description": "Cannot calculate fair price per share",
                "details": {"Issue": "Invalid shares outstanding"}
            })
        else:
            fair_price_per_share = total_equity_value / shares_outstanding_median

            equity_value_formatted = self._format_value(total_equity_value)
            shares_formatted = self._format_value(shares_outstanding_median)
            fair_price_formatted = self._format_value(fair_price_per_share)

            calculation_steps_list.append({
                "step": "Fair Price Per Share",
                "description": "Sum all PVs and divide by shares",
                "latex": rf"P_0 = \dfrac{{PV_1 + PV_2 + PV_{{TV}}}}{{Shares}} = {fair_price_formatted}",
                "explanation": f"where PV1 + PV2 + PV_TV = {equity_value_formatted}, Shares = {shares_formatted}",
            })

        return fair_price_per_share, calculation_steps_list

    def discounted_dividend_two_stage(
            self, conservative_growth_rate, cost_of_equity, n_years1, n_years2, terminal_growth
    ) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        dividend_per_share_median = _safe_median(self.stock.dividend_per_share_history, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather dividend and discount rate inputs",
            "input_table": {
                "Dividend Per Share (3-year median)": self._format_value(dividend_per_share_median),
                "Stage 1 Growth Rate (g)": self._format_value(conservative_growth_rate),
                "Terminal Growth Rate (g_term)": self._format_value(terminal_growth),
                "Cost of Equity (k_e)": self._format_value(cost_of_equity),
                "Stage 1 Years (N1)": str(n_years1),
                "Stage 2 Years (N2)": str(n_years2)
            }
        })

        # Stage 1
        present_value_stage_one_dividends = 0.0
        dividend_per_share_current_year = dividend_per_share_median
        stage_one_yearly_breakdown_data = []

        for year_index in range(n_years1):
            dividend_per_share_current_year = dividend_per_share_current_year * (1.0 + conservative_growth_rate)
            present_value_dividend_this_year = dividend_per_share_current_year / (1.0 + cost_of_equity) ** (
                        year_index + 1)
            present_value_stage_one_dividends += present_value_dividend_this_year

            stage_one_yearly_breakdown_data.append({
                "Year": f"Year {year_index + 1}",
                "Dividend": self._format_value(dividend_per_share_current_year),
                "PV": self._format_value(present_value_dividend_this_year)
            })

        # Add sum row for Stage 1
        stage_one_df = pd.DataFrame(stage_one_yearly_breakdown_data).set_index("Year")
        stage_one_df.loc["Sum"] = {
            "Dividend": "—",
            "PV": self._format_value(present_value_stage_one_dividends)
        }

        stage_one_pv_formatted = self._format_value(present_value_stage_one_dividends)

        calculation_steps_list.append({
            "step": "Stage 1 Dividends (High Growth)",
            "description": f"High growth dividend phase ({n_years1} years)",
            "latex": rf"PV_1 = \sum_{{t=1}}^{{N_1}} \dfrac{{DPS_t}}{{(1 + k_e)^t}} = {stage_one_pv_formatted}",
            "explanation": f"Present value of Stage 1 dividends = {stage_one_pv_formatted}",
            "details": {"yearly_table": stage_one_df}
        })

        # Stage 2
        present_value_stage_two_dividends = 0.0
        stage_two_yearly_breakdown_data = []

        for year_offset in range(n_years2):
            dividend_per_share_current_year = dividend_per_share_current_year * (1.0 + terminal_growth)
            present_value_dividend_this_year = dividend_per_share_current_year / (1.0 + cost_of_equity) ** (
                        n_years1 + year_offset + 1)
            present_value_stage_two_dividends += present_value_dividend_this_year

            stage_two_yearly_breakdown_data.append({
                "Year": f"Year {n_years1 + year_offset + 1}",
                "Dividend": self._format_value(dividend_per_share_current_year),
                "PV": self._format_value(present_value_dividend_this_year)
            })

        # Add sum row for Stage 2
        stage_two_df = pd.DataFrame(stage_two_yearly_breakdown_data).set_index("Year")
        stage_two_df.loc["Sum"] = {
            "Dividend": "—",
            "PV": self._format_value(present_value_stage_two_dividends)
        }

        stage_two_pv_formatted = self._format_value(present_value_stage_two_dividends)

        calculation_steps_list.append({
            "step": "Stage 2 Dividends (Stable Growth)",
            "description": f"Stable growth dividend phase ({n_years2} years)",
            "latex": rf"PV_2 = \sum_{{k=1}}^{{N_2}} \dfrac{{DPS_{{N_1+k}}}}{{(1 + k_e)^{{N_1+k}}}} = {stage_two_pv_formatted}",
            "explanation": f"Present value of Stage 2 dividends = {stage_two_pv_formatted}",
            "details": {"yearly_table": stage_two_df}
        })

        # Terminal value
        dividend_next_year = dividend_per_share_current_year * (1.0 + terminal_growth)
        cost_of_equity_minus_growth = (cost_of_equity - terminal_growth)

        if cost_of_equity_minus_growth is None or not np.isfinite(
                cost_of_equity_minus_growth) or cost_of_equity_minus_growth <= 0:
            terminal_value_perpetuity = float("nan")
            calculation_steps_list.append({
                "step": "Terminal Value Calculation",
                "description": "ERROR: Invalid denominator",
                "details": {"Issue": "Cost of equity must exceed terminal growth (k_e > g_term)"}
            })
        else:
            terminal_value_perpetuity = dividend_next_year / cost_of_equity_minus_growth

            div_next_formatted = self._format_value(dividend_next_year)
            denominator_formatted = self._format_value(cost_of_equity_minus_growth)
            terminal_value_formatted = self._format_value(terminal_value_perpetuity)

            calculation_steps_list.append({
                "step": "Terminal Value (Gordon Growth Model)",
                "description": "Perpetuity value of dividends",
                "latex": rf"TV = \dfrac{{DPS_{{final}} \times (1 + g_{{term}})}}{{k_e - g_{{term}}}} = {terminal_value_formatted}",
                "explanation": f"where DPS_final × (1+g_term) = {div_next_formatted}, (k_e - g_term) = {denominator_formatted}",
            })

        total_years_projection = n_years1 + n_years2
        present_value_of_terminal = terminal_value_perpetuity / (1.0 + cost_of_equity) ** total_years_projection

        pv_terminal_formatted = self._format_value(present_value_of_terminal)

        calculation_steps_list.append({
            "step": "Discount Terminal Value to Present",
            "description": "Bring terminal value to present",
            "latex": rf"PV_{{TV}} = \dfrac{{TV}}{{(1 + k_e)^{{N_1+N_2}}}} = {pv_terminal_formatted}",
            "explanation": f"where TV = {self._format_value(terminal_value_perpetuity)}, N1+N2 = {total_years_projection}",
        })

        fair_price_per_share = present_value_stage_one_dividends + present_value_stage_two_dividends + present_value_of_terminal

        fair_price_formatted = self._format_value(fair_price_per_share)

        calculation_steps_list.append({
            "step": "Fair Price Per Share",
            "description": "Sum all present values",
            "latex": rf"P_0 = PV_1 + PV_2 + PV_{{TV}} = {fair_price_formatted}",
            "explanation": f"where PV1 = {stage_one_pv_formatted}, PV2 = {stage_two_pv_formatted}, PV_TV = {pv_terminal_formatted}",
        })

        return fair_price_per_share, calculation_steps_list

    def return_on_equity(
            self, conservative_growth_rate, discount_rate, average_market_return, n_years
    ) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        return_on_equity_median = _safe_median(self.stock.return_on_equity, n=3)
        dividend_per_share_mean = _safe_mean(self.stock.dividend_per_share_history, n=3)
        book_value_per_share_series = _safe_div(self.stock.total_equity, self.stock.shares_outstanding)
        book_value_per_share_mean = _safe_mean(book_value_per_share_series, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather profitability and dividend inputs",
            "input_table": {
                "ROE (3-year median)": self._format_value(return_on_equity_median),
                "Dividend Per Share (3-year mean)": self._format_value(dividend_per_share_mean),
                "Book Value Per Share (3-year mean)": self._format_value(book_value_per_share_mean),
                "Growth Rate (g)": self._format_value(conservative_growth_rate),
                "Discount Rate (r)": self._format_value(discount_rate),
                "Average Market Return": self._format_value(average_market_return),
                "Projection Years (N)": str(n_years)
            }
        })

        # Project dividends
        present_value_of_all_dividends = 0.0
        book_value_per_share_current_year = book_value_per_share_mean
        dividend_per_share_current_year = dividend_per_share_mean
        dividend_projection_breakdown_data = []

        for year_index in range(n_years):
            book_value_per_share_current_year = book_value_per_share_current_year * (1.0 + conservative_growth_rate)
            dividend_per_share_current_year = dividend_per_share_current_year * (1.0 + conservative_growth_rate)
            present_value_dividend_this_year = dividend_per_share_current_year / (1.0 + discount_rate) ** (
                        year_index + 1)
            present_value_of_all_dividends += present_value_dividend_this_year

            dividend_projection_breakdown_data.append({
                "Year": f"Year {year_index + 1}",
                "BVPS": self._format_value(book_value_per_share_current_year),
                "DPS": self._format_value(dividend_per_share_current_year),
                "PV of DPS": self._format_value(present_value_dividend_this_year)
            })

        pv_dividends_formatted = self._format_value(present_value_of_all_dividends)
        growth_formatted = self._format_value(conservative_growth_rate)

        calculation_steps_list.append({
            "step": "Dividend Projection",
            "description": "Project BVPS and dividends with growth",
            "latex": r"BVPS_t = BVPS_0 \times (1 + g)^t, \quad DPS_t = DPS_0 \times (1 + g)^t",
            "explanation": f"where g = {growth_formatted}, Total PV of Dividends = {pv_dividends_formatted}",
            "details": {"yearly_table": pd.DataFrame(dividend_projection_breakdown_data).set_index("Year")}
        })

        # Terminal value from earnings
        net_income_per_share_final_year = book_value_per_share_current_year * return_on_equity_median

        if average_market_return is None or not np.isfinite(average_market_return) or average_market_return <= 0:
            terminal_value_at_horizon = float("nan")
            calculation_steps_list.append({
                "step": "Terminal Value Calculation",
                "description": "ERROR: Invalid market return",
                "details": {"Issue": "Average market return must be positive"}
            })
        else:
            terminal_value_at_horizon = net_income_per_share_final_year / average_market_return
            present_value_of_terminal = terminal_value_at_horizon / (1.0 + discount_rate) ** n_years

            final_bvps_formatted = self._format_value(book_value_per_share_current_year)
            final_ni_formatted = self._format_value(net_income_per_share_final_year)
            market_return_formatted = self._format_value(average_market_return)
            terminal_value_formatted = self._format_value(terminal_value_at_horizon)

            calculation_steps_list.append({
                "step": "Terminal Value from Earnings",
                "description": "Capitalize final NI using market return",
                "latex": rf"TV = \dfrac{{BVPS_N \times ROE}}{{Market\ Return}} = {terminal_value_formatted}",
                "explanation": f"where BVPS_N = {final_bvps_formatted}, ROE × BVPS_N = {final_ni_formatted}, Market Return = {market_return_formatted}",
            })

            pv_terminal_formatted = self._format_value(present_value_of_terminal)

            calculation_steps_list.append({
                "step": "Discount Terminal Value to Present",
                "description": "Bring terminal value to present",
                "latex": rf"PV_{{TV}} = \dfrac{{TV}}{{(1 + r)^N}} = {pv_terminal_formatted}",
                "explanation": f"where TV = {terminal_value_formatted}, (1+r)^N = {self._format_value((1.0 + discount_rate) ** n_years)}",
            })

            fair_price_per_share = present_value_of_all_dividends + present_value_of_terminal
            fair_price_formatted = self._format_value(fair_price_per_share)

            calculation_steps_list.append({
                "step": "Fair Price Per Share",
                "description": "Sum dividend PV and terminal PV",
                "latex": rf"P_0 = PV_{{Div}} + PV_{{TV}} = {fair_price_formatted}",
                "explanation": f"where PV_Div = {pv_dividends_formatted}, PV_TV = {pv_terminal_formatted}",
            })

        return fair_price_per_share if 'fair_price_per_share' in locals() else float("nan"), calculation_steps_list

    def excess_return(
            self, conservative_growth_rate, cost_of_equity
    ) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        return_on_equity_median = _safe_median(self.stock.return_on_equity, n=3)
        total_equity_median = _safe_median(self.stock.total_equity, n=3)
        shares_outstanding_median = _safe_median(self.stock.shares_outstanding, n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Gather profitability and equity inputs",
            "input_table": {
                "ROE (3-year median)": self._format_value(return_on_equity_median),
                "Total Equity (3-year median)": self._format_value(total_equity_median),
                "Shares Outstanding (3-year median)": self._format_value(shares_outstanding_median),
                "Cost of Equity (k_e)": self._format_value(cost_of_equity),
                "Growth Rate (g)": self._format_value(conservative_growth_rate)
            }
        })

        # Excess return
        excess_return_dollar_value = (return_on_equity_median - cost_of_equity) * total_equity_median

        roe_formatted = self._format_value(return_on_equity_median)
        cost_equity_formatted = self._format_value(cost_of_equity)
        equity_formatted = self._format_value(total_equity_median)
        excess_return_formatted = self._format_value(excess_return_dollar_value)
        spread_formatted = self._format_value(
            return_on_equity_median - cost_of_equity if return_on_equity_median and cost_of_equity else None)

        calculation_steps_list.append({
            "step": "Excess Return Calculation",
            "description": "Calculate value created above required return",
            "latex": rf"ER = (ROE - k_e) \times Total\ Equity = {excess_return_formatted}",
            "explanation": f"where ROE = {roe_formatted}, k_e = {cost_equity_formatted}, ROE - k_e = {spread_formatted}, Total Equity = {equity_formatted}",
        })

        # Perpetuity value
        cost_of_equity_minus_growth = (cost_of_equity - conservative_growth_rate)

        if cost_of_equity_minus_growth is None or not np.isfinite(
                cost_of_equity_minus_growth) or cost_of_equity_minus_growth <= 0:
            present_value_of_excess_returns = float("nan")
            calculation_steps_list.append({
                "step": "Perpetuity Value",
                "description": "ERROR: Invalid denominator",
                "details": {"Issue": "Cost of equity must exceed growth rate (k_e > g)"}
            })
        else:
            present_value_of_excess_returns = excess_return_dollar_value / cost_of_equity_minus_growth

            denominator_formatted = self._format_value(cost_of_equity_minus_growth)
            pv_excess_returns_formatted = self._format_value(present_value_of_excess_returns)

            calculation_steps_list.append({
                "step": "Perpetuity Value of Excess Returns",
                "description": "Capitalize excess returns as perpetuity",
                "latex": rf"PV_{{ER}} = \dfrac{{ER}}{{k_e - g}} = {pv_excess_returns_formatted}",
                "explanation": f"where ER = {excess_return_formatted}, (k_e - g) = {denominator_formatted}",
            })

        # Fair price per share
        if shares_outstanding_median is None or not np.isfinite(
                shares_outstanding_median) or shares_outstanding_median <= 0:
            fair_price_per_share = float("nan")
            calculation_steps_list.append({
                "step": "ERROR",
                "description": "Invalid shares outstanding"
            })
        else:
            total_equity_value = total_equity_median + (
                present_value_of_excess_returns if 'present_value_of_excess_returns' in locals() else 0)
            fair_price_per_share = total_equity_value / shares_outstanding_median

            equity_value_formatted = self._format_value(total_equity_value)
            shares_formatted = self._format_value(shares_outstanding_median)
            fair_price_formatted = self._format_value(fair_price_per_share)

            calculation_steps_list.append({
                "step": "Fair Price Per Share",
                "description": "Add book value and excess return value",
                "latex": rf"P_0 = \dfrac{{Total\ Equity + PV_{{ER}}}}{{Shares}} = {fair_price_formatted}",
                "explanation": f"where Total Equity = {equity_formatted}, PV_ER = {self._format_value(present_value_of_excess_returns)}, Shares = {shares_formatted}",
            })

        return fair_price_per_share if 'fair_price_per_share' in locals() else float("nan"), calculation_steps_list

    def graham_number(self) -> tuple[float, List[Dict[str, Any]]]:
        """Returns (fair_price, calculation_steps)"""
        calculation_steps_list = []

        # Inputs
        earnings_per_share_median = _safe_median(self.stock.earning_per_share, n=3)
        book_value_per_share_median = _safe_median(
            _safe_div(self.stock.total_equity, self.stock.shares_outstanding), n=3)

        calculation_steps_list.append({
            "step": "Input Collection",
            "description": "Benjamin Graham's conservative valuation formula",
            "input_table": {
                "EPS (3-year median)": self._format_value(earnings_per_share_median),
                "BVPS (3-year median)": self._format_value(book_value_per_share_median)
            }
        })

        # Calculation
        product_of_eps_and_bvps = 22.5 * earnings_per_share_median * book_value_per_share_median

        eps_formatted = self._format_value(earnings_per_share_median)
        bvps_formatted = self._format_value(book_value_per_share_median)
        product_formatted = self._format_value(product_of_eps_and_bvps)

        calculation_steps_list.append({
            "step": "Product Calculation",
            "description": "Multiply EPS and BVPS by Graham's constant",
            "latex": rf"Product = 22.5 \times EPS \times BVPS = {product_formatted}",
            "explanation": f"where EPS = {eps_formatted}, BVPS = {bvps_formatted}",
        })

        if product_of_eps_and_bvps < 0 or not np.isfinite(product_of_eps_and_bvps):
            fair_price_per_share = float("nan")
            calculation_steps_list.append({
                "step": "Graham Number",
                "description": "ERROR: Product must be positive and finite",
                "details": {"Fair Price": "NaN"}
            })
        else:
            fair_price_per_share = math.sqrt(product_of_eps_and_bvps)
            fair_price_formatted = self._format_value(fair_price_per_share)

            calculation_steps_list.append({
                "step": "Graham Number (Square Root)",
                "description": "Take square root of the product",
                "latex": rf"P_0 = \sqrt{{Product}} = {fair_price_formatted}",
                "explanation": f"where Product = {product_formatted}",
            })

        return fair_price_per_share, calculation_steps_list

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
        earning_growth_estimates = None
        conservative_growth_on_earning = None

        if margin_of_safety is None:
            margin_of_safety = DEFAULT_PARAM_DICT["margin_of_safety"]

        if growth_rate is None:
            earning_growth_estimates, conservative_growth_on_earning = self.estimate_earning_growth_rate(
                margin_of_safety)

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
            earning_growth_estimates, conservative_growth_on_earning = self.estimate_earning_growth_rate(
                margin_of_safety)
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

        growth_estimates_from_dividend, conservative_growth_on_dividend = self.estimate_dividend_growth_rate(
            margin_of_safety)

        # --- Compute each model with calculation tracking ---
        fair_price_PEM, calc_PEM = self.price_earning_multiples(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            n_years=n_years1,
        )

        fair_price_DCF_1, calc_DCF_1 = self.discounted_cash_flow_one_stage(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            decline_rate=decline_rate,
            n_years=n_years1,
        )

        fair_price_DCF_2, calc_DCF_2 = self.discounted_cash_flow_two_stage(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            decline_rate=decline_rate,
            n_years1=n_years1,
            n_years2=n_years2,
            terminal_growth=terminal_growth_rate,
        )

        fair_price_ROE, calc_ROE = self.return_on_equity(
            conservative_growth_rate=conservative_growth_on_earning,
            discount_rate=discount_rate,
            average_market_return=average_market_return,
            n_years=n_years1,
        )

        fair_price_DDM, calc_DDM = self.discounted_dividend_two_stage(
            conservative_growth_rate=conservative_growth_on_dividend,
            cost_of_equity=self.stock.cost_of_equity if hasattr(self.stock, 'cost_of_equity') else discount_rate,
            n_years1=n_years1,
            n_years2=n_years2,
            terminal_growth=terminal_growth_rate,
        )

        fair_price_ER, calc_ER = self.excess_return(
            conservative_growth_rate=conservative_growth_on_earning,
            cost_of_equity=self.stock.cost_of_equity if hasattr(self.stock, 'cost_of_equity') else discount_rate,
        )

        fair_price_GRAHAM, calc_GRAHAM = self.graham_number()

        # --- Package results with calculation breakdown ---
        results: Dict[str, Dict[str, Any]] = {}

        r_pem = VALUATION["price_earning_multiples"].copy()
        r_pem["outputs"] = {"Fair Value": fair_price_PEM}
        r_pem["calculation"] = calc_PEM
        results["price_earning_multiples"] = r_pem

        r_dcf1 = VALUATION["discounted_cash_flow_one_stage"].copy()
        r_dcf1["outputs"] = {"Fair Value": fair_price_DCF_1}
        r_dcf1["calculation"] = calc_DCF_1
        results["discounted_cash_flow_one_stage"] = r_dcf1

        r_dcf2 = VALUATION["discounted_cash_flow_two_stage"].copy()
        r_dcf2["outputs"] = {"Fair Value": fair_price_DCF_2}
        r_dcf2["calculation"] = calc_DCF_2
        results["discounted_cash_flow_two_stage"] = r_dcf2

        r_roe = VALUATION["return_on_equity"].copy()
        r_roe["outputs"] = {"Fair Value": fair_price_ROE}
        r_roe["calculation"] = calc_ROE
        results["return_on_equity"] = r_roe

        r_ddm = VALUATION["discounted_dividend_two_stage"].copy()
        r_ddm["outputs"] = {"Fair Value": fair_price_DDM}
        r_ddm["calculation"] = calc_DDM
        results["discounted_dividend_two_stage"] = r_ddm

        r_er = VALUATION["excess_return"].copy()
        r_er["outputs"] = {"Fair Value": fair_price_ER}
        r_er["calculation"] = calc_ER
        results["excess_return"] = r_er

        r_gn = VALUATION["graham_number"].copy()
        r_gn["outputs"] = {"Fair Value": fair_price_GRAHAM}
        r_gn["calculation"] = calc_GRAHAM
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
            earning_growth_estimates = DEFAULT_PARAM_DICT["growth_rate"]

        conservative_growth_on_earning = earning_growth_estimates * (1.0 - margin_of_safety)

        return earning_growth_estimates, conservative_growth_on_earning

    def estimate_dividend_growth_rate(self, margin_of_safety):
        growth_estimates_from_dividend = _safe_median(self.stock.dividend_per_share_yoy_growth, n=5)
        if np.isnan(growth_estimates_from_dividend):
            return np.nan, np.nan

        conservative_growth_on_dividend = growth_estimates_from_dividend * (1.0 - margin_of_safety)

        return growth_estimates_from_dividend, conservative_growth_on_dividend

    def get_discount_rate(self, discount_rate: float | None, risk_free_rate=None,
                          average_market_return=None) -> float | None:
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

        from utils.stock import _safe_add
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