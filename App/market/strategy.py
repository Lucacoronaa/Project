"""
Strategia: trasforma gli indicatori in un segnale BUY / SELL / HOLD.

Regola di base (trend-following con filtro sul momentum):

  BUY  quando:  EMA veloce sopra EMA lenta  (trend rialzista)
                AND MACD sopra la sua linea di segnale (momentum positivo)
                AND RSI non gia' in ipercomprato (< 70)

  SELL quando:  EMA veloce sotto EMA lenta  (trend ribassista)
                AND MACD sotto la sua linea di segnale (momentum negativo)
                AND RSI non gia' in ipervenduto (> 30)

  HOLD in tutti gli altri casi.

Il "segnale d'ingresso" vero e proprio scatta quando lo stato passa da
HOLD/opposto a BUY (o SELL): e' il momento in cui le condizioni diventano vere.
"""
from __future__ import annotations

import pandas as pd

from .indicators import add_indicators

RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggiunge le colonne:
      - signal:  +1 (BUY), -1 (SELL), 0 (HOLD)  -> lo *stato* a ogni candela
      - entry:   True solo sulla candela in cui lo stato cambia (nuovo ingresso)
    """
    data = add_indicators(df)

    long_cond = (
        (data["ema_fast"] > data["ema_slow"])
        & (data["macd"] > data["macd_signal"])
        & (data["rsi"] < RSI_OVERBOUGHT)
    )
    short_cond = (
        (data["ema_fast"] < data["ema_slow"])
        & (data["macd"] < data["macd_signal"])
        & (data["rsi"] > RSI_OVERSOLD)
    )

    data["signal"] = 0
    data.loc[long_cond, "signal"] = 1
    data.loc[short_cond, "signal"] = -1

    # Un "ingresso" e' quando il segnale cambia rispetto alla candela precedente.
    data["entry"] = data["signal"].ne(data["signal"].shift(1)) & (data["signal"] != 0)
    return data


def _label(signal: int) -> str:
    return {1: "BUY", -1: "SELL", 0: "HOLD"}[int(signal)]


def latest_signal(df: pd.DataFrame) -> dict:
    """
    Restituisce un riepilogo leggibile dell'ULTIMA candela: cosa fare adesso.
    """
    data = generate_signals(df).dropna()
    if data.empty:
        raise ValueError("Dati insufficienti per calcolare gli indicatori.")

    last = data.iloc[-1]
    signal = int(last["signal"])
    atr_val = float(last["atr"])
    price = float(last["close"])

    # Suggerimento di stop loss basato sulla volatilita' (2*ATR).
    if signal == 1:
        stop_loss = round(price - 2 * atr_val, 5)
    elif signal == -1:
        stop_loss = round(price + 2 * atr_val, 5)
    else:
        stop_loss = None

    return {
        "datetime": str(data.index[-1]),
        "price": round(price, 5),
        "signal": _label(signal),
        "is_new_entry": bool(last["entry"]),
        "indicators": {
            "ema_fast": round(float(last["ema_fast"]), 5),
            "ema_slow": round(float(last["ema_slow"]), 5),
            "rsi": round(float(last["rsi"]), 2),
            "macd": round(float(last["macd"]), 6),
            "macd_signal": round(float(last["macd_signal"]), 6),
            "atr": round(atr_val, 6),
        },
        "suggested_stop_loss": stop_loss,
        "nota": "Segnale probabilistico, non un consiglio finanziario. Valuta sempre col backtest.",
    }
