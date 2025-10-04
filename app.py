from __future__ import annotations

from typing import Dict, Any, Optional, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from textwrap import dedent as textwrap_dedent
import html as html_module
import plotly.graph_objects as go
from plotly.graph_objs import Figure
import plotly.express as px
import yfinance as yf

# ---- project modules
from core.valuation import Valuation
from core.constants import (
    DEFAULT_PARAM_DICT,
    CRITERION,
    VALUATION,
    FINANCIALS,
    DERIVED_METRICS,
    STOCK_INFO,
    KEY_RATIO_DICT
)

from utils.prompt_templates import PROMPT_TEMPLATE
from core.macros import MacroEconomic
from core.evaluation import Evaluator
from core.stock import Stock
from configs import macro_cfg

# =============================================================================
# Page config
# =============================================================================
st.set_page_config(page_title="Value Investing Dashboard", page_icon="📈", layout="wide")

# =============================================================================
# Enhanced Global CSS — responsive design for PC, iPad, Phone
# =============================================================================
st.markdown(
    """
    <style>
      :root{
        --bg: #0A1120;
        --bg2: #101A2E;
        --border: rgba(255,255,255,0.08);
        --text: #E6EEF7;
        --muted: rgba(230,238,247,0.7);
        --accent: #5FE3B9;
        --btn-secondary-bg: #2A3553;
        --btn-secondary-bg-hover: #324266;
        --btn-secondary-border: rgba(255,255,255,0.14);
        --btn-secondary-text: #E6EEF7;
      }

      /* Base layout */
      .block-container { 
        padding-top: 1.2rem; 
        padding-bottom: 2rem;
      }

      [data-baseweb="tab-panel"] { overflow: visible; }
      .stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); }
      .stTabs [aria-selected="true"] { color: var(--text); border-bottom: 2px solid var(--accent); }
      h1,h2,h3,h4 { color: var(--text); letter-spacing: 0.1px; }

      /* App cards */
      .app-card{
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
        position: relative;
        margin-bottom: 18px;
      }

      .app-card h3, .app-card h4{ margin: 0 0 8px 0; }
      .keyline{ height:1px; background: rgba(255,255,255,0.10); margin:10px 0; }

      .kv{ 
        display:flex; 
        align-items:baseline; 
        gap:8px; 
        margin:6px 0;
        flex-wrap: wrap;
      }
      .kv .k{ 
        color: var(--muted); 
        min-width:140px; 
        font-size:0.92rem;
      }
      .kv .v{ 
        color: var(--text); 
        font-weight:600; 
        font-size:1.05rem;
      }

      .chip{
        display:inline-block; 
        padding:4px 12px; 
        border-radius:999px;
        border:1px solid var(--border); 
        font-size:0.82rem; 
        color: var(--muted);
        margin-right:6px; 
        margin-bottom:6px; 
        background: rgba(255,255,255,0.02);
      }

      .company-header {
        display:flex; 
        align-items:center; 
        gap:10px; 
        flex-wrap:wrap;
        margin:-6px 0 12px 0;
      }
      .company-name { 
        font-weight:700; 
        font-size:1.3rem; 
        color:var(--text); 
      }

      .row-spacer { height: 18px; }

      /* Buttons */
      .stButton > button{
        min-height: 44px;
        font-size: 0.95rem;
      }

      .stButton > button[kind="secondary"]{
        background: var(--btn-secondary-bg);
        color: var(--btn-secondary-text);
        border: 1px solid var(--btn-secondary-border);
      }

      .stButton > button[kind="secondary"]:hover:not(:disabled){
        background: var(--btn-secondary-bg-hover);
        border-color: var(--btn-secondary-border);
      }

      .stButton > button[kind="secondary"]:disabled{
        opacity: .55;
        cursor: not-allowed;
      }

      /* Mobile Optimizations */
      @media (max-width: 768px){
        .block-container{
          padding-left: 1rem;
          padding-right: 1rem;
        }

        .app-card{
          padding: 14px;
        }

        .company-name{
          font-size: 1.1rem;
        }

        .chip{
          font-size: 0.75rem;
          padding: 3px 8px;
        }

        .kv .k{
          min-width: 100px;
          font-size: 0.88rem;
        }

        .kv .v{
          font-size: 0.98rem;
        }

        h4{
          font-size: 1rem;
        }
      }

      .streamlit-expanderHeader { 
        font-weight:600; 
        font-size: 0.95rem;
      }

      details > summary{
        cursor: pointer;
        padding: 8px 0;
        word-wrap: break-word;
      }

      details{
        border-bottom: 1px solid var(--border);
        margin: 4px 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# Utility functions
# =============================================================================
def is_missing(x: Any) -> bool:
    try:
        return pd.isna(x) or (isinstance(x, float) and not np.isfinite(x))
    except Exception:
        return False


def _trim_trailing_zeros(text: str) -> str:
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_compact_number(value: Any, *, decimals: int = 2) -> str:
    """Format large numbers to K/M/B/T; smaller numbers keep thousands separators."""
    try:
        x = float(value)
    except Exception:
        return "—"
    if not np.isfinite(x):
        return "—"

    sign = "-" if x < 0 else ""
    x = abs(x)

    thresholds = [
        (1e12, "T"),
        (1e9, "B"),
        (1e6, "M"),
        (1e3, "K"),
    ]
    for thr, suf in thresholds:
        if x >= thr:
            num = x / thr
            return f"{sign}{_trim_trailing_zeros(f'{num:.{decimals}f}')}{suf}"

    if x < 1:
        return f"{sign}{_trim_trailing_zeros(f'{x:.{decimals}f}')}"
    return f"{sign}{_trim_trailing_zeros(f'{x:,.{decimals}f}')}" if x % 1 else f"{sign}{int(x):,}"


def fmt_ratio(value: Any, suffix: str = "") -> str:
    """Generic numeric formatter (2 decimals)."""
    if is_missing(value):
        return "—"
    try:
        return f"{float(value):,.2f}{suffix}"
    except Exception:
        return "—"


def get_latest(series: Optional[pd.Series]) -> Any:
    """Return the first (most-recent) value of a time-indexed series, else NaN."""
    if isinstance(series, pd.Series) and not series.empty:
        return series.iloc[0]
    return np.nan


# =============================================================================
# Layout helpers
# =============================================================================
def insert_vertical_row_spacing(spacing_height_px: int = 18) -> None:
    st.markdown(
        f"<div class='row-spacer' style='height:{int(spacing_height_px)}px;'></div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# Param defaults
# =============================================================================
def ensure_default_param_keys() -> None:
    if "_apply_pending_params" in st.session_state and st.session_state["_apply_pending_params"]:
        pending = st.session_state.get("_pending_params", {})
        for key, value in pending.items():
            st.session_state[key] = value
        st.session_state["_apply_pending_params"] = False
        st.session_state["_pending_params"] = {}

    st.session_state.setdefault("discount_rate", float(DEFAULT_PARAM_DICT["discount_rate"]))
    st.session_state.setdefault("growth_rate", float(DEFAULT_PARAM_DICT["growth_rate"]))
    st.session_state.setdefault("decline_rate", float(DEFAULT_PARAM_DICT["decline_rate"]))
    st.session_state.setdefault("terminal_growth_rate", float(DEFAULT_PARAM_DICT["terminal_growth_rate"]))
    st.session_state.setdefault("margin_of_safety", float(DEFAULT_PARAM_DICT["margin_of_safety"]))
    st.session_state.setdefault("n_years1", int(DEFAULT_PARAM_DICT["n_years1"]))
    st.session_state.setdefault("n_years2", int(DEFAULT_PARAM_DICT["n_years2"]))
    st.session_state.setdefault("risk_free_rate", float(DEFAULT_PARAM_DICT["risk_free_rate"]))
    st.session_state.setdefault("average_market_return", float(DEFAULT_PARAM_DICT["average_market_return"]))
    st.session_state.setdefault("has_run", False)

    st.session_state.setdefault("url_10k", "https://example.com/10k.pdf")
    st.session_state.setdefault("url_10q", "https://example.com/10q.pdf")
    st.session_state.setdefault("url_extra", "https://example.com/extra")
    st.session_state.setdefault("ticker_input", "AAPL")
    st.session_state.setdefault("_show_prompt_success", False)
    st.session_state.setdefault("_top_error", "")
    st.session_state.setdefault("_pending_params", {})
    st.session_state.setdefault("_apply_pending_params", False)
    st.session_state.setdefault("user_modified_params", set())


def _on_run_clicked_reset_urls_if_ticker_changed() -> None:
    """Reset 10-K/10-Q/Extra to placeholders if ticker changed."""
    current_typed_ticker = (st.session_state.get("ticker_input") or "").strip().upper()
    previous_ticker = st.session_state.get("last_ticker")

    if previous_ticker is None or current_typed_ticker != previous_ticker:
        st.session_state["url_10k"] = "https://example.com/10k.pdf"
        st.session_state["url_10q"] = "https://example.com/10q.pdf"
        st.session_state["url_extra"] = "https://example.com/extra"
        st.session_state["generated_prompt_text"] = ""
        st.session_state["_show_prompt_success"] = False
        st.session_state["user_modified_params"] = set()

        # Reset params to defaults
        st.session_state["discount_rate"] = float(DEFAULT_PARAM_DICT["discount_rate"])
        st.session_state["growth_rate"] = float(DEFAULT_PARAM_DICT["growth_rate"])
        st.session_state["decline_rate"] = float(DEFAULT_PARAM_DICT["decline_rate"])
        st.session_state["terminal_growth_rate"] = float(DEFAULT_PARAM_DICT["terminal_growth_rate"])
        st.session_state["margin_of_safety"] = float(DEFAULT_PARAM_DICT["margin_of_safety"])
        st.session_state["n_years1"] = int(DEFAULT_PARAM_DICT["n_years1"])
        st.session_state["n_years2"] = int(DEFAULT_PARAM_DICT["n_years2"])
        st.session_state["risk_free_rate"] = float(DEFAULT_PARAM_DICT["risk_free_rate"])
        st.session_state["average_market_return"] = float(DEFAULT_PARAM_DICT["average_market_return"])


# =============================================================================
# Fetch & compute
# =============================================================================
@st.cache_resource(show_spinner=False)
def fetch_stock(ticker_symbol: str) -> Stock:
    """Fetch Stock object with validation."""
    data = yf.Ticker(ticker_symbol)
    prices = yf.download(tickers=[ticker_symbol], interval="1d", period="10y")

    if not isinstance(prices, pd.DataFrame) or prices.empty or ("Close" not in prices.columns):
        raise ValueError(
            f"No price data returned for '{ticker_symbol}'. "
            "Please double-check the ticker symbol. For non-US listings, use Yahoo Finance's suffix format, e.g.: "
            "Japan: 9697.T   Poland: CDR.WA   Hong Kong: 0700.HK   London: ULVR.L"
        )

    return Stock(data=data, prices=prices)


def run_evaluation_only() -> Dict[str, Any]:
    macros = MacroEconomic(
        macro_cfg["base_currency_country"],
        st.session_state.stock.country,
        macro_cfg["macro_years"],
        macro_cfg["fx_years"],
        macro_cfg["ca_years"],
        macro_cfg["inflation_years"],
    )
    evaluator = Evaluator(st.session_state.stock, macros)
    return evaluator.run_all()


def run_valuation_only(stock_obj: Stock, user_param_overrides: Dict[str, Any]) -> Dict[str, Any]:
    val = Valuation(stock_obj)
    return val.valuate(
        margin_of_safety=user_param_overrides.get("margin_of_safety"),
        growth_rate=user_param_overrides.get("growth_rate"),
        discount_rate=user_param_overrides.get("discount_rate"),
        risk_free_rate=user_param_overrides.get("risk_free_rate"),
        average_market_return=user_param_overrides.get("average_market_return"),
        decline_rate=user_param_overrides.get("decline_rate"),
        n_years1=user_param_overrides.get("n_years1"),
        n_years2=user_param_overrides.get("n_years2"),
        terminal_growth_rate=user_param_overrides.get("terminal_growth_rate"),
    )


# =============================================================================
# Charts
# =============================================================================
def render_fair_value_table_card(current_price_float: float, fair_value_payload: Dict[str, Any]) -> None:
    method_display_map = {
        "price_earning_multiples": "PE Multiple",
        "discounted_cash_flow_one_stage": "Discounted Cashflow (One-Stage)",
        "discounted_cash_flow_two_stage": "Discounted Cashflow (Two-Stage)",
        "discounted_dividend_two_stage": "Discounted Dividend (Two-Stage)",
        "return_on_equity": "Return on Equity",
        "excess_return": "Excess Return",
        "graham_number": "Graham Number",
    }

    rows: List[Dict[str, Any]] = []
    for method_key, payload in fair_value_payload.items():
        if isinstance(payload, dict):
            fv = payload.get("outputs", {}).get("Fair Value", np.nan)
            if isinstance(fv, (int, float)) and np.isfinite(fv):
                rows.append({"Method": method_display_map.get(method_key, method_key), "FairValue": float(fv)})

    if isinstance(current_price_float, (int, float)) and np.isfinite(current_price_float) and current_price_float > 0:
        rows.sort(key=lambda r: r["FairValue"] / current_price_float, reverse=True)
    else:
        rows.sort(key=lambda r: r["FairValue"], reverse=True)

    if rows:
        df_rows = []
        for row_dict in rows:
            fv = row_dict["FairValue"]
            if isinstance(current_price_float, (int, float)) and np.isfinite(
                    current_price_float) and current_price_float > 0:
                upside_ratio = fv / current_price_float - 1.0
                upside_text = f"{upside_ratio:.0%}"
            else:
                upside_text = "—"

            df_rows.append({
                "Method": row_dict['Method'],
                "Fair Value": format_compact_number(fv),
                "Upside": upside_text
            })

        st.markdown("#### Fair Value")
        if isinstance(current_price_float, (int, float)) and np.isfinite(current_price_float):
            st.caption(f"Current Price: **{format_compact_number(current_price_float)}**")

        df = pd.DataFrame(df_rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Method": st.column_config.TextColumn("Method", width="medium"),
                "Fair Value": st.column_config.TextColumn("Fair Value", width="small"),
                "Upside": st.column_config.TextColumn("Upside", width="small"),
            }
        )
    else:
        st.markdown("#### Fair Value")
        st.caption("No fair value results available.")


def build_price_line_chart(price_dataframe: pd.DataFrame, *, height: int = 300,
                           margin: Optional[dict] = None) -> Figure:
    if price_dataframe is None or price_dataframe.empty:
        raise ValueError("price_dataframe is empty.")
    margin = margin or dict(l=10, r=10, t=10, b=10)

    df = price_dataframe.copy().reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    if "Close" not in df.columns:
        raise ValueError("Expected a 'Close' column in price_dataframe.")

    monthly = df.sort_values("Date").set_index("Date")["Close"].resample("M").last().reset_index()
    fig = px.line(monthly, x="Date", y="Close", height=height, labels={"Date": "Date", "Close": "Close"})
    fig.update_traces(line=dict(width=2.8), hovertemplate="Month: %{x|%Y-%m}<br>Close: %{y:.2f}<extra></extra>")
    fig.update_xaxes(tickformat="%Y-%m", ticklabelmode="period", showgrid=True, gridwidth=1,
                     gridcolor="rgba(255,255,255,0.10)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.10)")
    fig.update_layout(margin=margin, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig


def compute_category_scores_for_radar(evaluation_payload: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for category_key, signals in evaluation_payload.items():
        if not isinstance(signals, dict) or len(signals) == 0:
            scores[category_key] = 0.0
            continue
        numeric_values: List[float] = []
        for _, result in signals.items():
            v = result.get("check", 0.0)
            if isinstance(v, (int, float)) and np.isfinite(v):
                numeric_values.append(float(v))
        scores[category_key] = float(np.sum(numeric_values)) if numeric_values else 0.0
    return scores


def build_radar_chart(radar_labels: List[str], radar_values: List[float], *, height: int = 300, edge_pad: float = 0.08,
                      margin: Optional[dict] = None) -> Figure:
    margin = margin or dict(l=18, r=18, t=8, b=8)
    if not radar_labels or not radar_values or len(radar_labels) != len(radar_values):
        empty = go.Figure();
        empty.update_layout(height=height, margin=margin);
        return empty
    labels_closed = radar_labels + [radar_labels[0]]
    values_closed = radar_values + [radar_values[0]]
    pad = max(0.0, min(0.2, float(edge_pad)))
    domain = dict(x=[pad, 1.0 - pad], y=[pad, 1.0 - pad])
    fig = go.Figure(data=go.Scatterpolar(
        r=values_closed, theta=[l.capitalize() for l in labels_closed],
        fill="toself", name="Scores", mode="lines+markers",
        line=dict(width=3.5, shape="spline"), marker=dict(size=5),
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>", cliponaxis=False,
    ))
    fig.update_layout(
        height=height, margin=margin,
        polar=dict(
            domain=domain, bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 6], showticklabels=False, ticks='',
                            gridcolor="rgba(255,255,255,0.10)", linecolor="rgba(255,255,255,0.20)"),
            angularaxis=dict(tickfont=dict(size=14, color="#E6EEF7"), gridcolor="rgba(255,255,255,0.08)",
                             linecolor="rgba(255,255,255,0.20)"),
        ),
        showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# =============================================================================
# Key Ratios - Using st.dataframe
# =============================================================================
def build_key_ratios_from_config(stock_obj: Stock) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for key, meta in KEY_RATIO_DICT.items():
        attr_name = meta.get("attr")
        kind = meta.get("kind")
        fancy_name = meta.get("fancy_name", key)
        fmt_kind = meta.get("format", "raw")

        src = getattr(stock_obj, attr_name, None)
        if kind == "scalar":
            value = src
        elif kind == "series_latest":
            value = get_latest(src if isinstance(src, pd.Series) else pd.Series(dtype=float))
        else:
            value = None

        items.append({"key": key, "fancy_name": fancy_name, "value": value, "format": fmt_kind})
    return items


def render_key_ratios_card(key_ratios_payload: List[Dict[str, Any]]) -> None:
    def _fmt(value: Any, kind: str) -> str:
        if kind == "ratio":
            return fmt_ratio(value)
        if kind == "money":
            return format_compact_number(value)
        try:
            return format_compact_number(float(value))
        except Exception:
            return "—" if value is None else str(value)

    st.markdown("#### Key Ratios")

    if key_ratios_payload:
        df_rows = []
        for item in key_ratios_payload:
            df_rows.append({
                "Metric": item.get('fancy_name', item.get('key', '—')),
                "Value": _fmt(item.get('value'), item.get('format', 'raw'))
            })

        df = pd.DataFrame(df_rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Metric": st.column_config.TextColumn("Metric", width="medium"),
                "Value": st.column_config.TextColumn("Value", width="small"),
            }
        )
    else:
        st.caption("No key ratios available.")


# =============================================================================
# News, About, Officers
# =============================================================================
def _news_items_html(stock_obj: Stock) -> str:
    news_items = getattr(stock_obj, "news", None) or getattr(stock_obj, "company_news", None)
    if not isinstance(news_items, list) or not news_items:
        return "<div style='opacity:.8;'>No recent news available.</div>"

    rows: List[str] = []
    for item in news_items[:15]:
        date_str, title, summary, link = None, None, "", None
        if isinstance(item, (list, tuple)) and len(item) >= 4:
            date_str = item[0];
            title = item[1];
            summary = item[2] if item[2] is not None else "";
            link = item[-1]
        elif isinstance(item, dict):
            n = item
            date_str = n.get("pubDate") or n.get("published") or n.get("providerPublishTime") or ""
            title = n.get("title") or n.get("headline") or "News"
            summary = n.get("summary") or n.get("content") or ""
            url_obj = n.get("canonicalUrl") or {}
            link = url_obj.get("url") if isinstance(url_obj, dict) else (n.get("link") or n.get("url"))
        else:
            continue

        if not title: title = "News"
        summary_line = f"{date_str or ''} — {title}"
        if link: summary_line += f" — <a href='{link}' target='_blank' style='color:#4EA1FF;'>link</a>"
        body_html = f"<div style='margin:6px 0 8px 0;'>{summary}</div>" if summary else ""
        rows.append(
            f"<details style='margin:6px 0; padding:8px 0;'>"
            f"<summary style='cursor:pointer; opacity:.95;'>{summary_line}</summary>"
            f"{body_html}"
            f"</details>"
        )
    return "".join(rows) if rows else "<div style='opacity:.8;'>No recent news available.</div>"


def render_about_news_officers_tabbed(stock_obj: Stock) -> None:
    tab_about, tab_news, tab_officers = st.tabs(["About", "News", "Officers"])

    with tab_about:
        about_text = getattr(stock_obj, "company_summary", None) or "No company summary available."
        st.markdown("#### About")
        st.markdown(f"<div style='opacity:.95; line-height:1.6;'>{about_text}</div>", unsafe_allow_html=True)

    with tab_news:
        st.markdown("#### News")
        items_html = _news_items_html(stock_obj)
        st.markdown(items_html, unsafe_allow_html=True)

    with tab_officers:
        st.markdown("#### Officers")
        officers = getattr(stock_obj, "officers", None) or getattr(stock_obj, "company_officers", None)
        if isinstance(officers, list) and officers:
            for off in officers:
                if isinstance(off, dict):
                    name = off.get("name") or "—"
                    title = off.get("title") or off.get("position") or ""
                elif isinstance(off, (list, tuple)):
                    name = off[0] if len(off) > 0 else "—"
                    title = off[1] if len(off) > 1 else ""
                else:
                    continue
                st.markdown(f"- **{name}** — {title}")
        else:
            st.caption("No officer information available.")


# =============================================================================
# Evaluation Checklist - Using st.dataframe
# =============================================================================
def render_evaluation_checklist_card(evaluation_payload: Dict[str, Any], criterion_meta: Dict[str, Any]) -> None:
    tab_past, tab_present, tab_future, tab_health, tab_dividend, tab_macro = st.tabs(
        ["Past", "Present", "Future", "Health", "Dividend", "Macro"]
    )

    def _render_category_table(category_key: str) -> None:
        category_results_map: Dict[str, Dict[str, Any]] = evaluation_payload.get(category_key, {}) or {}
        category_meta_map: Dict[str, Any] = criterion_meta.get(category_key, {}) or {}

        ordered_signal_keys: List[str] = [k for k in category_meta_map.keys() if k in category_results_map]
        ordered_signal_keys = ordered_signal_keys[:6]

        if ordered_signal_keys:
            df_rows = []
            for signal_key in ordered_signal_keys:
                meta_for_signal: Dict[str, Any] = category_meta_map.get(signal_key, {}) if isinstance(category_meta_map,
                                                                                                      dict) else {}
                fancy_name: str = meta_for_signal.get("fancy_name", signal_key)
                check_value = category_results_map.get(signal_key, {}).get("check", 0.0)
                is_passed_boolean = (isinstance(check_value, (int, float)) and float(check_value) >= 0.5)
                pass_fail_emoji = "✅" if is_passed_boolean else "❌"

                df_rows.append({
                    "Criterion": fancy_name,
                    "Result": pass_fail_emoji
                })

            df = pd.DataFrame(df_rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Criterion": st.column_config.TextColumn("Criterion", width="large"),
                    "Result": st.column_config.TextColumn("Pass/Fail", width="small"),
                }
            )
        else:
            st.caption("No evaluation criteria available.")

    with tab_past:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("past")
    with tab_present:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("present")
    with tab_future:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("future")
    with tab_health:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("health")
    with tab_dividend:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("dividend")
    with tab_macro:
        st.markdown("#### Evaluation Checklist")
        _render_category_table("macroeconomics")


# =============================================================================
# Fact Sheet Data Preparation
# =============================================================================
def prepare_fact_sheet_data(stock_obj: Stock) -> Dict[str, Any]:
    """Collect and structure all mappings for fact sheet."""
    try:
        complete_payload_dictionary: Dict[str, Any] = stock_obj.to_payload() if hasattr(stock_obj, "to_payload") else {}
    except Exception:
        complete_payload_dictionary = {}

    basic_information_mapping: Dict[str, Any] = complete_payload_dictionary.get("basic_information", {}) if isinstance(
        complete_payload_dictionary, dict) else {}
    financial_points_mapping: Dict[str, Dict[str, Any]] = complete_payload_dictionary.get("financial_points",
                                                                                          {}) if isinstance(
        complete_payload_dictionary, dict) else {}
    derived_metrics_mapping: Dict[str, Any] = complete_payload_dictionary.get("derived_metrics", {}) if isinstance(
        complete_payload_dictionary, dict) else {}

    basic_info_name_map: Dict[str, str] = {entry["alias"]: entry.get("fancy_name", entry["alias"]) for entry in
                                           STOCK_INFO}
    financial_points_name_map: Dict[str, str] = {alias: meta.get("fancy_name", alias) for alias, meta in
                                                 FINANCIALS.items()}
    derived_name_map: Dict[str, str] = {var: meta.get("fancy_name", var) for var, meta in DERIVED_METRICS.items()}

    derived_series_mapping: Dict[str, Dict[str, Any]] = {}
    derived_scalar_mapping: Dict[str, Any] = {}
    if isinstance(derived_metrics_mapping, dict):
        for metric_key, metric_value in derived_metrics_mapping.items():
            if isinstance(metric_value, dict):
                derived_series_mapping[metric_key] = metric_value
            else:
                derived_scalar_mapping[metric_key] = metric_value

    return dict(
        basic_information_mapping=basic_information_mapping,
        financial_points_mapping=financial_points_mapping,
        derived_series_mapping=derived_series_mapping,
        derived_scalar_mapping=derived_scalar_mapping,
        basic_info_name_map=basic_info_name_map,
        financial_points_name_map=financial_points_name_map,
        derived_name_map=derived_name_map,
    )


def _fmt_scalar_value_for_display(value_any: Any) -> str:
    if value_any is None:
        return "—"
    if isinstance(value_any, (int, float)):
        if not np.isfinite(value_any):
            return "—"
        return format_compact_number(value_any)
    return str(value_any)


# =============================================================================
# Details Tab Renderers
# =============================================================================
def render_details_scalars(data: Dict[str, Any]) -> None:
    """Render scalar fact sheets using st.dataframe."""
    st.markdown("### 📊 Basic & Derived Metrics")
    st.markdown("Key financial metrics and ratios that provide a snapshot of the company's current state.")

    tab_original, tab_derived = st.tabs(["Original Metrics", "Derived Metrics"])

    with tab_original:
        st.markdown("#### Basic Information")
        st.caption("Core company metrics extracted from financial statements")
        mapping = data["basic_information_mapping"]
        name_map = data["basic_info_name_map"]

        if mapping:
            df_rows = []
            for metric_name, value in mapping.items():
                if metric_name == "company_summary":
                    continue
                display_name = name_map.get(metric_name, metric_name)
                df_rows.append({
                    "Metric": display_name,
                    "Value": _fmt_scalar_value_for_display(value)
                })

            if df_rows:
                df = pd.DataFrame(df_rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Metric": st.column_config.TextColumn("Metric", width="medium"),
                        "Value": st.column_config.TextColumn("Value", width="medium"),
                    }
                )
        else:
            st.caption("No basic information available.")

    with tab_derived:
        st.markdown("#### Derived Scalars")
        st.caption("Calculated metrics based on fundamental data")
        mapping = data["derived_scalar_mapping"]
        name_map = {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()}

        if mapping:
            df_rows = []
            for metric_name, value in mapping.items():
                display_name = name_map.get(metric_name, metric_name)
                df_rows.append({
                    "Metric": display_name,
                    "Value": _fmt_scalar_value_for_display(value)
                })

            if df_rows:
                df = pd.DataFrame(df_rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Metric": st.column_config.TextColumn("Metric", width="medium"),
                        "Value": st.column_config.TextColumn("Value", width="medium"),
                    }
                )
        else:
            st.caption("No derived scalars available.")


def render_details_series(data: Dict[str, Any]) -> None:
    """Render series fact sheets using st.dataframe."""
    st.markdown("### 📈 Time Series Data")
    st.markdown("Historical trends showing how key metrics have evolved over time (latest 5 periods).")

    tab_original, tab_derived = st.tabs(["Original Series", "Derived Series"])

    def _render_series_dataframe(mapping: Dict[str, Dict[str, Any]], name_map: Dict[str, str], title: str,
                                 caption: str):
        st.markdown(f"#### {title}")
        st.caption(caption)

        if not mapping:
            st.caption("No time-series data available.")
            return

        all_timestamps = set()
        for series_map in mapping.values():
            all_timestamps.update(str(k) for k in (series_map or {}).keys())

        timestamps_sorted = sorted(all_timestamps, reverse=True)[:5]

        if not timestamps_sorted:
            st.caption("No time-series data available.")
            return

        df_data = {"Metric": []}
        for ts in timestamps_sorted:
            df_data[ts] = []

        for metric_key in name_map.keys():
            if metric_key not in mapping:
                continue

            display_name = name_map.get(metric_key, metric_key)
            df_data["Metric"].append(display_name)

            series_map = mapping.get(metric_key, {}) or {}
            for ts in timestamps_sorted:
                val = series_map.get(ts)
                try:
                    f = float(val)
                    txt = format_compact_number(f) if np.isfinite(f) else "—"
                except Exception:
                    txt = "—"
                df_data[ts].append(txt)

        if df_data["Metric"]:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption('"—" indicates no data for that period.')
        else:
            st.caption("No time-series data available.")

    with tab_original:
        _render_series_dataframe(
            data["financial_points_mapping"],
            data["financial_points_name_map"],
            "Financial Points",
            "Raw financial data from statements over time"
        )

    with tab_derived:
        _render_series_dataframe(
            data["derived_series_mapping"],
            {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
            "Derived Series",
            "Calculated metrics showing historical trends"
        )


def render_details_valuation(fair_value_payload: Dict[str, Any]) -> None:
    """Render valuation methods with educational content."""
    st.markdown("### 💰 Valuation Methods")
    st.markdown("""
    Different valuation approaches provide multiple perspectives on fair value. Each method has strengths and limitations 
    depending on the company's characteristics and industry dynamics.
    """)

    method_order = [
        ("price_earning_multiples", "PE Multiple Method"),
        ("discounted_cash_flow_one_stage", "DCF One-Stage"),
        ("discounted_cash_flow_two_stage", "DCF Two-Stage"),
        ("discounted_dividend_two_stage", "Dividend Discount Model"),
        ("return_on_equity", "ROE Capitalization"),
        ("excess_return", "Residual Income Model"),
        ("graham_number", "Graham Number"),
    ]

    for method_key, display_name in method_order:
        method_data = fair_value_payload.get(method_key, {})
        if not isinstance(method_data, dict):
            continue

        fancy_name = method_data.get("fancy_name", display_name)
        description = method_data.get("description", "")
        inputs_list = method_data.get("inputs", [])
        outputs = method_data.get("outputs", {})
        feasibility = method_data.get("feasibility", "")
        formula = method_data.get("formula", "")

        fair_value = outputs.get("Fair Value", np.nan)

        with st.expander(f"**{fancy_name}** — Fair Value: {format_compact_number(fair_value)}"):
            if description:
                st.markdown("**Overview**")
                st.write(description)

            if inputs_list:
                st.markdown("**Key Inputs**")
                for inp in inputs_list:
                    st.markdown(f"- {inp}")

            if outputs:
                st.markdown("**Outputs**")
                for key, val in outputs.items():
                    st.metric(key, format_compact_number(val))

            if feasibility:
                st.markdown("**Feasibility & Limitations**")
                st.info(feasibility)

            # if formula:
            #     st.markdown("**Formula**")
            #     # Fix LaTeX escaping: replace single backslashes with double backslashes
            #     formula_escaped = formula.replace('\\', '\\\\')
            #     st.latex(formula_escaped)


def render_details_evaluation(evaluation_payload: Dict[str, Any]) -> None:
    """Render evaluation criteria with educational content."""
    st.markdown("### ✅ Investment Criteria Evaluation")
    st.markdown("""
    A systematic evaluation across six dimensions: historical performance (Past), current fundamentals (Present), 
    growth momentum (Future), financial health (Health), dividend quality (Dividend), and macroeconomic context (Macroeconomics).
    """)

    categories = [
        ("past", "📜 Past Performance", "Historical trends in key financial metrics"),
        ("present", "🎯 Present Fundamentals", "Current financial strength and valuation"),
        ("future", "🚀 Future Momentum", "Growth trajectory and forward indicators"),
        ("health", "💪 Financial Health", "Balance sheet strength and risk metrics"),
        ("dividend", "💵 Dividend Quality", "Dividend sustainability and track record"),
        ("macroeconomics", "🌍 Macroeconomic Context", "Broader economic environment"),
    ]

    for category_key, category_title, category_desc in categories:
        category_data = evaluation_payload.get(category_key, {})
        if not isinstance(category_data, dict) or not category_data:
            continue

        st.markdown(f"#### {category_title}")
        st.caption(category_desc)

        for signal_key, result in category_data.items():
            if not isinstance(result, dict):
                continue

            # Get metadata from CRITERION
            meta = CRITERION.get(category_key, {}).get(signal_key, {}) if isinstance(CRITERION.get(category_key, {}),
                                                                                     dict) else {}

            fancy_name = meta.get("fancy_name", signal_key)
            description = meta.get("description", "")
            criteria = meta.get("criteria", "")
            input_info = meta.get("input", "")
            method_info = meta.get("method", "")

            check_value = result.get("check", 0.0)
            passed = isinstance(check_value, (int, float)) and float(check_value) >= 0.5
            outputs = result.get("outputs", {})

            status_icon = "✅" if passed else "❌"
            status_text = "PASS" if passed else "FAIL"

            with st.expander(f"{status_icon} **{fancy_name}** — {status_text}"):
                if description:
                    st.markdown("**What This Measures**")
                    st.write(description)

                if criteria:
                    st.markdown("**Criteria**")
                    st.code(criteria, language=None)

                if outputs:
                    st.markdown("**Results**")
                    cols = st.columns(len(outputs))
                    for idx, (key, val) in enumerate(outputs.items()):
                        with cols[idx]:
                            if isinstance(val, bool):
                                st.metric(key, "Yes" if val else "No")
                            elif isinstance(val, (int, float)):
                                st.metric(key, format_compact_number(val))
                            else:
                                st.metric(key, str(val))

                if input_info or method_info:
                    st.markdown("**Methodology**")
                    if input_info:
                        st.markdown(f"*Input:* {input_info}")
                    if method_info:
                        st.markdown(f"*Method:* {method_info}")


# =============================================================================
# Sidebar
# =============================================================================
def render_left_panel() -> Tuple[str, Dict[str, Any], bool, bool]:
    with st.sidebar:
        st.markdown("### Ticker & Parameters")
        ticker_symbol_input: str = st.text_input(
            "Ticker Symbol",
            key="ticker_input",
            help=(
                "Type a ticker (e.g., AAPL, MSFT) and press Run. "
                "For non-US stocks, use Yahoo Finance format (e.g., 9697.T for Japan, 0700.HK for Hong Kong)."
            ),
        )

        with st.expander("Valuation Parameters (Optional)", expanded=False):
            st.caption(
                "Parameters will be calculated automatically. Adjust them afterward to see different valuations.")
            st.number_input("Discount Rate", key="discount_rate", step=0.005, format="%.3f")
            st.number_input("Growth Rate", key="growth_rate", step=0.005, format="%.3f")
            st.number_input("Growth Decline Rate (per year)", key="decline_rate", step=0.005, format="%.3f")
            st.number_input("Terminal Growth Rate", key="terminal_growth_rate", step=0.005, format="%.3f")
            st.number_input("Margin of Safety", key="margin_of_safety", step=0.05, format="%.2f")
            st.number_input("Projection Years (Stage 1)", key="n_years1", min_value=1)
            st.number_input("Projection Years (Stage 2)", key="n_years2", min_value=0)
            st.number_input("Risk-Free Rate", key="risk_free_rate", step=0.005, format="%.3f")
            st.number_input("Average Market Return", key="average_market_return", step=0.005, format="%.3f")

        run_button_pressed = st.button(
            "Run",
            type="primary",
            use_container_width=True,
            on_click=_on_run_clicked_reset_urls_if_ticker_changed,
        )

        insert_vertical_row_spacing(8)

        with st.expander("Fiscal Report URLs (Optional)", expanded=False):
            st.caption("Add URLs to online reports. They'll be included in the generated prompt.")
            st.text_input("10-K", key="url_10k", help="Annual report URL")
            st.text_input("10-Q", key="url_10q", help="Quarterly report URL")
            st.text_input("Extra", key="url_extra", help="Additional document URL")

        generate_prompt_pressed = st.button(
            "Generate Prompt",
            type="secondary",
            use_container_width=True,
            disabled=not st.session_state.get("has_run", False),
        )

        override_params = {
            "discount_rate": st.session_state["discount_rate"],
            "growth_rate": st.session_state["growth_rate"],
            "decline_rate": st.session_state["decline_rate"],
            "terminal_growth_rate": st.session_state["terminal_growth_rate"],
            "margin_of_safety": st.session_state["margin_of_safety"],
            "n_years1": int(st.session_state["n_years1"]),
            "n_years2": int(st.session_state["n_years2"]),
            "risk_free_rate": st.session_state["risk_free_rate"],
            "average_market_return": st.session_state["average_market_return"],
        }
        return ticker_symbol_input.strip().upper(), override_params, run_button_pressed, generate_prompt_pressed


# =============================================================================
# Prompt Generation
# =============================================================================
def _format_key_value_lines(name_map: Dict[str, str], data_map: Dict[str, Any]) -> str:
    lines: List[str] = []
    for key in name_map.keys():
        if key == "company_summary":
            continue
        if key in data_map:
            val = data_map.get(key)
            if isinstance(val, (int, float)):
                if np.isfinite(val):
                    lines.append(f"{name_map.get(key, key)}: {format_compact_number(val)}")
                else:
                    lines.append(f"{name_map.get(key, key)}: —")
            else:
                lines.append(f"{name_map.get(key, key)}: {val if (val is not None and val != '') else '—'}")
    return "\n".join(lines)


def _format_key_ratios_lines(key_ratios_payload: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for item in key_ratios_payload or []:
        fancy = item.get("fancy_name", item.get("key", "Metric"))
        fmt_kind = item.get("format", "raw")
        val = item.get("value", None)
        if fmt_kind == "ratio":
            txt = fmt_ratio(val)
        elif fmt_kind == "money":
            txt = format_compact_number(val)
        else:
            try:
                txt = format_compact_number(float(val))
            except Exception:
                txt = "—" if val is None else str(val)
        lines.append(f"{fancy}: {txt}")
    return "\n".join(lines)


def _format_fair_values_lines(fair_values: Dict[str, Any], current_price: Optional[float]) -> str:
    method_display_map = {
        "price_earning_multiples": "PE Multiple",
        "discounted_cash_flow_one_stage": "1-Stage Discounted Cashflow",
        "discounted_cash_flow_two_stage": "2-Stage Discounted Cashflow",
        "discounted_dividend_two_stage": "2-Stage Discounted Dividend",
        "return_on_equity": "Return on Equity",
        "excess_return": "Excess Return",
        "graham_number": "Graham Number",
    }
    rows: List[Tuple[str, float, Optional[float]]] = []
    for method_key, payload in (fair_values or {}).items():
        outputs = (payload or {}).get("outputs", {}) or {}
        fv = outputs.get("Fair Value", None)
        if isinstance(fv, (int, float)) and np.isfinite(fv):
            upside = None
            if isinstance(current_price, (int, float)) and np.isfinite(current_price) and current_price > 0:
                upside = fv / current_price - 1.0
            rows.append((method_display_map.get(method_key, method_key), float(fv), upside))

    if isinstance(current_price, (int, float)) and np.isfinite(current_price) and current_price > 0:
        rows.sort(key=lambda r: (r[1] / current_price), reverse=True)
    else:
        rows.sort(key=lambda r: r[1], reverse=True)

    lines: List[str] = []
    if isinstance(current_price, (int, float)) and np.isfinite(current_price):
        lines.append(f"Current Price: {format_compact_number(current_price)}")
    for method_name, fv, up in rows:
        if up is None:
            lines.append(f"{method_name}: {format_compact_number(fv)}")
        else:
            lines.append(f"{method_name}: {format_compact_number(fv)}  (Upside: {up:.0%})")
    return "\n".join(lines)


def _format_series_table_lines(series_map: Dict[str, Dict[str, Any]], name_map: Dict[str, str]) -> str:
    all_ts = set()
    for v in (series_map or {}).values():
        all_ts.update(str(k) for k in (v or {}).keys())
    ts_sorted_desc = sorted(all_ts, reverse=True)[:5]

    lines: List[str] = []
    for metric_key in name_map.keys():
        if metric_key not in series_map:
            continue
        display = name_map.get(metric_key, metric_key)
        lines.append(f"- {display}:")
        per_ts = series_map.get(metric_key, {}) or {}
        for ts in ts_sorted_desc:
            val = per_ts.get(ts, None)
            try:
                f = float(val)
                txt = format_compact_number(f) if np.isfinite(f) else "—"
            except Exception:
                txt = "—"
            lines.append(f"    {ts}: {txt}")
    return "\n".join(lines)


def _format_officers_lines(officers: Optional[List[Any]]) -> str:
    if not isinstance(officers, list) or not officers:
        return "No officer information available."
    lines: List[str] = []
    for off in officers:
        if isinstance(off, dict):
            name = off.get("name") or "—"
            title = off.get("title") or off.get("position") or ""
        elif isinstance(off, (list, tuple)):
            name = off[0] if len(off) > 0 else "—"
            title = off[1] if len(off) > 1 else ""
        else:
            continue
        if title:
            lines.append(f"{name} — {title}")
        else:
            lines.append(f"{name}")
    return "\n".join(lines)


def _format_evaluation_lines(evaluation_payload: Dict[str, Any]) -> str:
    def fmt_val(v: Any) -> str:
        if isinstance(v, (int, float)):
            if np.isfinite(v):
                return format_compact_number(v)
            return "—"
        return "—" if v is None else str(v)

    lines: List[str] = []
    for group_key in ["past", "present", "future", "health", "dividend", "macroeconomics"]:
        group = evaluation_payload.get(group_key, {}) or {}
        if not group:
            continue
        lines.append(f"{group_key.capitalize()}:")
        for signal_key, result in group.items():
            meta = CRITERION.get(group_key, {}).get(signal_key, {}) if isinstance(CRITERION.get(group_key, {}),
                                                                                  dict) else {}
            fancy = meta.get("fancy_name", signal_key)
            check_val = result.get("check", 0.0)
            passed = (isinstance(check_val, (int, float)) and float(check_val) >= 0.5)
            emoji = "✅" if passed else "❌"
            lines.append(f"- {fancy}: {emoji}")
            outputs = result.get("outputs", {}) or {}
            for k, v in outputs.items():
                lines.append(f"    {k}: {fmt_val(v)}")
    return "\n".join(lines) if lines else "No evaluation data."


def _prune_default_urls(urls: Dict[str, str]) -> Dict[str, str]:
    defaults = {
        "10-K": "https://example.com/10k.pdf",
        "10-Q": "https://example.com/10q.pdf",
        "Extra": "https://example.com/extra",
    }
    out: Dict[str, str] = {}
    for k, v in urls.items():
        v_str = (v or "").strip()
        if not v_str:
            continue
        if defaults.get(k) and v_str == defaults[k]:
            continue
        out[k] = v_str
    return out


def collect_prompt_text(
        stock_obj: Stock,
        prepared_fact_data: Dict[str, Any],
        evaluation_payload: Dict[str, Any],
        fair_values: Dict[str, Any],
        key_ratios_payload: Optional[List[Dict[str, Any]]] = None,
        url_map: Optional[Dict[str, str]] = None,
) -> str:
    """Build the final plain-text prompt."""
    company_summary_text: str = getattr(stock_obj, "company_summary", "") or ""

    basic_info_lines = _format_key_value_lines(
        prepared_fact_data["basic_info_name_map"],
        prepared_fact_data["basic_information_mapping"],
    )

    derived_scalar_lines = _format_key_value_lines(
        {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
        prepared_fact_data["derived_scalar_mapping"],
    )

    if not key_ratios_payload:
        key_ratios_payload = build_key_ratios_from_config(stock_obj)
    key_ratios_lines = _format_key_ratios_lines(key_ratios_payload)

    current_price_val = getattr(stock_obj, "current_price", None)
    fair_values_lines = _format_fair_values_lines(fair_values, current_price_val)

    series_original_lines = _format_series_table_lines(
        prepared_fact_data["financial_points_mapping"],
        prepared_fact_data["financial_points_name_map"],
    )
    series_derived_lines = _format_series_table_lines(
        prepared_fact_data["derived_series_mapping"],
        {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
    )

    officers_lines = _format_officers_lines(
        getattr(stock_obj, "officers", None) or getattr(stock_obj, "company_officers", None)
    )

    evaluation_lines = _format_evaluation_lines(evaluation_payload)

    url_map = url_map or {}
    pruned = _prune_default_urls(url_map)
    if pruned:
        url_lines = []
        if "10-K" in pruned: url_lines.append(f"10-K: {pruned['10-K']}")
        if "10-Q" in pruned: url_lines.append(f"10-Q: {pruned['10-Q']}")
        if "Extra" in pruned: url_lines.append(f"Extra: {pruned['Extra']}")
        urls_block = "\n".join(url_lines)
    else:
        urls_block = "(none provided)"

    sections: List[str] = []
    sections.append("Company Summary:\n" + (company_summary_text.strip() or "(no summary)"))
    sections.append("Stock basic information:\n" + (basic_info_lines.strip() or "—"))
    sections.append("Stock key ratios:\n" + (key_ratios_lines.strip() or "—"))
    sections.append("Stock Fair values:\n" + (fair_values_lines.strip() or "—"))

    fp_blocks: List[str] = []
    fp_blocks.append("(Derived Series - latest 5):\n" + (series_derived_lines.strip() or "—"))
    sections.append("Stock financial points\n" + "\n".join(fp_blocks))

    sections.append("Company Officer:\n" + (officers_lines.strip() or "—"))
    sections.append("Evaluation:\n" + (evaluation_lines.strip() or "—"))
    sections.append("Online document URLs:\n" + (urls_block.strip() if urls_block else "(none provided)"))

    final_text = "\n\n".join(sections)
    final_text = PROMPT_TEMPLATE + "\n\n" + final_text
    return final_text


# =============================================================================
# Main
# =============================================================================
def main() -> None:
    st.session_state.setdefault("stock", None)
    st.session_state.setdefault("evaluation_payload", None)
    st.session_state.setdefault("fair_value_payload", None)
    st.session_state.setdefault("last_ticker", None)
    st.session_state.setdefault("generated_prompt_text", "")

    ensure_default_param_keys()

    ticker_symbol, override_params, run_pressed, gen_prompt_pressed = render_left_panel()

    ticker_changed = (st.session_state.last_ticker != ticker_symbol)

    if run_pressed:
        try:
            if (st.session_state.stock is None) or ticker_changed:
                with st.spinner("Fetching stock & building evaluation..."):
                    stock = fetch_stock(ticker_symbol)
                    st.session_state.stock = stock

                    evaluation_payload = run_evaluation_only()
                    val = Valuation(stock)
                    val_params = val.get_valuation_params()

                    params_to_update = {}

                    for param_key in ["discount_rate", "growth_rate", "decline_rate",
                                      "terminal_growth_rate", "margin_of_safety", "n_years1",
                                      "n_years2", "risk_free_rate", "average_market_return"]:

                        current_value = st.session_state.get(param_key)
                        default_value = DEFAULT_PARAM_DICT.get(param_key)
                        calculated_value = val_params.get(param_key)

                        user_modified = (current_value != default_value)

                        if user_modified:
                            st.session_state["user_modified_params"].add(param_key)
                            override_params[param_key] = current_value
                        elif calculated_value is not None:
                            if param_key in ["n_years1", "n_years2"]:
                                calculated_value = int(calculated_value)
                            else:
                                calculated_value = float(calculated_value)

                            params_to_update[param_key] = calculated_value
                            override_params[param_key] = calculated_value
                        else:
                            override_params[param_key] = current_value

                    if params_to_update:
                        st.session_state["_pending_params"] = params_to_update
                        st.session_state["_apply_pending_params"] = True

                    st.session_state.evaluation_payload = evaluation_payload
                    st.session_state.last_ticker = ticker_symbol
                    st.session_state["_show_prompt_success"] = False

            else:
                for param_key in ["discount_rate", "growth_rate", "decline_rate",
                                  "terminal_growth_rate", "margin_of_safety", "n_years1",
                                  "n_years2", "risk_free_rate", "average_market_return"]:
                    override_params[param_key] = st.session_state.get(param_key)

            with st.spinner("Computing valuations..."):
                st.session_state.fair_value_payload = run_valuation_only(st.session_state.stock, override_params)

            st.session_state["_top_error"] = ""
            st.session_state.has_run = True
            st.rerun()

        except ValueError as e:
            st.session_state["_top_error"] = str(e)
            st.toast(str(e), icon="⚠️")
            st.session_state.has_run = False
            st.session_state.stock = None
            st.session_state.fair_value_payload = None
            st.session_state["_show_prompt_success"] = False

        except Exception as e:
            msg = f"Failed to fetch or compute for '{ticker_symbol}'. Please try again. Details: {e}"
            st.session_state["_top_error"] = msg
            st.toast(msg, icon="❌")
            st.session_state.has_run = False
            st.session_state.stock = None
            st.session_state.fair_value_payload = None
            st.session_state["_show_prompt_success"] = False

    st.title("Value Investing Dashboard")

    if st.session_state.get("_show_prompt_success"):
        st.success("Prompt generated. Open the **Prompts** tab to copy it.")

    insert_vertical_row_spacing(6)

    _top_error = st.session_state.get("_top_error", "")
    if _top_error:
        st.error(_top_error)
        insert_vertical_row_spacing(8)

    if st.session_state.stock is None or st.session_state.fair_value_payload is None:
        st.info("Enter a ticker and click **Run** to load data.")
        return

    stock_obj = st.session_state.stock
    try:
        payload: Dict[str, Any] = stock_obj.to_payload()
    except Exception:
        payload = {}

    company_name_string = getattr(stock_obj, "name", None)
    sector_string = getattr(stock_obj, "sector", "") or ""
    industry_string = getattr(stock_obj, "industry", "") or ""
    country_string = getattr(stock_obj, "country", "") or ""
    chips_html = "".join(
        f'<span class="chip">{t}</span>' for t in [sector_string, industry_string, country_string] if t)

    st.markdown(
        textwrap_dedent(f"""
            <div class="company-header">
              <span class="company-name">{company_name_string}</span>
              {chips_html}
            </div>
            """).strip(),
        unsafe_allow_html=True,
    )

    # Three tabs: Overview, Details (renamed from Fact Sheet), Prompts
    tab_overview, tab_details, tab_prompts = st.tabs(["Overview", "Details", "Prompts"])

    fair_values = st.session_state.fair_value_payload
    evaluation_payload = st.session_state.evaluation_payload or {}

    if gen_prompt_pressed:
        try:
            prepared_fact_data = prepare_fact_sheet_data(stock_obj)
            key_ratios_payload = (payload or {}).get("key_ratios", []) or build_key_ratios_from_config(stock_obj)
            url_map_for_prompt = {
                "10-K": st.session_state.get("url_10k", ""),
                "10-Q": st.session_state.get("url_10q", ""),
                "Extra": st.session_state.get("url_extra", ""),
            }

            prompt_text_built = collect_prompt_text(
                stock_obj=stock_obj,
                prepared_fact_data=prepared_fact_data,
                evaluation_payload=evaluation_payload,
                fair_values=fair_values,
                key_ratios_payload=key_ratios_payload,
                url_map=url_map_for_prompt,
            )

            st.session_state["generated_prompt_text"] = prompt_text_built
            st.session_state["_show_prompt_success"] = True

        except Exception as e:
            st.session_state["_show_prompt_success"] = False
            st.error(f"Failed to generate prompt. Details: {e}")

    with tab_overview:
        col_price_chart, col_radar_chart, col_checklist = st.columns([0.4, 0.3, 0.3], gap="large")

        with col_price_chart:
            st.markdown("#### Price in 10 years")
            price_df = getattr(stock_obj, "prices", None)
            try:
                if hasattr(stock_obj, "get_prices_series"):
                    price_df = stock_obj.get_prices_series()
            except Exception:
                pass
            if isinstance(price_df, pd.DataFrame) and "Close" in price_df.columns and not price_df.empty:
                chart = build_price_line_chart(price_df.tail(3650 + 30), height=300,
                                               margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.caption("No price data available.")

        with col_radar_chart:
            st.markdown("#### Evaluation Snowflakes")
            category_scores = compute_category_scores_for_radar(evaluation_payload)
            radar_labels = ["past", "present", "future", "health", "dividend", "macroeconomics"]
            radar_values = [category_scores.get(k, 0.0) for k in radar_labels]
            radar_fig = build_radar_chart(radar_labels, radar_values, height=300, edge_pad=0.10,
                                          margin=dict(l=10, r=10, t=10))
            st.plotly_chart(radar_fig, use_container_width=True)

        with col_checklist:
            render_evaluation_checklist_card(evaluation_payload, CRITERION)

        insert_vertical_row_spacing(30)

        colC, colD, colE = st.columns([0.20, 0.30, 0.5], gap="large")
        with colC:
            key_ratios_payload = (payload or {}).get("key_ratios", [])
            if not key_ratios_payload:
                key_ratios_payload = build_key_ratios_from_config(stock_obj)
            render_key_ratios_card(key_ratios_payload)

        with colD:
            current_price = getattr(stock_obj, "current_price", np.nan) or np.nan
            render_fair_value_table_card(current_price, fair_values)

        with colE:
            render_about_news_officers_tabbed(stock_obj)

    with tab_details:
        # Prepare fact sheet data once
        prepared_fact_data = prepare_fact_sheet_data(stock_obj)

        # Section 1: Scalars and Series
        render_details_scalars(prepared_fact_data)
        st.markdown("---")

        render_details_series(prepared_fact_data)
        st.markdown("---")

        # Section 2: Valuation Methods
        render_details_valuation(fair_values)
        st.markdown("---")

        # Section 3: Evaluation Criteria
        render_details_evaluation(evaluation_payload)

    with tab_prompts:
        st.subheader("Prompt")
        st.caption(
            "Copy and paste the Prompt to your AI to generate the final report. Enable reasoning and web search. Gemini 2.5 Pro is highly recommended.")
        if st.session_state.get("generated_prompt_text"):
            st.code(st.session_state["generated_prompt_text"], language=None)
        else:
            st.info("No prompt yet. Use the **Generate Prompt** button in the sidebar under **Fiscal Report URLs**.")


if __name__ == "__main__":
    main()