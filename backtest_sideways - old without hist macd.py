# BSJP : Backtest Sideways Swing - Historical Trade Analysis Module
# Module ini berisi fungsi-fungsi untuk menganalisis historical trades 
# berdasarkan strategi sideways swing (saham yang sedang sideways)

import yfinance as yf
import pandas as pd
import numpy as np
from screener_sideways import (
    tickers, apply_fraksi_harga, MA_CLUSTER_TOLERANCE, SWING_DAYS,
    is_ma_clustered, get_ma_position
)


# --- Backtest Strategy Parameters ---
DEFAULT_HOLDING_DAYS = 5  # Default holding period for swing trade


def backtest_sideways_strategy(df, holding_days=DEFAULT_HOLDING_DAYS):
    """
    Simulasi trades berdasarkan strategi sideways swing.
    
    Entry Criteria:
    1. MA5, MA10, MA20 clustered (sideways)
    2. Price >= 100
    3. Value >= 1 billion
    
    Exit Criteria:
    1. Max holding days reached
    2. Trail stop: Close below MA20 (after 2 days)
    """
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return []

    if len(df_copy) < 50:
        return []

    # Calculate MA for clustering check
    df_copy['MA5'] = df_copy['Close'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['Close'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['Close'].rolling(window=20).mean()

    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20'])

    if len(df_copy) < 30:
        return []

    detailed_trades = []

    for i in range(20, len(df_copy) - holding_days):
        signal_day = df_copy.iloc[i]
        
        current_price = float(signal_day['Close'])
        latest_volume = float(signal_day['Volume'])
        transaction_value_billion = (current_price * latest_volume) / 1_000_000_000

        # Basic filters
        if current_price < 100 or transaction_value_billion < 1:
            continue

        # Get MA values
        ma5 = float(signal_day['MA5'])
        ma10 = float(signal_day['MA10'])
        ma20 = float(signal_day['MA20'])

        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
            continue

        # Check MA clustering (sideways)
        if not is_ma_clustered(ma5, ma10, ma20, current_price):
            continue

        # Get MA position
        ma_position = get_ma_position(ma5, ma10, ma20, current_price)
        
        # Calculate MA spread
        ma_values = [ma5, ma10, ma20]
        ma_spread_pct = (max(ma_values) - min(ma_values)) / current_price * 100

        # Trade parameters
        entry_date = signal_day.name.strftime('%d-%m-%Y')
        entry_price = current_price

        # Simulate trade - look forward for exit
        trade_result = None
        actual_holding = 0
        exit_price = entry_price
        exit_reason = 'MAX_DAYS'
        
        for j in range(i + 1, min(i + 1 + holding_days, len(df_copy))):
            actual_holding = j - i
            future_day = df_copy.iloc[j]
            future_close = float(future_day['Close'])
            future_ma20 = float(future_day['MA20'])

            # Trail stop: Close below MA20 (exit early)
            if future_close < future_ma20 and actual_holding >= 2:
                trade_result = ((future_close - entry_price) / entry_price) * 100
                exit_price = future_close
                exit_reason = 'TRAIL_STOP'
                break

            # Max holding days reached
            if actual_holding >= holding_days:
                trade_result = ((future_close - entry_price) / entry_price) * 100
                exit_price = future_close
                exit_reason = 'MAX_DAYS'
                break

        if trade_result is not None:
            detailed_trades.append({
                'Date': entry_date,
                'Price': f"{round(entry_price):,.0f}",
                'Entry': f"{apply_fraksi_harga(entry_price):,.0f}",
                'Exit': f"{apply_fraksi_harga(exit_price):,.0f}",
                '%P/L': f"{round(trade_result, 2):.2f}%",
                'Days': str(actual_holding),
                'Exit Type': exit_reason,
                'MA5': f"{apply_fraksi_harga(ma5):,.0f}",
                'MA10': f"{apply_fraksi_harga(ma10):,.0f}",
                'MA20': f"{apply_fraksi_harga(ma20):,.0f}",
                'Spread%': f"{ma_spread_pct:.2f}%",
                'Position': ma_position,
                '1. Side': "☑"
            })

    return detailed_trades


def run_backtest_for_ticker(ticker_symbol, period="5y"):
    """
    Menjalankan backtest untuk ticker tertentu dan mengembalikan DataFrame hasil.
    """
    if not ticker_symbol.upper().endswith('.JK'):
        ticker_symbol = ticker_symbol.upper() + '.JK'

    try:
        df = yf.download(ticker_symbol, period=period, interval="1d", auto_adjust=True, progress=False)

        if df.empty:
            return None, None

        detailed_trades = backtest_sideways_strategy(df.copy())

        if not detailed_trades:
            return None, None

        df_trades = pd.DataFrame(detailed_trades)
        df_trades['Date'] = pd.to_datetime(df_trades['Date'])
        df_trades = df_trades.sort_values(by='Date', ascending=False).reset_index(drop=True)
        df_trades['Date'] = df_trades['Date'].dt.strftime('%d/%m/%Y')

        total_trades = len(df_trades)
        
        # Extract numeric P/L
        df_trades['PL_numeric'] = df_trades['%P/L'].str.rstrip('%').astype(float)
        
        # Winning Trade: P/L > 0
        winning_trades = len(df_trades[df_trades['PL_numeric'] > 0])
        win_rate = (winning_trades / total_trades) * 100
        avg_profit_loss = df_trades['PL_numeric'].mean()
        
        # Calculate average holding days
        df_trades['Days_numeric'] = df_trades['Days'].astype(int)
        avg_holding = df_trades['Days_numeric'].mean()

        summary = {
            'ticker': ticker_symbol.replace('.JK', ''),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_profit_loss': avg_profit_loss,
            'avg_holding_days': avg_holding
        }

        display_cols = [
            'Date', 'Price', '%P/L', 'Days', 'Exit Type',
            'Entry', 'Exit',
            'MA5', 'MA10', 'MA20', 'Spread%',
            'Position', '1. Side'
        ]
        
        # Only include columns that exist
        available_cols = [col for col in display_cols if col in df_trades.columns]
        df_display = df_trades[available_cols]

        return df_display, summary

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None, None


def get_ticker_list():
    """Mengembalikan list ticker yang tersedia untuk backtest."""
    return [t.replace('.JK', '') for t in tickers]
