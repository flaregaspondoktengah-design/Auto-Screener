# BSJP : Bullish Divergence Screener - Live Screening Module

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']

# --- Helper Functions ---
def apply_fraksi_harga(price):
    if price is None or pd.isna(price):
        return np.nan
    price = float(price)
    if price < 200:
        return np.ceil(price / 1) * 1
    elif 200 <= price <= 500:
        return np.ceil(price / 2) * 2
    elif 500 < price <= 2000:
        return np.ceil(price / 5) * 5
    elif 2000 < price <= 5000:
        return np.ceil(price / 10) * 10
    elif price > 5000:
        return np.ceil(price / 25) * 25
    return price

def get_mintick(price):
    price = float(price)
    if price < 200: return 1
    elif 200 <= price <= 500: return 2
    elif 500 < price <= 2000: return 5
    elif 2000 < price <= 5000: return 10
    else: return 25

# --- Main Screener Function ---
def run_bullish_divergence_screener(df, ticker_item, target_date=None):
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    if df is None:
        if ticker_item is None:
            return None
        df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=False, progress=False)

    if df.empty:
        return None

    df_copy = df.copy()
    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return None

    if len(df_copy) < 50:
        return None
    
    df_copy = df_copy[df_copy.index.date <= target_date]
    if len(df_copy) < 50:
        return None

    latest = df_copy.iloc[-1]
    prev = df_copy.iloc[-2]
    current_price = float(latest['Close'])

    low_today = float(latest['Low'])
    low_yesterday = float(prev['Low'])
    high_today = float(latest['High'])
    close_today = float(latest['Close'])
    
    # KRITERIA 1: Low hari ini < Low kemarin (Membuat Lower Low)
    if not (low_today < low_yesterday):
        return None
        
    # KRITERIA 2: Close hari ini harus berada di setengah atas bar (Upper Half)
    if not (close_today >= ((high_today + low_today) / 2.0)):
        return None

    # Hitung Harga Buy dan Stop Loss berdasarkan bar hari ini
    tick = get_mintick(current_price)
    buy_price = high_today + tick
    sl_price = low_today - tick
    
    prev_close = float(df_copy['Close'].iloc[-2]) if len(df_copy) > 1 else current_price
    pct_change_vs_pc = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0

    return {
        'Date': latest.name.strftime('%d/%m/%Y'),
        'Tickers': ticker_item.replace('.JK', ''),
        'Price': f"{apply_fraksi_harga(current_price):,.0f}",
        'Low Today': f"{apply_fraksi_harga(low_today):,.0f}",
        'Low Yesterday': f"{apply_fraksi_harga(low_yesterday):,.0f}",
        'Buy Price': f"{apply_fraksi_harga(buy_price):,.0f}",
        'SL Price': f"{apply_fraksi_harga(sl_price):,.0f}",
        '%C vs PC': f"{pct_change_vs_pc:+.2f}%"
    }

def run_full_screener():
    results = []
    print("Starting Bullish Divergence Screener...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=False, progress=False)
            if df.empty or len(df) < 50:
                continue
            screener_output = run_bullish_divergence_screener(df.copy(), ticker_item)
            if screener_output:
                results.append(screener_output)
        except Exception:
            pass
            
    print("Screener finished.")
    if results:
        return pd.DataFrame(results)
    return None