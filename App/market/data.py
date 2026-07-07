"""
Scarica le candele storiche (OHLCV) per una coppia Forex.

Usa yfinance (Yahoo Finance): gratis, senza chiave API.
I ticker Forex su Yahoo hanno il formato "EURUSD=X", "GBPUSD=X", ecc.
"""
from __future__ import annotations

import pandas as pd
import yfinance as yf


def to_yahoo_symbol(pair: str) -> str:
    """
    Converte una coppia in stile "EUR/USD" o "EURUSD" nel ticker Yahoo "EURUSD=X".
    Se l'utente passa gia' un ticker con "=X" lo lascia invariato.
    """
    pair = pair.strip().upper()
    if pair.endswith("=X"):
        return pair
    pair = pair.replace("/", "").replace("-", "").replace(" ", "")
    return f"{pair}=X"


def get_candles(pair: str, period: str = "6mo", interval: str = "1h") -> pd.DataFrame:
    """
    Restituisce un DataFrame con le candele OHLCV.

    period:   quanto storico scaricare (es. "1mo", "6mo", "1y", "2y").
    interval: granularita' delle candele (es. "15m", "1h", "1d").
              NB: Yahoo limita gli intervalli intraday a storici brevi
              (es. "1h" -> max ~2 anni, "15m" -> ~60 giorni).

    Colonne restituite: open, high, low, close, volume  (indice = data/ora).
    """
    symbol = to_yahoo_symbol(pair)
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError(
            f"Nessun dato ricevuto per '{pair}' (ticker Yahoo '{symbol}'). "
            f"Controlla la coppia oppure riduci l'intervallo/periodo."
        )

    # yfinance a volte restituisce colonne multi-livello: le appiattiamo.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df.index.name = "datetime"
    return df
