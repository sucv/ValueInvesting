# utils/stock.py
from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timezone
import calendar
import numpy as np
import pandas as pd

# -----------------------------
# Core numeric helpers (Series)
# -----------------------------

def _to_numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def _align_like(x: pd.Series, y: pd.Series) -> Tuple[pd.Series, pd.Series]:
    # Align y to x's index order (latest -> older)
    y2 = y.reindex(x.index)
    return x, y2

def _safe_add(X: pd.Series, Y: pd.Series) -> pd.Series:
    xs = _to_numeric(X).fillna(0)
    ys = _to_numeric(_align_like(xs, Y)[1]).fillna(0)
    z = xs + ys
    z.name = X.name or Y.name
    return z

def _safe_minus(X: pd.Series, Y: pd.Series) -> pd.Series:
    xs = _to_numeric(X).fillna(0)
    ys = _to_numeric(_align_like(xs, Y)[1]).fillna(0)
    z = xs - ys
    z.name = X.name or Y.name
    return z

def _safe_mul(X: pd.Series, Y: pd.Series) -> pd.Series:
    xs = _to_numeric(X)
    ys = _to_numeric(_align_like(xs, Y)[1])
    z = xs * ys
    z.name = X.name or Y.name
    return z

def _safe_div(X: pd.Series, Y: pd.Series) -> pd.Series:
    xs = _to_numeric(X)
    ys = _to_numeric(_align_like(xs, Y)[1])
    with np.errstate(divide="ignore", invalid="ignore"):
        z = xs / ys
        z = z.mask((ys == 0) | ys.isna())
    z.name = X.name or Y.name
    return z

def _safe_shift(s: pd.Series, n: int = -1) -> pd.Series:
    """
    Horizontal shift along the Series (index is latest -> older).
    n = -1: drop first, shift left, pad NaN at end
    n =  1: drop last, shift right, pad NaN at beginning
    """
    if s.empty or n == 0:
        return s.copy()
    k = int(n)
    m = len(s)
    if abs(k) >= m:
        return pd.Series([np.nan] * m, index=s.index, name=s.name)
    out = pd.Series(np.nan, index=s.index, name=s.name)
    if k < 0:
        out.iloc[: m + k] = s.iloc[-k :].to_numpy()
    else:
        out.iloc[k:] = s.iloc[: m - k].to_numpy()
    return out

def _safe_yoy_growth(s: pd.Series) -> pd.Series:
    v = _to_numeric(s).copy()
    out = v.copy()
    for i in range(len(v) - 1):
        num = v.iloc[i]
        denom = v.iloc[i + 1]
        out.iloc[i] = np.nan if (pd.isna(num) or pd.isna(denom) or denom == 0) else (num / denom - 1)
    if len(out) > 0:
        out.iloc[-1] = np.nan
    out.name = s.name
    return out

def _safe_cagr(s: pd.Series, n_year: int) -> float:
    if n_year <= 0:
        return float("nan")

    values = _to_numeric(s)
    idx = s.index

    # Try reading dates/years from index
    try:
        # allow int years; convert to timestamps (Dec-31 of that year)
        if np.issubdtype(np.array(idx)[0].__class__, np.integer) or all(str(x).isdigit() for x in idx):
            col_dates = pd.to_datetime([f"{int(y)}-12-31" for y in idx], errors="coerce")
        else:
            col_dates = pd.to_datetime(idx, errors="coerce")
        has_dates = isinstance(col_dates, pd.DatetimeIndex) and not col_dates.isna().all()
    except Exception:
        has_dates = False

    latest_pos = None
    for i in range(len(values)):
        if pd.notna(values.iloc[i]):
            latest_pos = i
            break
    if latest_pos is None:
        return float("nan")

    latest_value = float(values.iloc[latest_pos])

    start_pos = None
    years_diff = float(n_year)

    if has_dates and pd.notna(col_dates[latest_pos]):
        latest_date = col_dates[latest_pos]
        for j in range(latest_pos + 1, len(values)):
            if pd.isna(col_dates[j]):
                continue
            if latest_date.year - col_dates[j].year >= n_year:
                start_pos = j
                years_diff = max((latest_date - col_dates[j]).days / 365.25, 0.0)
                break
        if start_pos is None:
            candidate = latest_pos + n_year
            if candidate < len(values):
                start_pos = candidate
                if pd.notna(col_dates[candidate]):
                    years_diff = max((latest_date - col_dates[candidate]).days / 365.25, 0.0)
    else:
        candidate = latest_pos + n_year
        if candidate < len(values):
            start_pos = candidate

    if start_pos is None:
        return float("nan")

    start_value = np.nan
    for k in range(start_pos, len(values)):
        if pd.notna(values.iloc[k]):
            start_value = float(values.iloc[k])
            if has_dates and pd.notna(col_dates[latest_pos]) and pd.notna(col_dates[k]):
                years_diff = max((col_dates[latest_pos] - col_dates[k]).days / 365.25, 0.0)
            break

    if np.isnan(start_value) or years_diff <= 0:
        return float("nan")

    if latest_value <= 0 or start_value <= 0:
        return float("nan")

    try:
        cagr = (latest_value / start_value) ** (1.0 / years_diff) - 1.0
    except Exception:
        cagr = float("nan")
    return float(cagr)

def _safe_sign_adjust(X: pd.Series, mode: str = "neg_to_pos") -> pd.Series:
    xs = _to_numeric(X)
    if mode == "neg_to_pos":
        y = xs.where((xs >= 0) | xs.isna(), -xs)
    elif mode == "pos_to_neg":
        y = xs.where((xs <= 0) | xs.isna(), -xs)
    elif mode == "flip_all":
        y = -xs
    elif mode == "abs_all":
        y = xs.abs()
    else:
        raise ValueError(
            f'Unknown mode="{mode}". Use one of: "neg_to_pos", "pos_to_neg", "flip_all", "abs_all".'
        )
    y.name = X.name
    return y

def _safe_mean(series: pd.Series, n: int = 1) -> float:
    """Mean of the leftmost n values (latest first)."""
    if series is None or len(series) == 0:
        return float("nan")
    vals = _to_numeric(series).values
    return float(np.nanmean(vals[: max(int(n), 0)])) if vals.size else float("nan")

def _safe_median(series: pd.Series, n: int = 1) -> float:
    """Median of the leftmost n values (latest first)."""
    if series is None or len(series) == 0:
        return float("nan")
    vals = _to_numeric(series).values
    subset = vals[: max(int(n), 0)]
    subset = subset[~np.isnan(subset)]
    if subset.size == 0:
        return float("nan")
    return float(np.median(subset))

# -----------------------------
# Prices (lookup by nearest date)
# -----------------------------

def _get_price_at(X: pd.Series, prices: pd.DataFrame) -> pd.Series:
    """
    Map each date in X.index to the nearest daily Close in `prices`.
    Returns a Series (index = X.index, name preserved if present).
    """
    x_cols = pd.to_datetime(X.index, errors="coerce")

    if "Close" not in prices.columns:
        raise KeyError("No 'Close' column found in prices.")
    s = pd.to_numeric(prices["Close"], errors="coerce")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise TypeError("prices.index must be a DatetimeIndex")
    s = s.sort_index()

    out_vals = []
    for d in x_cols:
        if pd.isna(d):
            out_vals.append(np.nan)
            continue
        idx = s.index.get_indexer([d], method="nearest")[0]
        out_vals.append(float(s.iloc[idx]) if not pd.isna(s.iloc[idx]) else np.nan)

    Z = pd.Series(out_vals, index=X.index, name=(X.name or "price_at"))
    return Z

# -----------------------------
# yfinance / returns helpers
# -----------------------------

def _extract_close_series(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty:
        return pd.Series(dtype=float)
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index, errors="coerce")

    s = None
    if isinstance(df.columns, pd.MultiIndex):
        if ("Close" in df.columns.get_level_values(0)):
            try:
                s = df.xs("Close", level=0, axis=1)
                if isinstance(s, pd.DataFrame) and s.shape[1] >= 1:
                    s = s.iloc[:, 0]
            except Exception:
                pass
    else:
        if "Close" in df.columns:
            s = df["Close"]

    if s is None:
        s = df.iloc[:, -1]

    s = pd.to_numeric(s, errors="coerce")
    s = s.sort_index()
    return s

def _winsorize(series: pd.Series, lower=0.01, upper=0.99) -> pd.Series:
    q_low, q_high = series.quantile([lower, upper])
    return series.clip(lower=q_low, upper=q_high)

def _pct_ret(close: pd.Series) -> pd.Series:
    if close.empty:
        return close
    close = close.copy()
    close[(~np.isfinite(close)) | (close <= 0)] = np.nan
    ret = close.pct_change()
    return ret

def _slice_ticker_block(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    try:
        block = df.loc[:, (slice(None), ticker)]
        if isinstance(block, pd.Series):
            block = block.to_frame()
        if isinstance(block.columns, pd.MultiIndex):
            try:
                block = block.reindex([("Open", ticker), ("Close", ticker)], axis=1)
            except Exception:
                pass
        return block
    except Exception:
        return pd.DataFrame()

# -----------------------------
# Fiscal-year & dividends
# -----------------------------

def _month(date_str: str) -> int:
    return int(str(date_str).split("-")[1])

def _distinct_as_of_dates(financials: pd.DataFrame, frequency: str) -> List[str]:
    rows = list(financials.columns)
    uniq = sorted(set(map(str, rows)))
    return uniq

def _infer_fye_month(financials: pd.DataFrame) -> int:
    months = []
    annual_dates = _distinct_as_of_dates(financials, "ANNUAL")
    if annual_dates:
        months += [_month(d) for d in annual_dates if "-" in d]
    if not months:
        quarterly_dates = _distinct_as_of_dates(financials, "QUARTERLY")
        months += [_month(d) for d in quarterly_dates if "-" in d]
    if not months:
        return 12
    from collections import Counter
    cnt = Counter(months)
    return cnt.most_common(1)[0][0]

def _fiscal_year_end_for(dt: date, fye_month: int) -> date:
    end_year = dt.year if dt.month <= fye_month else dt.year + 1
    last_day = calendar.monthrange(end_year, fye_month)[1]
    return date(end_year, fye_month, last_day)

def _fiscal_year_label_for(dt: date, fye_month: int) -> int:
    return _fiscal_year_end_for(dt, fye_month).year

def _annual_dps_complete_years(
    dividends: pd.Series,
    fye_month: int,
    as_of: date = None,
) -> pd.Series:
    """
    Return a Series (name='dividend_per_share') indexed by fiscal year-end dates (latest -> older),
    summing DPS for each FULL fiscal year (latest incomplete year dropped).
    """
    if dividends is None or len(dividends) == 0:
        return pd.Series(dtype=float, name="dividend_per_share")

    if as_of is None:
        as_of = date.today()

    totals_by_fy = {}
    for pay_date, amount in dividends.items():
        if pd.isna(amount):
            continue
        try:
            pay_dt = pay_date.date() if isinstance(pay_date, pd.Timestamp) else pd.to_datetime(pay_date).date()
            fiscal_year_label = _fiscal_year_label_for(pay_dt, fye_month)
            totals_by_fy[fiscal_year_label] = totals_by_fy.get(fiscal_year_label, 0.0) + float(amount)
        except Exception:
            continue

    if not totals_by_fy:
        return pd.Series(dtype=float, name="dividend_per_share")

    current_fye_date = _fiscal_year_end_for(as_of, fye_month)
    current_fy_label = current_fye_date.year
    if as_of < current_fye_date:
        totals_by_fy.pop(current_fy_label, None)

    if not totals_by_fy:
        return pd.Series(dtype=float, name="dividend_per_share")

    fy_end_dates = [pd.Timestamp(year, fye_month, calendar.monthrange(year, fye_month)[1])
                    for year in totals_by_fy.keys()]

    sorted_pairs = sorted(zip(fy_end_dates, totals_by_fy.values()), key=lambda x: x[0], reverse=True)
    idx = pd.Index([pair[0] for pair in sorted_pairs])
    vals = [pair[1] for pair in sorted_pairs]
    return pd.Series(vals, index=idx, name="dividend_per_share")

def _build_zero_dividends_series_for_recent_years(
    as_of_timestamp: pd.Timestamp,
    number_of_calendar_years: int = 10,
    quarterly_payment_months: List[int] = [2, 5, 8, 11],
    day_of_month: int = 15,
) -> pd.Series:
    latest_calendar_year = int(pd.Timestamp(as_of_timestamp).year)
    earliest_calendar_year = latest_calendar_year - (int(number_of_calendar_years) - 1)

    payment_datetimes = []
    payment_values = []

    for year in range(earliest_calendar_year, latest_calendar_year + 1):
        for month in quarterly_payment_months:
            payment_datetimes.append(pd.Timestamp(year=year, month=month, day=day_of_month))
            payment_values.append(0.0)

    payment_index = pd.DatetimeIndex(sorted(payment_datetimes))
    zero_dividends_series = pd.Series(payment_values, index=payment_index, dtype=float)
    zero_dividends_series.name = "Dividends"
    return zero_dividends_series

# -----------------------------
# News & officers (yfinance)
# -----------------------------

def _to_iso_date_str(dt_like) -> str:
    if dt_like is None:
        return ""
    if isinstance(dt_like, date):
        return dt_like.isoformat()
    if isinstance(dt_like, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(dt_like)).date().isoformat()
        except Exception:
            return ""
    s = str(dt_like)
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S%Z"):
        try:
            return datetime.strptime(s[:19], fmt).date().isoformat()
        except Exception:
            pass
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return s

def _coerce_float(x):
    try:
        return None if x is None or (isinstance(x, float) and pd.isna(x)) else float(x)
    except Exception:
        return None

def _extract_news(t: pd.DataFrame) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
    """
    Return list of (published_iso, title, summary, url)
    - URL is taken from canonicalUrl ONLY (dict or string). previewUrl is ignored.
    - Handles both top-level and nested `content` dicts.
    """
    def _canon_url(value) -> Optional[str]:
        # canonicalUrl can be a dict like {"url": "..."} or a plain string
        if isinstance(value, dict):
            return value.get("url")
        if isinstance(value, str):
            return value
        return None

    rows: List[Tuple[str, str, Optional[str], Optional[str]]] = []

    news_list = getattr(t, "news", None)
    if not news_list:
        return rows

    for news in news_list:
        try:
            n = news.get("content", {}) if isinstance(news, dict) else {}
            # Base fields
            title = n.get("title") or n.get("headline")
            url = _canon_url(n.get("canonicalUrl"))
            pub = n.get("providerPublishTime") or n.get("published") or n.get("pubDate")
            summary = n.get("summary")

            # Some feeds wrap again under "content"
            if not title and isinstance(n.get("content"), dict):
                c = n["content"]
                title = c.get("title")
                # Only canonicalUrl; ignore previewUrl entirely
                url = _canon_url(c.get("canonicalUrl")) or url
                pub = c.get("pubDate") or pub
                summary = c.get("summary") or summary

            if not title:
                continue

            pub_iso = _to_iso_date_str(pub) if pub else ""
            rows.append((pub_iso, str(title), (None if summary is None else str(summary)), (None if url is None else str(url))))
        except Exception:
            # Skip malformed item, keep going
            continue

    # Sort newest first (ISO strings sort correctly)
    try:
        rows.sort(key=lambda r: r[0], reverse=True)
    except Exception:
        pass

    return rows


def _extract_officers(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    officers = info.get("companyOfficers") or []
    for o in officers:
        out.append({
            "name": o.get("name"),
            "title": o.get("title"),
            "age": o.get("age"),
            "total_pay": _coerce_float(o.get("totalPay")),
            "unexercised_value": _coerce_float(o.get("unexercisedValue")),
        })
    return out

# -----------------------------
# Stateless helpers extracted from core/stock.py
# -----------------------------

def _select_close_volume(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure we return a DataFrame with 'Close' and 'Volume' columns.
    """
    if not isinstance(prices, pd.DataFrame) or prices.empty:
        return pd.DataFrame(columns=["Close", "Volume"])
    out = pd.DataFrame(index=prices.index.copy())
    out["Close"] = prices["Close"] if "Close" in prices.columns else np.nan
    out["Volume"] = prices["Volume"] if "Volume" in prices.columns else np.nan
    return out


def _coerce_datetime_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    - Coerce columns to DatetimeIndex, keep only valid ones
    - Sort columns latest -> older
    """
    if not isinstance(dataframe, pd.DataFrame) or dataframe.empty:
        return pd.DataFrame()
    columns_as_datetime = pd.to_datetime(dataframe.columns, errors="coerce")
    valid_mask = ~pd.isna(columns_as_datetime)
    coerced = dataframe.loc[:, valid_mask].copy()
    coerced.columns = columns_as_datetime[valid_mask]
    coerced = coerced.sort_index(axis=1, ascending=False)
    return coerced


def _zeros_like_series(columns: pd.Index, name: str) -> pd.Series:
    return pd.Series(0.0, index=columns, name=name)


def _ensure_list(v) -> List[str]:
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return list(v)
    return [str(v)]


def get_current_timestamp(as_of: Optional[date]) -> pd.Timestamp:
    """
    Convert a date (or None -> today UTC) to a midnight timestamp.
    """
    if as_of is None:
        d = datetime.now(timezone.utc).date()
    else:
        d = as_of
    return pd.Timestamp(d.year, d.month, d.day, 0, 0, 0)


def _dates_within(d1: Optional[pd.Timestamp], d2: Optional[pd.Timestamp], tol_days: int) -> bool:
    if d1 is None or d2 is None:
        return False
    return abs((d1.normalize() - d2.normalize()).days) <= max(tol_days, 0)


def _infer_reporting_interval_days(quarterly_balance_sheet: pd.DataFrame) -> int:
    """
    Infer median spacing between quarterly columns in days.
    """
    qdf = _coerce_datetime_columns(quarterly_balance_sheet)
    if qdf.shape[1] < 2:
        return 90
    dates = qdf.columns.sort_values(ascending=False)
    diffs = dates.to_series().diff(-1).dropna().abs().dt.days
    if diffs.empty:
        return 90
    return max(int(float(diffs.median())), 1)


def _k_for_reporting_frequency(quarterly_balance_sheet: pd.DataFrame, cutoff_days: int) -> int:
    """
    Return 4 for quarterly reporters, 2 for semiannual (based on inferred interval).
    """
    return 4 if _infer_reporting_interval_days(quarterly_balance_sheet) < cutoff_days else 2


def _latest_quarter_end(quarterly_balance_sheet: pd.DataFrame) -> Optional[pd.Timestamp]:
    qdf = _coerce_datetime_columns(quarterly_balance_sheet)
    if qdf.shape[1] == 0:
        return None
    return qdf.columns[0]


def is_balance_sheet_stale(
    quarterly_balance_sheet: pd.DataFrame,
    asof: Optional[date],
    tolerance_days: int,
) -> bool:
    """
    Compare latest quarter end vs as-of date using inferred reporting interval.
    """
    if asof is None:
        asof = datetime.now(timezone.utc).date()
    latest_q = _latest_quarter_end(quarterly_balance_sheet)
    if latest_q is None:
        return False
    gap = (pd.Timestamp(asof) - latest_q.normalize()).days
    interval = _infer_reporting_interval_days(quarterly_balance_sheet)
    return gap >= max(interval - tolerance_days, 1)


def _safe_statement_init(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize statement frames:
    - Coerce columns to DatetimeIndex, sorted latest->older (delegated to _coerce_datetime_columns).
    - If the last column has >50% NA/NaN, drop that last column (only if there are at least 2 columns).
    - Fill missing values with zeros.
    """
    if not isinstance(dataframe, pd.DataFrame) or dataframe.empty:
        return pd.DataFrame()

    df = _coerce_datetime_columns(dataframe)

    # Decide on dropping AFTER coercion/sorting, and BEFORE fillna
    if df.shape[1] >= 2:
        last_col = df.columns[-1]
        na_ratio = df[last_col].isna().mean()  # counts both <NA> and NaN
        if float(na_ratio) > 0.5:
            df = df.iloc[:, :-1]

    return df.fillna(0)


# -----------------------------
# World Bank year/value → Series
# -----------------------------

def _convert_year_value_list_to_series(
    indicator_key: str,
    year_value_list: List[Tuple[int, Optional[float]]],
    maximum_points: Optional[int] = None,
) -> pd.Series:
    """
    Convert a list of (year, value) tuples to a Series:
    - index: years as integers, ordered latest → older
    - values: floats (NaN preserved)
    - name: indicator_key
    """
    if not year_value_list:
        return pd.Series(dtype=float, name=indicator_key)

    sorted_pairs_desc = sorted(year_value_list, key=lambda p: p[0], reverse=True)
    if maximum_points is not None and maximum_points > 0:
        sorted_pairs_desc = sorted_pairs_desc[:maximum_points]

    years_desc = [int(y) for (y, _) in sorted_pairs_desc]
    values_desc = [np.nan if v is None else float(v) for (_, v) in sorted_pairs_desc]
    return pd.Series(values_desc, index=pd.Index(years_desc), name=indicator_key)


