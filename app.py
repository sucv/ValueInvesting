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
    # key-ratio config
)
from utils.prompt_templates import PROMPT_TEMPLATE
from core.macros import MacroEconomic
from core.evaluation import Evaluator
from core.stock import Stock
from utils.app import format_compact_number, fmt_ratio, get_latest
from configs import macro_cfg

# =============================================================================
# Page config
# =============================================================================
st.set_page_config(page_title="Value Investing Dashboard", page_icon="📈", layout="wide")

# =============================================================================
# Global CSS — theme + tooltip + secondary button + responsiveness
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
        --tooltip-bg: #0f1a30;
        --tooltip-border: rgba(255,255,255,0.12);

        /* Secondary button palette to match theme */
        --btn-secondary-bg: #2A3553;
        --btn-secondary-bg-hover: #324266;
        --btn-secondary-border: rgba(255,255,255,0.14);
        --btn-secondary-text: #E6EEF7;

        /* Tooltip text controls */
        --tooltip-font-size: 0.95rem;
        --tooltip-line-height: 1.55;
      }

      /* Ensure overlays can float above siblings across the page */
      .block-container { padding-top: 1.2rem; overflow: visible; }
      [data-baseweb="tab-panel"] { overflow: visible; } /* Streamlit Tabs pane */
      .stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); }
      .stTabs [aria-selected="true"] { color: var(--text); border-bottom: 2px solid var(--accent); }
      h1,h2,h3,h4 { color: var(--text); letter-spacing: 0.1px; }

      .app-card{
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
        position: relative;   /* needed so z-index applies */
        z-index: 0;           /* default layering */
        overflow: visible;    /* let tooltip overflow this card */
      }
      /* Raise hovered card so its tooltip can overlay neighboring cards */
      .app-card:hover { z-index: 100; }

      .app-card h3, .app-card h4{ margin: 0 0 6px 0; }
      .keyline{ height:1px; background: rgba(255,255,255,0.10); margin:10px 0; }
      .kv{ display:flex; align-items:baseline; gap:8px; margin:6px 0;}
      .kv .k{ color: var(--muted); min-width:160px; font-size:0.92rem;}
      .kv .v{ color: var(--text); font-weight:600; font-size:1.05rem;}
      .chip{
        display:inline-block; padding:3px 10px; border-radius:999px;
        border:1px solid var(--border); font-size:0.82rem; color: var(--muted);
        margin-right:6px; margin-bottom:6px; background: rgba(255,255,255,0.02);
      }
      .streamlit-expanderHeader { font-weight:600; }

      .masonry { column-count: 3; column-gap: 18px; overflow: visible; }
      @media (max-width: 1200px) { .masonry { column-count: 2; } }
      @media (max-width: 700px)  { .masonry { column-count: 1; } }
      .masonry .app-card {
        display: inline-block;
        width: 100%;
        break-inside: avoid;
        margin: 0 0 18px;
      }

      .company-header {
        display:flex; align-items:center; gap:10px; flex-wrap:wrap;
        margin:-6px 0 8px 0;
      }
      .company-name { font-weight:700; font-size:1.2rem; color:var(--text); }

      .row-spacer { height: 18px; }

      /* ============ Card grids ============ */
      .card-grid{
        display:grid;
        grid-template-columns: repeat(3, minmax(0,1fr));
        gap:18px;
        position: relative;
        overflow: visible; /* allow children to overflow visibly */
      }
      @media (max-width: 1100px){
        .card-grid{
          grid-template-columns: repeat(2, minmax(0,1fr));
        }
      }
      @media (max-width: 700px){
        .card-grid{
          grid-template-columns: 1fr;
        }
      }

      /* ============ Table wrappers ============ */
      .table-wrap{
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
      /* by default, allow wrapping; numbers will be right-aligned inline */
      .table-wrap table{
        width: 100%;
        border-collapse: collapse;
      }
      .table-wrap th, .table-wrap td{
        overflow-wrap: anywhere;
        word-break: normal;
        white-space: normal; /* allow text to wrap */
      }

      /* Compact tables for Key Ratios / Fair Value / Basic Info */
      .compact-table{
        table-layout: fixed;              /* stable column widths */
        font-size: 0.94rem;
      }
      .compact-table th,
      .compact-table td{
        padding: 6px 8px;                 /* tighter padding */
      }
      .compact-table th:nth-child(1),
      .compact-table td:nth-child(1){
        width: 60%;                        /* name/metric column */
      }
      .compact-table th:nth-child(n+2),
      .compact-table td:nth-child(n+2){
        width: 40%;                        /* values */
        text-align: right;
        white-space: nowrap;               /* keep concise numbers on one line */
      }

      /* ===========================
         Tooltip styles (.help-tip)
         =========================== */

      /* ensure each table row/cell forms a positioning context so children's z-index compete predictably */
      table tr, table td { position: relative; }

      .help-tip{
        position: relative;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        width:18px; height:18px;
        margin-left:6px;
        border-radius:50%;
        border:1px solid var(--border);
        font-size:.78rem; line-height:1;
        color: var(--muted);
        cursor: help;
        user-select:none;
        z-index: 2; /* base above sibling text */
        outline: none;
      }
      .help-tip::before{ content:"?"; }

      /* lift the hovered icon and its parent card so bubble can sit on top of other cards */
      .help-tip:hover { z-index: 10000; }
      .help-tip:focus { z-index: 10000; }

      .help-tip__bubble{
        display:none;
        position:absolute;
        top: 24px;
        left: 50%;
        transform: translateX(-50%);
        min-width: 320px;                 /* wider tooltip */
        max-width: 720px;                 /* allow longer lines before wrapping */
        background: var(--tooltip-bg);
        border: 1px solid var(--tooltip-border);
        border-radius: 10px;
        padding: 10px 12px;
        color: var(--text);
        box-shadow: 0 10px 28px rgba(0,0,0,.45);
        z-index: 10001; /* above hovered icon and any later rows */
        text-align: left;
        white-space: normal;
        overflow-wrap: anywhere;
        pointer-events: auto;
        font-size: var(--tooltip-font-size);
        line-height: var(--tooltip-line-height);
      }
      .help-tip:hover .help-tip__bubble{ display:block; }
      .help-tip:focus .help-tip__bubble,
      .help-tip:focus-within .help-tip__bubble{ display:block; }

      /* Touch-friendly: keep within viewport */
      @media (hover: none){
        .help-tip__bubble{ max-width: 90vw; }
      }
      @media (max-width: 700px){
        .help-tip{ width:24px; height:24px; font-size:.9rem; }
      }

      /* ===========================
         Secondary button styling + tap target
         =========================== */
      .stButton > button[kind="secondary"]{
        background: var(--btn-secondary-bg);
        color: var(--btn-secondary-text);
        border: 1px solid var(--btn-secondary-border);
        min-height: 44px; /* tap target */
      }
      .stButton > button[kind="secondary"]:hover:not(:disabled){
        background: var(--btn-secondary-bg-hover);
        border-color: var(--btn-secondary-border);
      }
      .stButton > button[kind="secondary"]:disabled{
        opacity: .55;
        cursor: not-allowed;
      }
      .stButton > button[kind="primary"]{
        min-height: 44px; /* ensure Run has adequate tap target too */
      }

      /* Wrap long text in News/Officers */
      .app-card details > summary{
        overflow-wrap:anywhere;
        white-space: normal;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Small layout helper
# =============================================================================
def insert_vertical_row_spacing(spacing_height_px: int = 18) -> None:
    st.markdown(
        f"<div class='row-spacer' style='height:{int(spacing_height_px)}px;'></div>",
        unsafe_allow_html=True,
    )

# =============================================================================
# Tooltip helpers
# =============================================================================
def build_help_tip_html(
    bubble_title_text: Optional[str],
    bubble_content_html: str,
) -> str:
    title_html = f"<div class='help-tip__title'>{html_module.escape(bubble_title_text)}</div>" if bubble_title_text else ""
    # NOTE: tabindex + role make it focusable/tappable on mobile; aria-label aids AT
    return (
        "<span class='help-tip' tabindex='0' role='button' aria-label='Show help'>"
        f"<div class='help-tip__bubble'>{title_html}<div class='help-tip__content'>{bubble_content_html}</div></div>"
        "</span>"
    )

def make_html_paragraph_safe(text: Optional[str]) -> str:
    if not text:
        return ""
    return f"<p>{html_module.escape(str(text))}</p>"

# =============================================================================
# Param defaults
# =============================================================================
def ensure_default_param_keys() -> None:
    st.session_state.setdefault("discount_rate", float(DEFAULT_PARAM_DICT["discount_rate"]))
    st.session_state.setdefault("growth_rate", float(DEFAULT_PARAM_DICT["growth_rate"]))
    st.session_state.setdefault("decline_rate", float(DEFAULT_PARAM_DICT["decline_rate"]))
    st.session_state.setdefault("terminal_growth_rate", float(DEFAULT_PARAM_DICT["terminal_growth_rate"]))
    st.session_state.setdefault("margin_of_safety", float(DEFAULT_PARAM_DICT["margin_of_safety"]))
    st.session_state.setdefault("n_years1", int(DEFAULT_PARAM_DICT["n_years1"]))
    st.session_state.setdefault("n_years2", int(DEFAULT_PARAM_DICT["n_years2"]))
    st.session_state.setdefault("risk_free_rate", float(DEFAULT_PARAM_DICT["risk_free_rate"]))
    st.session_state.setdefault("average_market_return", float(DEFAULT_PARAM_DICT["average_market_return"]))
    st.session_state.setdefault("has_run", False)  # track if Run has been clicked for the current ticker

    # Defaults for URL inputs
    st.session_state.setdefault("url_10k", "https://example.com/10k.pdf")
    st.session_state.setdefault("url_10q", "https://example.com/10q.pdf")
    st.session_state.setdefault("url_extra", "https://example.com/extra")

    # Ticker text input state
    st.session_state.setdefault("ticker_input", "AAPL")

    # error banner holder
    st.session_state.setdefault("_show_prompt_success", False)
    st.session_state.setdefault("_top_error", "")

def _on_run_clicked_reset_urls_if_ticker_changed() -> None:
    """Reset 10-K/10-Q/Extra to placeholders if ticker changed before URL inputs render."""
    current_typed_ticker = (st.session_state.get("ticker_input") or "").strip().upper()
    previous_ticker = st.session_state.get("last_ticker")

    # Treat None -> something as a change as well
    if previous_ticker is None or current_typed_ticker != previous_ticker:
        st.session_state["url_10k"] = "https://example.com/10k.pdf"
        st.session_state["url_10q"] = "https://example.com/10q.pdf"
        st.session_state["url_extra"] = "https://example.com/extra"
        # also clear any stale prompt/success flag
        st.session_state["generated_prompt_text"] = ""
        st.session_state["_show_prompt_success"] = False

# =============================================================================
# Fetch & compute
# =============================================================================
@st.cache_resource(show_spinner=False)
def fetch_stock(ticker_symbol: str) -> Stock:
    """Fetch Stock object with basic validation; raise ValueError if no price history."""
    data = yf.Ticker(ticker_symbol)
    prices = yf.download(tickers=[ticker_symbol], interval="1d", period="10y")

    # Validate data
    if not isinstance(prices, pd.DataFrame) or prices.empty or ("Close" not in prices.columns):
        raise ValueError(
            f"No price data returned for '{ticker_symbol}'. "
            "Please double-check the ticker symbol. For non-US listings, use Yahoo Finance’s suffix format, e.g.: "
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
# Charts — Fair value table, price chart, radar
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

    table_rows_html = ""
    for row_dict in rows:
        fv = row_dict["FairValue"]
        if isinstance(current_price_float, (int, float)) and np.isfinite(current_price_float) and current_price_float > 0:
            upside_ratio = fv / current_price_float - 1.0
            if upside_ratio > 0:
                arrow_symbol, color_hex = "▲", "#5FE3B9"
            elif upside_ratio < 0:
                arrow_symbol, color_hex = "▼", "#FF6B6B"
            else:
                arrow_symbol, color_hex = "▬", "rgba(230,238,247,0.7)"
            upside_html = f'<span style="color:{color_hex}; font-weight:600">{arrow_symbol}&nbsp;{upside_ratio:.0%}</span>'
        else:
            upside_html = '<span style="opacity:.8">—</span>'

        table_rows_html += f"""
<tr>
  <td style="padding:6px 8px; border-bottom:1px solid var(--border);">{row_dict['Method']}</td>
  <td style="padding:6px 8px; border-bottom:1px solid var(--border); text-align:right; white-space:nowrap;">{format_compact_number(fv)}</td>
  <td style="padding:6px 8px; border-bottom:1px solid var(--border); text-align:right;">{upside_html}</td>
</tr>
""".strip()

    price_badge_html = ""
    if isinstance(current_price_float, (int, float)) and np.isfinite(current_price_float):
        price_badge_html = f'<div style="font-size:.9rem; opacity:.85; margin-bottom:8px;">Price: <b>{format_compact_number(current_price_float)}</b></div>'

    html = textwrap_dedent(f"""\
    <div class="app-card">
      <h4 style="margin-bottom:8px;">Fair Value</h4>
      {price_badge_html}
      <div class="table-wrap">
        <table class="compact-table" style="color:var(--text);">
          <thead>
            <tr>
              <th style="text-align:left; border-bottom:1px solid var(--border);">Method</th>
              <th style="text-align:right; border-bottom:1px solid var(--border);">Fair Value</th>
              <th style="text-align:right; border-bottom:1px solid var(--border);">Upside</th>
            </tr>
          </thead>
          <tbody>
            {table_rows_html if table_rows_html else '<tr><td colspan="3" style="padding:10px; opacity:.8;">No fair value results.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
    """).strip()

    st.markdown(html, unsafe_allow_html=True)

def build_price_line_chart(price_dataframe: pd.DataFrame, *, height: int = 300, margin: Optional[dict] = None) -> Figure:
    if price_dataframe is None or price_dataframe.empty:
        raise ValueError("price_dataframe is empty.")
    margin = margin or dict(l=10, r=10, t=10, b=10)

    df = price_dataframe.copy().reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    if "Close" not in df.columns:
        raise ValueError("Expected a 'Close' column in price_dataframe.")

    monthly = df.sort_values("Date").set_index("Date")["Close"].resample("M").last().reset_index()
    fig = px.line(monthly, x="Date", y="Close", height=height, labels={"Date": "Date (YYYY-MM)", "Close": "Close"})
    fig.update_traces(line=dict(width=2.8), hovertemplate="Month: %{x|%Y-%m}<br>Close: %{y:.2f}<extra></extra>")
    fig.update_xaxes(tickformat="%Y-%m", ticklabelmode="period", showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.10)")
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

def build_radar_chart(radar_labels: List[str], radar_values: List[float], *, height: int = 300, edge_pad: float = 0.08, margin: Optional[dict] = None) -> Figure:
    margin = margin or dict(l=18, r=18, t=8, b=8)
    if not radar_labels or not radar_values or len(radar_labels) != len(radar_values):
        empty = go.Figure(); empty.update_layout(height=height, margin=margin); return empty
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
            radialaxis=dict(visible=True, range=[0, 6], showticklabels=False, ticks='', gridcolor="rgba(255,255,255,0.10)", linecolor="rgba(255,255,255,0.20)"),
            angularaxis=dict(tickfont=dict(size=18, color="#E6EEF7"), gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.20)"),
        ),
        showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# =============================================================================
# Sections (Key ratios, News tabs, Evaluation, Valuation, Facts)
# =============================================================================
from core.constants import KEY_RATIO_DICT  # ensure imported

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

    table_rows_html = ""
    for item in key_ratios_payload or []:
        table_rows_html += (
            "<tr>"
            f"<td style='border-bottom:1px solid var(--border); color:var(--text);'>{item.get('fancy_name', item.get('key', '—'))}</td>"
            f"<td style='border-bottom:1px solid var(--border); text-align:right; color:var(--text); white-space:nowrap;'>{_fmt(item.get('value'), item.get('format', 'raw'))}</td>"
            "</tr>"
        )

    html = textwrap_dedent(f"""
    <div class="app-card">
      <h4 style="margin-bottom:6px;">Key Ratios</h4>
      <div class="table-wrap">
        <table class="compact-table" style="color:var(--text);">
          <thead>
            <tr>
              <th style="text-align:left; border-bottom:1px solid var(--border);">Metric</th>
              <th style="text-align:right; border-bottom:1px solid var(--border);">Value</th>
            </tr>
          </thead>
          <tbody>
            {table_rows_html if table_rows_html else "<tr><td colspan='2' style='padding:10px;'>No key ratios.</td></tr>"}
          </tbody>
        </table>
      </div>
    </div>
    """).strip()
    st.markdown(html, unsafe_allow_html=True)

def _news_items_html(stock_obj: Stock) -> str:
    news_items = getattr(stock_obj, "news", None) or getattr(stock_obj, "company_news", None)
    if not isinstance(news_items, list) or not news_items:
        return "<div style='opacity:.8;'>No recent news available.</div>"
    rows: List[str] = []
    for item in news_items[:15]:
        date_str, title, summary, link = None, None, "", None
        if isinstance(item, (list, tuple)) and len(item) >= 4:
            date_str = item[0]; title = item[1]; summary = item[2] if item[2] is not None else ""; link = item[-1]
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
        if link: summary_line += f" — <a href='{link}' target='_blank' style='color:#4EA1FF;'>url</a>"
        body_html = f"<div style='margin:6px 0 8px 0;'>{summary}</div>" if summary else ""
        rows.append(
            f"<details style='margin:6px 0; padding:8px 0; border-bottom:1px solid var(--border);'>"
            f"<summary style='cursor:pointer; opacity:.95;'>{summary_line}</summary>"
            f"{body_html}"
            f"</details>"
        )
    return "".join(rows) if rows else "<div style='opacity:.8;'>No recent news available.</div>"

def render_about_news_officers_tabbed(stock_obj: Stock) -> None:
    tab_about, tab_news, tab_officers = st.tabs(["About", "News", "Officers"])

    with tab_about:
        about_text = getattr(stock_obj, "company_summary", None) or "No company summary available."
        html = textwrap_dedent(f"""
        <div class="app-card">
          <h4 style="margin-bottom:8px;">About</h4>
          <div style="opacity:.95; line-height:1.5;">{about_text}</div>
        </div>
        """).strip()
        st.markdown(html, unsafe_allow_html=True)

    with tab_news:
        items_html = _news_items_html(stock_obj)
        html = textwrap_dedent(f"""
        <div class="app-card">
          <h4 style="margin-bottom:8px;">News</h4>
          {items_html}
        </div>
        """).strip()
        st.markdown(html, unsafe_allow_html=True)

    with tab_officers:
        officers = getattr(stock_obj, "officers", None) or getattr(stock_obj, "company_officers", None)
        if isinstance(officers, list) and officers:
            list_items_html: List[str] = []
            for off in officers:
                if isinstance(off, dict):
                    name = off.get("name") or "—"
                    title = off.get("title") or off.get("position") or ""
                elif isinstance(off, (list, tuple)):
                    name = off[0] if len(off) > 0 else "—"
                    title = off[1] if len(off) > 1 else ""
                else:
                    continue
                list_items_html.append(f"<li style='margin:2px 0;'>{name} — <span style='opacity:.85'>{title}</span></li>")
            body_html = f"<ul style='margin:0; padding-left:18px;'>{''.join(list_items_html)}</ul>"
        else:
            body_html = "<div style='opacity:.8;'>No officer information available.</div>"

        html = textwrap_dedent(f"""
        <div class="app-card">
          <h4 style="margin-bottom:8px;">Officers</h4>
          {body_html}
        </div>
        """).strip()
        st.markdown(html, unsafe_allow_html=True)

# ---------- Evaluation Checklist (tabs)
def render_evaluation_checklist_card(evaluation_payload: Dict[str, Any], criterion_meta: Dict[str, Any]) -> None:
    tab_past, tab_present, tab_future, tab_health, tab_dividend, tab_macro = st.tabs(
        ["Past", "Present", "Future", "Health", "Dividend", "Macroeconomics "]
    )

    def _table_html_for_category(category_key: str) -> str:
        category_results_map: Dict[str, Dict[str, Any]] = evaluation_payload.get(category_key, {}) or {}
        category_meta_map: Dict[str, Any] = criterion_meta.get(category_key, {}) or {}

        ordered_signal_keys: List[str] = [k for k in category_meta_map.keys() if k in category_results_map]
        ordered_signal_keys = ordered_signal_keys[:6]

        body_rows_html_parts: List[str] = []
        for signal_key in ordered_signal_keys:
            meta_for_signal: Dict[str, Any] = category_meta_map.get(signal_key, {}) if isinstance(category_meta_map, dict) else {}
            fancy_name: str = meta_for_signal.get("fancy_name", signal_key)
            check_value = category_results_map.get(signal_key, {}).get("check", 0.0)
            is_passed_boolean = (isinstance(check_value, (int, float)) and float(check_value) >= 0.5)
            pass_fail_emoji = "✅" if is_passed_boolean else "❌"

            # tooltip = criteria text
            criteria_text: Optional[str] = meta_for_signal.get("criteria")
            criteria_html = make_html_paragraph_safe(criteria_text)
            tooltip_html = build_help_tip_html(bubble_title_text="Criterion", bubble_content_html=criteria_html) if criteria_text else ""

            name_cell_html = f"{html_module.escape(fancy_name)}{tooltip_html}"

            body_rows_html_parts.append(
                f"<tr>"
                f"<td style='border-bottom:1px solid var(--border); color:var(--text);'>{name_cell_html}</td>"
                f"<td style='border-bottom:1px solid var(--border); text-align:center; color:var(--text); white-space:nowrap;'>{pass_fail_emoji}</td>"
                f"</tr>"
            )

        while len(body_rows_html_parts) < 6:
            body_rows_html_parts.append(
                "<tr>"
                "<td style='border-bottom:1px solid var(--border); color:var(--text); opacity:.5;'>—</td>"
                "<td style='border-bottom:1px solid var(--border); text-align:center; color:var(--text); opacity:.5;'>—</td>"
                "</tr>"
            )

        table_html: str = textwrap_dedent(f"""
        <div class="app-card">
          <h4 style="margin-bottom:8px;">Evaluation Checklist</h4>
          <div class="table-wrap">
            <table class="compact-table" style="color:var(--text);">
              <thead>
                <tr>
                  <th style="text-align:left; border-bottom:1px solid var(--border);">Criterion</th>
                  <th style="text-align:center; border-bottom:1px solid var(--border);">Pass / Fail</th>
                </tr>
              </thead>
              <tbody>
                {''.join(body_rows_html_parts)}
              </tbody>
            </table>
          </div>
        </div>
        """).strip()
        return table_html

    with tab_past:     st.markdown(_table_html_for_category("past"),     unsafe_allow_html=True)
    with tab_present:  st.markdown(_table_html_for_category("present"),  unsafe_allow_html=True)
    with tab_future:   st.markdown(_table_html_for_category("future"),   unsafe_allow_html=True)
    with tab_health:   st.markdown(_table_html_for_category("health"),   unsafe_allow_html=True)
    with tab_dividend: st.markdown(_table_html_for_category("dividend"), unsafe_allow_html=True)
    with tab_macro:    st.markdown(_table_html_for_category("macroeconomics"),    unsafe_allow_html=True)

# ---------- Valuation (simplified per your edit) — now using responsive grid
def render_valuation_section(fair_value_payload: Dict[str, Any]) -> None:

    order = [
        "price_earning_multiples",
        "discounted_cash_flow_one_stage",
        "discounted_cash_flow_two_stage",
        "discounted_dividend_two_stage",
        "return_on_equity",
        "excess_return",
        "graham_number",
    ]

    def _card_html(
        title: str,
        desc: Optional[str],
        inputs: List[str],
        feas: Optional[str],
        fv: Any,
        mos: Any,
    ) -> str:
        fv_txt = format_compact_number(fv)
        tip_parts: List[str] = []
        if desc:
            tip_parts.append(make_html_paragraph_safe(desc))
        if feas:
            tip_parts.append("<span class='subhead'>Feasibility &amp; Notes</span>")
            tip_parts.append(make_html_paragraph_safe(feas))
        tip_html = build_help_tip_html("About this method", "".join(tip_parts)) if tip_parts else ""

        title_row_html = (
            "<div style='display:flex;align-items:center;gap:8px;"
            "font-weight:700;font-size:1.05rem;margin-bottom:6px;'>"
            f"<span>{html_module.escape(str(title))}</span>{tip_html}"
            "</div>"
        )

        card_html = textwrap_dedent(f"""
        <div class="app-card">
          {title_row_html}
          <div class="keyline"></div>
          <div class="kv"><div class="k">Fair Value</div><div class="v">{fv_txt}</div></div>
        </div>
        """).strip()

        return card_html

    cards_html_list: List[str] = []
    for method_key in order:
        meta = VALUATION.get(method_key, {})
        payload = fair_value_payload.get(method_key, {}) or {}
        outputs = payload.get("outputs", {}) or {}

        fv = outputs.get("Fair Value", np.nan)
        effective_mos = outputs.get("Margin Of Safety Applied", None)
        if not isinstance(effective_mos, (int, float)):
            effective_mos = st.session_state.get("margin_of_safety", DEFAULT_PARAM_DICT.get("margin_of_safety", 0.25))

        cards_html_list.append(
            _card_html(
                title=meta.get("fancy_name", method_key),
                desc=meta.get("description"),
                inputs=meta.get("inputs", []),
                feas=meta.get("feasibility"),
                fv=fv,
                mos=effective_mos,
            )
        )

    grid_container_html = '<div class="card-grid">' + "".join(cards_html_list) + "</div>"
    st.markdown(grid_container_html, unsafe_allow_html=True)

def render_evaluation_section(evaluation_payload: Dict[str, Any], criterion_meta: Dict[str, Any]) -> None:
    def _fmt_val(value_any: Any) -> str:
        if isinstance(value_any, (int, float)):
            if not np.isfinite(value_any):
                return "—"
            return format_compact_number(value_any)
        if value_any is None:
            return "—"
        return str(value_any)

    def _card_for_signal(signal_key: str, result: Dict[str, Any], meta_map: Dict[str, Any]) -> str:
        meta = meta_map.get(signal_key, {}) if isinstance(meta_map, dict) else {}
        title = meta.get("fancy_name", signal_key)
        desc = meta.get("description")
        input_text = meta.get("input")
        method_text = meta.get("method")
        criteria_text = meta.get("criteria")

        tip_parts: List[str] = []
        if desc: tip_parts.append(make_html_paragraph_safe(desc))
        if criteria_text:
            tip_parts.append("<span class='subhead'>Criterion</span>")
            tip_parts.append(make_html_paragraph_safe(criteria_text))
        tooltip_html = build_help_tip_html("About this signal", "".join(tip_parts)) if tip_parts else ""

        title_row_html = (
            "<div style='display:flex;align-items:center;gap:8px;"
            "font-weight:700;font-size:1.05rem;margin-bottom:6px;'>"
            f"<span>{html_module.escape(str(title))}</span>{tooltip_html}"
            "</div>"
        )

        meta_bits_html_list: List[str] = []
        if input_text:
            meta_bits_html_list.append(
                "<div style='opacity:.8; font-size:.85rem; margin:2px 0;'>"
                f"<span style='opacity:.8;'>Input:</span> {html_module.escape(str(input_text))}"
                "</div>"
            )
        if method_text:
            meta_bits_html_list.append(
                "<div style='opacity:.8; font-size:.85rem; margin:2px 0;'>"
                f"<span style='opacity:.8;'>Method:</span> {html_module.escape(str(method_text))}"
                "</div>"
            )
        if criteria_text:
            meta_bits_html_list.append(
                "<div style='opacity:.8; font-size:.85rem; margin:2px 0;'>"
                f"<span style='opacity:.8;'>Criterion:</span> {html_module.escape(str(criteria_text))}"
                "</div>"
            )
        meta_block_html = "".join(meta_bits_html_list)

        check_val = result.get("check", None)
        pass_html = ""
        if isinstance(check_val, (int, float)):
            passed = float(check_val) >= 0.5
            pass_html = f"<div class='kv'><div class='k'>Pass</div><div class='v'>{'✅' if passed else '❌'}</div></div>"

        outputs = result.get("outputs", {}) or {}
        outputs_row_html_list: List[str] = []
        for key_text, value_any in outputs.items():
            outputs_row_html_list.append(
                f"<div class='kv'><div class='k'>{html_module.escape(str(key_text))}</div><div class='v'>{_fmt_val(value_any)}</div></div>"
            )
        outputs_html = "".join(outputs_row_html_list) if outputs_row_html_list else "<div style='opacity:.8;'>No outputs.</div>"

        return textwrap_dedent(f"""
        <div class="app-card">
          {title_row_html}
          {meta_block_html}
          <div class="keyline"></div>
          {pass_html}
          {outputs_html}
        </div>
        """).strip()

    for group_key in ["past", "present", "future", "health", "dividend", "macroeconomics"]:
        group_data = evaluation_payload.get(group_key, {}) or {}
        if not group_data:
            continue

        st.markdown(f"#### {group_key.capitalize()}")

        meta_map = criterion_meta.get(group_key, {}) if isinstance(criterion_meta, dict) else {}
        cards_html_list: List[str] = []
        for signal_key, result in group_data.items():
            if not isinstance(result, dict):
                continue
            cards_html_list.append(_card_for_signal(signal_key, result, meta_map))

        if not cards_html_list:
            st.caption("No signals available.")
            continue

        grid_container_html = '<div class="card-grid">' + "".join(cards_html_list) + "</div>"
        st.markdown(grid_container_html, unsafe_allow_html=True)
        st.markdown("---")

# =============================================================================
# Fact Sheet: split into data prep + scalar and series renderers
# =============================================================================
def prepare_fact_sheet_data(stock_obj: Stock) -> Dict[str, Any]:
    """Collect and structure all mappings once for both renderers."""
    try:
        complete_payload_dictionary: Dict[str, Any] = stock_obj.to_payload() if hasattr(stock_obj, "to_payload") else {}
    except Exception:
        complete_payload_dictionary = {}

    basic_information_mapping: Dict[str, Any] = complete_payload_dictionary.get("basic_information", {}) if isinstance(complete_payload_dictionary, dict) else {}
    financial_points_mapping: Dict[str, Dict[str, Any]] = complete_payload_dictionary.get("financial_points", {}) if isinstance(complete_payload_dictionary, dict) else {}
    derived_metrics_mapping: Dict[str, Any] = complete_payload_dictionary.get("derived_metrics", {}) if isinstance(complete_payload_dictionary, dict) else {}

    # Name maps
    basic_info_name_map: Dict[str, str] = {entry["alias"]: entry.get("fancy_name", entry["alias"]) for entry in STOCK_INFO}
    financial_points_name_map: Dict[str, str] = {alias: meta.get("fancy_name", alias) for alias, meta in FINANCIALS.items()}
    derived_name_map: Dict[str, str] = {var: meta.get("fancy_name", var) for var, meta in DERIVED_METRICS.items()}

    # Split derived metrics into scalar vs series
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

def _render_scalar_table_card_html(table_title_text: str, mapping_name_to_value: Dict[str, Any], name_map: Dict[str, str]) -> str:
    if not isinstance(mapping_name_to_value, dict) or not mapping_name_to_value:
        return textwrap_dedent(f"""
        <div class="app-card" style="max-width:600px; width:100%; display:inline-block;">
          <h4 style="margin-bottom:8px;">{table_title_text}</h4>
          <div style="opacity:.8;">No scalar data available.</div>
        </div>
        """).strip()

    table_rows_html = ""
    for metric_name in mapping_name_to_value.keys():
        if metric_name == "company_summary":
            continue
        display_name = name_map.get(metric_name, metric_name)
        table_rows_html += (
            "<tr>"
            f"<td style='border-bottom:1px solid var(--border); color:var(--text);'>{display_name}</td>"
            f"<td style='border-bottom:1px solid var(--border); text-align:right; white-space:nowrap;'>{_fmt_scalar_value_for_display(mapping_name_to_value[metric_name])}</td>"
            "</tr>"
        )
    return textwrap_dedent(f"""
    <div class="app-card" style="max-width:600px; width:100%; display:inline-block;">
      <h4 style="margin-bottom:8px;">{table_title_text}</h4>
      <div class="table-wrap">
        <table class="compact-table" style="color:var(--text);">
        <thead>
          <tr>
            <th style="text-align:left; border-bottom:1px solid var(--border);">Metric</th>
            <th style="text-align:right; border-bottom:1px solid var(--border);">Value</th>
          </tr>
        </thead>
          <tbody>
            {table_rows_html}
          </tbody>
        </table>
      </div>
    </div>
    """).strip()

def _render_series_table_card_html(table_title_text: str, mapping_metric_to_series_map: Dict[str, Dict[str, Any]], name_map: Dict[str, str]) -> str:
    if not isinstance(mapping_metric_to_series_map, dict) or not mapping_metric_to_series_map:
        return textwrap_dedent(f"""
        <div class="app-card" style="width:100%;">
          <h4 style="margin-bottom:8px;">{table_title_text}</h4>
          <div style="opacity:.8;">No time-series data available.</div>
        </div>
        """).strip()

    all_timestamp_labels_set = set()
    for series_mapping in mapping_metric_to_series_map.values():
        all_timestamp_labels_set.update(str(k) for k in (series_mapping or {}).keys())

    latest_five_timestamp_labels_desc: List[str] = sorted(all_timestamp_labels_set, reverse=True)[:5]
    header_cells_html = "".join(
        f"<th style='text-align:right; padding:8px 10px; border-bottom:1px solid var(--border); white-space:nowrap;'>{label}</th>"
        for label in latest_five_timestamp_labels_desc
    )

    def _fmt_series_point(v: Any) -> str:
        if v is None:
            return "—"
        try:
            f = float(v)
            if not np.isfinite(f):
                return "—"
            return format_compact_number(f)
        except Exception:
            return "—"

    body_rows_html = ""
    for metric_name in mapping_metric_to_series_map.keys():
        series_map_for_metric = mapping_metric_to_series_map.get(metric_name, {}) or {}
        display_name = name_map.get(metric_name, metric_name)
        value_cells_html_parts = []
        for timestamp_label in latest_five_timestamp_labels_desc:
            value_cells_html_parts.append(
                f"<td style='padding:8px 10px; border-bottom:1px solid var(--border); text-align:right; white-space:nowrap;'>{_fmt_series_point(series_map_for_metric.get(timestamp_label))}</td>"
            )
        body_rows_html += (
                "<tr>"
                f"<td style='padding:8px 10px; border-bottom:1px solid var(--border); width:34%; white-space: normal;'>{display_name}</td>"
                + "".join(value_cells_html_parts)
                + "</tr>"
        )

    return textwrap_dedent(f"""
    <div class="app-card" style="width:100%;">
      <h4 style="margin-bottom:8px;">{table_title_text}</h4>
      <div class="table-wrap">
        <table style="border-collapse:collapse; color:var(--text); font-size:0.95rem;">
        <thead>
          <tr>
            <th style="text-align:left; padding:8px 10px; border-bottom:1px solid var(--border); width:34%; white-space: normal;">Metric</th>
            {header_cells_html}
          </tr>
        </thead>
          <tbody>
            {body_rows_html if body_rows_html else "<tr><td colspan='6' style='padding:10px;'>No time-series data available.</td></tr>"}
          </tbody>
        </table>
      </div>
      <div style="opacity:.7; font-size:.85rem; margin-top:6px;">“—” means no data for that timestamp.</div>
    </div>
    """).strip()

def render_fact_sheet_scalars(data: Dict[str, Any]) -> None:
    """Render the scalar-side Fact Sheet tabs."""
    tab_original, tab_derived = st.tabs(["Original", "Derived"])
    with tab_original:
        name_map = data["basic_info_name_map"]
        html = _render_scalar_table_card_html("Basic Information (Original)", data["basic_information_mapping"], name_map)
        st.markdown(html, unsafe_allow_html=True)
    with tab_derived:
        derived_name_map = {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()}
        html = _render_scalar_table_card_html("Derived Scalars", data["derived_scalar_mapping"], derived_name_map)
        st.markdown(html, unsafe_allow_html=True)

def render_fact_sheet_series(data: Dict[str, Any]) -> None:
    """Render the series-side Fact Sheet tabs."""
    tab_original, tab_derived = st.tabs(["Original", "Derived"])
    with tab_original:
        html = _render_series_table_card_html(
            "Financial Points (Original)",
            data["financial_points_mapping"],
            data["financial_points_name_map"],
        )
        st.markdown(html, unsafe_allow_html=True)
    with tab_derived:
        html = _render_series_table_card_html(
            "Derived Series (latest 5)",
            data["derived_series_mapping"],
            {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
        )
        st.markdown(html, unsafe_allow_html=True)


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
                "For non-US stocks, please refer to Yahoo Finance. For example, 9697.T (Japan), "
                "CDR.WA (Poland), 0700.HK (Hong Kong), ULVR.L (London)."
            ),
        )

        # Valuation params in expander
        with st.expander("Valuation Parameters (Optional)", expanded=False):
            st.caption("The parameters will be calculated. Tweak them after which to see different valuations.")
            discount_rate = st.number_input("Discount Rate", key="discount_rate", step=0.005, format="%.3f")
            growth_rate = st.number_input("Growth Rate", key="growth_rate", step=0.005, format="%.3f")
            decline_rate = st.number_input("Growth Decline Rate (per year)", key="decline_rate", step=0.005, format="%.3f")
            terminal_growth_rate = st.number_input("Terminal Growth Rate", key="terminal_growth_rate", step=0.005, format="%.3f")
            margin_of_safety = st.number_input("Margin of Safety", key="margin_of_safety", step=0.05, format="%.2f")
            n_years1 = st.number_input("Projection Years (Stage 1)", key="n_years1", min_value=1)
            n_years2 = st.number_input("Projection Years (Stage 2)", key="n_years2", min_value=0)
            risk_free_rate = st.number_input("Risk-Free Rate", key="risk_free_rate", step=0.005, format="%.3f")
            average_market_return = st.number_input("Average Market Return", key="average_market_return", step=0.005, format="%.3f")

        # RUN button goes *below* the Valuation Parameters expander
        run_button_pressed = st.button(
            "Run",
            type="primary",
            use_container_width=True,
            on_click=_on_run_clicked_reset_urls_if_ticker_changed,  # ← add this
        )

        insert_vertical_row_spacing(8)

        # Fiscal URLs expander
        with st.expander("Fiscal Report URLs (Optional)", expanded=False):
            st.caption(
                "You may copy/paste the URL(s) for any online documents below. "
                "Their urls, if any, will be added to the generated prompt."
                "It's highly recommended."
            )
            url_10k = st.text_input("10-K", key="url_10k", help="Annual report (10-K) URL.")
            url_10q = st.text_input("10-Q", key="url_10q", help="Quarterly report (10-Q) URL.")
            url_extra = st.text_input("Extra", key="url_extra", help="Any additional relevant URL (investor deck, etc.).")

        # Generate Prompt button goes *outside* the expander, right after it
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
# Prompt Collector
# =============================================================================
def _format_key_value_lines(name_map: Dict[str, str], data_map: Dict[str, Any]) -> str:
    """Format key-value pairs using a display name map; skip None/empty gracefully."""
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
                # strings, dates, misc
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
    # Sort by upside if available
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
    """
    series_map: { metric_key: { timestamp_str: value, ... }, ... }
    Output latest 5 timestamps (descending) for each metric to mirror on-screen table.
    """
    # Collect universe of timestamps
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
    return "\n".njoin(lines) if False else "\n".join(lines)

def _format_evaluation_lines(evaluation_payload: Dict[str, Any]) -> str:
    """
    Dump all groups/signals with pass/fail and outputs.
    """
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
            meta = CRITERION.get(group_key, {}).get(signal_key, {}) if isinstance(CRITERION.get(group_key, {}), dict) else {}
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
    """Return only non-empty, non-default placeholders."""
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
    """
    Build the final plain-text prompt per requested sections.
    """

    company_summary_text: str = getattr(stock_obj, "company_summary", "") or ""

    basic_info_lines = _format_key_value_lines(
        prepared_fact_data["basic_info_name_map"],
        prepared_fact_data["basic_information_mapping"],
    )

    derived_scalar_lines = _format_key_value_lines(
        {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
        prepared_fact_data["derived_scalar_mapping"],
    )

    # Key ratios (from payload or config fallback)
    if not key_ratios_payload:
        key_ratios_payload = build_key_ratios_from_config(stock_obj)
    key_ratios_lines = _format_key_ratios_lines(key_ratios_payload)

    # Fair values
    current_price_val = getattr(stock_obj, "current_price", None)
    fair_values_lines = _format_fair_values_lines(fair_values, current_price_val)

    # Series (original + derived)
    series_original_lines = _format_series_table_lines(
        prepared_fact_data["financial_points_mapping"],
        prepared_fact_data["financial_points_name_map"],
    )
    series_derived_lines = _format_series_table_lines(
        prepared_fact_data["derived_series_mapping"],
        {k: v.get("fancy_name", k) for k, v in DERIVED_METRICS.items()},
    )

    officers_lines = _format_officers_lines(getattr(stock_obj, "officers", None) or getattr(stock_obj, "company_officers", None))

    evaluation_lines = _format_evaluation_lines(evaluation_payload)

    # URLs
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

    # Assemble final plain string with clean spacing (no markdown decorations)
    sections: List[str] = []

    sections.append("Company Summary:\n" + (company_summary_text.strip() or "(no summary)"))

    sections.append("Stock basic information:\n" + (basic_info_lines.strip() or "—"))

    sections.append("Stock key ratios:\n" + (key_ratios_lines.strip() or "—"))

    sections.append("Stock Fair values:\n" + (fair_values_lines.strip() or "—"))

    # Financial points
    fp_blocks: List[str] = []
    fp_blocks.append("(Original Series - latest 5):\n" + (series_original_lines.strip() or "—"))
    fp_blocks.append("(Derived Series - latest 5):\n" + (series_derived_lines.strip() or "—"))
    sections.append("Stock financial points\n" + "\n".join(fp_blocks))

    sections.append("Company Officer:\n" + (officers_lines.strip() or "—"))

    sections.append("Evaluation:\n" + (evaluation_lines.strip() or "—"))

    # URLs
    url_block = urls_block.strip() if urls_block else "(none provided)"
    sections.append("Online document URLs:\n" + url_block)

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
    st.session_state.setdefault("generated_prompt_text", "")  # where we store the built prompt

    ensure_default_param_keys()

    ticker_symbol, override_params, run_pressed, gen_prompt_pressed = render_left_panel()

    # Reset "has_run" if ticker text changed
    ticker_changed = (st.session_state.last_ticker != ticker_symbol)

    # Run pipeline
    if run_pressed:
        try:
            if (st.session_state.stock is None) or ticker_changed:
                with st.spinner("Fetching stock & building evaluation…"):
                    stock = fetch_stock(ticker_symbol)
                    st.session_state.stock = stock

                    evaluation_payload = run_evaluation_only()
                    val = Valuation(stock)
                    val_params = val.get_valuation_params()

                    st.session_state["_pending_param_keys"] = {
                        "discount_rate": float(val_params["discount_rate"]),
                        "growth_rate": float(val_params["growth_rate"]),
                        "decline_rate": float(val_params["decline_rate"]),
                        "terminal_growth_rate": float(val_params["terminal_growth_rate"]),
                        "margin_of_safety": float(val_params["margin_of_safety"]),
                        "n_years1": int(val_params["n_years1"]),
                        "n_years2": int(val_params["n_years2"]),
                        "risk_free_rate": float(val_params["risk_free_rate"]),
                        "average_market_return": float(val_params["average_market_return"]),
                    }

                    st.session_state.evaluation_payload = evaluation_payload
                    st.session_state.last_ticker = ticker_symbol
                    st.session_state["_show_prompt_success"] = False

                    override_params = {**val_params, **override_params}

            with st.spinner("Computing valuations…"):
                st.session_state.fair_value_payload = run_valuation_only(st.session_state.stock, override_params)

            # Clear any prior error on success
            st.session_state["_top_error"] = ""

            # Mark that Run has been completed for current ticker
            st.session_state.has_run = True

            st.rerun()

        except ValueError as e:
            # Capture the message and show a toast; render it later below the title
            st.session_state["_top_error"] = str(e)
            st.toast(str(e))
            st.session_state.has_run = False
            # ensure state is consistent
            st.session_state.stock = None
            st.session_state.fair_value_payload = None
            st.session_state["_show_prompt_success"] = False

        except Exception as e:
            msg = f"Failed to fetch or compute for '{ticker_symbol}'. Please try again. Details: {e}"
            st.session_state["_top_error"] = msg
            st.toast(msg)
            st.session_state.has_run = False
            st.session_state.stock = None
            st.session_state.fair_value_payload = None
            st.session_state["_show_prompt_success"] = False

    # Title and top-of-page notices (always visible and below the deploy banner)
    st.title("Value Investing Dashboard")

    # Success message for prompt generation — pinned right under the title
    if st.session_state.get("_show_prompt_success"):
        st.success("✅ Prompt generated. Open the **Prompts** tab to copy it.")

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
    chips_html = "".join(f'<span class="chip">{t}</span>' for t in [sector_string, industry_string, country_string] if t)
    st.markdown(
        textwrap_dedent(f"""
        <div class="company-header">
          <span class="company-name">{company_name_string}</span>
          {chips_html}
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    # Add a Prompts tab after Fact Sheet
    tab_overview, tab_valuation, tab_evaluation, tab_facts, tab_prompts = st.tabs(["Overview", "Valuation", "Evaluation", "Fact Sheet", "Prompts"])

    fair_values = st.session_state.fair_value_payload
    evaluation_payload = st.session_state.evaluation_payload or {}

    # Handle "Generate Prompt" click from the sidebar
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
            st.session_state["_show_prompt_success"] = True  # <— mark to show notice under title

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
                chart = build_price_line_chart(price_df.tail(3650 + 30), height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.caption("No price data available.")

        with col_radar_chart:
            st.markdown("#### Evaluation Snowflakes")
            category_scores = compute_category_scores_for_radar(evaluation_payload)
            radar_labels = ["past", "present", "future", "health", "dividend", "macroeconomics"]
            radar_values = [category_scores.get(k, 0.0) for k in radar_labels]
            radar_fig = build_radar_chart(radar_labels, radar_values, height=300, edge_pad=0.10, margin=dict(l=10, r=10, t=10))
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

    with tab_valuation:
        render_valuation_section(fair_values)

    with tab_evaluation:
        render_evaluation_section(evaluation_payload, CRITERION)

    with tab_facts:
        insert_vertical_row_spacing(8)
        data = prepare_fact_sheet_data(stock_obj)
        left_col, right_col = st.columns([0.2, 0.5], gap="small")
        with left_col:
            render_fact_sheet_scalars(data)
        with right_col:
            render_fact_sheet_series(data)
        insert_vertical_row_spacing(8)

    with tab_prompts:
        st.subheader("Prompt")
        st.caption("Copy and paste the Prompt to your AI to generate the final report. Enable reasoning and web search (even the deep research if you like). Gemini 2.5pro is highly recommended.")
        if st.session_state.get("generated_prompt_text"):
            st.code(st.session_state["generated_prompt_text"], language=None)
        else:
            st.info("No prompt yet. Use the **Generate Prompt** button in the sidebar under **Fiscal Report URLs**.")

if __name__ == "__main__":
    main()
