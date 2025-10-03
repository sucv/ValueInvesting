# utils/world_bank.py
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlencode

WB_BASE = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

@dataclass(frozen=True)
class _Key:
    country: str
    indicator: str
    mrv: int

class _HttpWBClient:
    """
    Minimal, dependency-free World Bank client using urllib.
    - Fetches only the latest MRV years.
    - Caches responses per (country, indicator, mrv) in-memory.
    Returns a list of (year:int, value:float|None) sorted ASC by year.
    """
    def __init__(self, timeout: float = 15.0, retries: int = 2, backoff: float = 0.6):
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._cache: Dict[_Key, List[Tuple[int, Optional[float]]]] = {}

    def get_series(self, country_iso3: str, indicator: str, mrv: int = 5) -> List[Tuple[int, Optional[float]]]:
        key = _Key(country_iso3.upper(), indicator, max(1, int(mrv)))
        if key in self._cache:
            return self._cache[key]

        url = WB_BASE.format(country=key.country, indicator=key.indicator)
        params = {"MRV": key.mrv, "format": "json"}
        full_url = f"{url}?{urlencode(params)}"

        last_err = None
        for attempt in range(self.retries + 1):
            try:
                req = urllib.request.Request(full_url, headers={"User-Agent": "stocks-vi/1.0"})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8", errors="ignore")
                data = json.loads(raw)
                if not isinstance(data, list) or len(data) < 2 or not isinstance(data[1], list):
                    self._cache[key] = []
                    return []
                rows: List[Tuple[int, Optional[float]]] = []
                for d in data[1]:
                    try:
                        year = int(d.get("date"))
                    except Exception:
                        continue
                    val = d.get("value")
                    v = None if (val is None) else float(val)
                    rows.append((year, v))
                rows.sort(key=lambda t: t[0])  # ASC
                self._cache[key] = rows
                return rows
            except Exception as e:
                last_err = e
                if attempt < self.retries:
                    time.sleep(self.backoff * (attempt + 1))
                else:
                    self._cache[key] = []
                    return []

_client = _HttpWBClient()

def wb_client(country_iso3: str, indicators: List[str], mrv: int = 5) -> Dict[str, List[Tuple[int, Optional[float]]]]:
    """
    One-shot multi-indicator fetch.
    Returns dict: { indicator_code: [(year:int, value:float|None), ... ASC] }
    """
    out: Dict[str, List[Tuple[int, Optional[float]]]] = {}
    for code in indicators:
        out[code] = _client.get_series(country_iso3, code, mrv=max(1, int(mrv)))
    return out
