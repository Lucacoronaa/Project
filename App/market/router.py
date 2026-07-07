"""
Endpoint FastAPI per l'analisi di mercato Forex.

  GET /market/analyze?pair=EUR/USD          -> segnale attuale + indicatori
  GET /market/backtest?pair=EUR/USD         -> statistiche della strategia sul passato
  GET /market/candles?pair=EUR/USD&limit=50 -> ultime candele grezze (per un grafico)

I dati arrivano da Yahoo Finance (yfinance), gratis e senza chiave API.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from .backtest import run_backtest
from .data import get_candles
from .strategy import latest_signal

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/analyze")
def analyze(
    pair: str = Query("EUR/USD", description="Coppia Forex, es. EUR/USD"),
    period: str = Query("6mo", description="Storico da scaricare, es. 1mo/6mo/1y"),
    interval: str = Query("1h", description="Granularita' candele, es. 15m/1h/1d"),
):
    try:
        df = get_candles(pair, period=period, interval=interval)
        result = latest_signal(df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"pair": pair, "interval": interval, **result}


@router.get("/backtest")
def backtest(
    pair: str = Query("EUR/USD", description="Coppia Forex, es. EUR/USD"),
    period: str = Query("1y", description="Storico da scaricare, es. 6mo/1y/2y"),
    interval: str = Query("1h", description="Granularita' candele, es. 1h/1d"),
):
    try:
        df = get_candles(pair, period=period, interval=interval)
        result = run_backtest(df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"pair": pair, "period": period, "interval": interval, **result}


@router.get("/candles")
def candles(
    pair: str = Query("EUR/USD", description="Coppia Forex, es. EUR/USD"),
    period: str = Query("1mo"),
    interval: str = Query("1h"),
    limit: int = Query(50, ge=1, le=500),
):
    try:
        df = get_candles(pair, period=period, interval=interval).tail(limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "pair": pair,
        "interval": interval,
        "candles": [
            {"datetime": str(idx), **{k: round(float(v), 5) for k, v in row.items()}}
            for idx, row in df.iterrows()
        ],
    }
