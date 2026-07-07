"""
Backtest semplice della strategia sui dati storici.

Simula di stare "long" quando signal == 1 e "short" quando signal == -1,
entrando/uscendo alla chiusura della candela in cui cambia il segnale.
Serve a misurare se la strategia AVREBBE funzionato in passato — non e' una
garanzia sul futuro, ma e' il minimo indispensabile prima di rischiare denaro.

Limiti volutamente semplici (da migliorare in seguito):
  - niente commissioni/spread
  - posizione sempre a mercato (long o short), size costante
  - esecuzione al prezzo di chiusura
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .strategy import generate_signals


def run_backtest(df: pd.DataFrame) -> dict:
    data = generate_signals(df).dropna().copy()
    if len(data) < 2:
        raise ValueError("Dati insufficienti per il backtest.")

    # Rendimento della candela successiva (in %) applicato alla posizione tenuta.
    data["ret"] = data["close"].pct_change().shift(-1)

    # Posizione = segnale della candela corrente (entriamo alla chiusura).
    data["position"] = data["signal"]
    data["strategy_ret"] = data["position"] * data["ret"]
    data = data.dropna(subset=["strategy_ret"])

    equity = (1 + data["strategy_ret"]).cumprod()
    buy_hold = (1 + data["ret"]).cumprod()

    # Statistiche sulle singole operazioni (blocchi consecutivi con stessa posizione).
    trades = []
    pos = 0
    trade_ret = 1.0
    for _, row in data.iterrows():
        if row["position"] != pos:
            if pos != 0:
                trades.append(trade_ret - 1)
            pos = row["position"]
            trade_ret = 1.0
        if pos != 0:
            trade_ret *= 1 + row["strategy_ret"]
    if pos != 0:
        trades.append(trade_ret - 1)

    trades = [t for t in trades if not np.isnan(t)]
    wins = [t for t in trades if t > 0]

    total_return = float(equity.iloc[-1] - 1) if len(equity) else 0.0
    max_drawdown = float((equity / equity.cummax() - 1).min()) if len(equity) else 0.0

    return {
        "candele_analizzate": int(len(data)),
        "operazioni_totali": len(trades),
        "operazioni_vincenti": len(wins),
        "win_rate_pct": round(100 * len(wins) / len(trades), 2) if trades else 0.0,
        "rendimento_strategia_pct": round(100 * total_return, 2),
        "rendimento_buy_and_hold_pct": round(100 * float(buy_hold.iloc[-1] - 1), 2),
        "max_drawdown_pct": round(100 * max_drawdown, 2),
        "nota": "Senza commissioni/spread. Risultati passati non garantiscono quelli futuri.",
    }
