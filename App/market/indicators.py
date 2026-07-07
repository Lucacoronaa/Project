"""
Indicatori tecnici calcolati direttamente con pandas (niente dipendenze extra).

Ogni funzione prende una Series (di solito il prezzo di chiusura) e restituisce
una Series con lo stesso indice, pronta da aggiungere al DataFrame.
"""
from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    """Media mobile esponenziale."""
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    """Media mobile semplice."""
    return series.rolling(window=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (0-100).
    > 70 = ipercomprato (possibile eccesso rialzista),
    < 30 = ipervenduto (possibile eccesso ribassista).
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    MACD: differenza tra due EMA + linea di segnale + istogramma.
    Colonne restituite: macd, macd_signal, macd_hist.
    """
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "macd_signal": signal_line, "macd_hist": hist}
    )


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range: misura la volatilita'.
    Utile per dimensionare gli stop loss (es. stop = entry - 2*ATR).
    Richiede le colonne high, low, close.
    """
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def add_indicators(
    df: pd.DataFrame,
    ema_fast: int = 20,
    ema_slow: int = 50,
    rsi_period: int = 14,
) -> pd.DataFrame:
    """Aggiunge tutti gli indicatori usati dalla strategia al DataFrame."""
    out = df.copy()
    out["ema_fast"] = ema(out["close"], ema_fast)
    out["ema_slow"] = ema(out["close"], ema_slow)
    out["rsi"] = rsi(out["close"], rsi_period)
    out = out.join(macd(out["close"]))
    out["atr"] = atr(out)
    return out
