# BSJP : Backtest BB Reversal - Historical Trade Analysis Module
# Module ini berisi fungsi-fungsi untuk menganalisis historical trades berdasarkan strategi BB Reversal

import yfinance as yf
import pandas as pd
import numpy as np
from screener_bb_reversal import calculate_moving_averages_bb, tickers

# --- Strategy Parameters ---
HIGH_TARGET_PCT = 1.36    # Target profit jika high tercapai
CLOSE_TARGET_PCT = 0.36   # Target profit jika close tercapai


# --- Backtest Function for Detailed Trade Analysis (BB Reversal) ---
def backtest_bb_reversal_strategy(df, min_gain_pct=HIGH_TARGET_PCT, close_target_pct=CLOSE_TARGET_PCT):
    """
    Simulasi trades berdasarkan buy signal BB Reversal.
    
    Exit Strategy:
    - Jika Open besok >= target high (1.36%): Profit = pct_next_open (Gap Up)
    - Jika High besok >= target high (1.36%): Profit = max(1.36%, pct_next_close)
    - Jika Close besok >= target close (0.36%): Profit = pct_next_close
    - Jika tidak: Profit = pct_next_close (bisa negatif)
    
    Kriteria BB Reversal:
    - Volume Up
    - Close Up
    - Current Day Green Candle
    - Value > 1B
    - Prev Day Red Candle
    - Close > Lower Band
    - Prev Close < Prev Lower Band
    - Price >= 100
    """
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return [], []

    try:
        df_copy = calculate_moving_averages_bb(df_copy)
    except ValueError:
        return [], []

    df_copy['Volume_MA_20'] = df_copy['Volume'].rolling(window=20).mean()
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5', 'Lower_Band'])

    if len(df_copy) < 200 + 2:
        return [], []

    detailed_trades = []
    profits_list = []

    for i in range(1, len(df_copy) - 1):
        signal_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i - 1]
        next_day = df_copy.iloc[i + 1]

        # Kriteria BB Reversal
        cond_volume_up = signal_day['Volume'] > prev_day['Volume']
        cond_close_up = signal_day['Close'] > prev_day['Close']
        cond_current_day_green_candle = signal_day['Close'] > signal_day['Open']
        cond_high_value = (signal_day['Close'] * signal_day['Volume']) / 1_000_000_000 > 1
        cond_prev_red_candle = prev_day['Close'] < prev_day['Open']
        cond_close_above_bb_lower = signal_day['Close'] > signal_day['Lower_Band']
        cond_prev_close_below_prev_bb_lower = prev_day['Close'] < prev_day['Lower_Band']

        if (cond_volume_up and cond_close_up and cond_current_day_green_candle and signal_day['Close'] >= 100 and
            cond_close_above_bb_lower and cond_prev_close_below_prev_bb_lower and cond_high_value and cond_prev_red_candle):

            entry_date = signal_day.name.strftime('%d-%m-%Y')
            entry_price = float(signal_day['Close'])
            target_high_price = entry_price * (1 + min_gain_pct / 100)
            target_close_price = entry_price * (1 + close_target_pct / 100)

            next_day_open = float(next_day['Open'])
            high_next_day = float(next_day['High'])
            low_next_day = float(next_day['Low'])
            close_next_day = float(next_day['Close'])

            # Calculate percentages
            pct_next_day_open = ((next_day_open - entry_price) / entry_price) * 100
            pct_next_day_high = ((high_next_day - entry_price) / entry_price) * 100
            pct_next_day_low = ((low_next_day - entry_price) / entry_price) * 100
            pct_next_day_close = ((close_next_day - entry_price) / entry_price) * 100

            # ==========================================
            # EXIT LOGIC & PROFIT CALCULATION
            # ==========================================
            profit_pct = pct_next_day_close  # default: actual close
            outcome = "Closed"

            if next_day_open >= target_high_price:
                # Gap up beyond target - profit adalah actual open percentage
                profit_pct = pct_next_day_open
                outcome = "Gap Up"
            elif high_next_day >= target_high_price:
                # Target high tercapai - profit minimal 1.36%, atau actual close jika lebih tinggi
                profit_pct = max(min_gain_pct, pct_next_day_close)
                outcome = "Target H"
            elif close_next_day >= target_close_price:
                # Target close tercapai
                outcome = "Target C"
            else:
                # Tidak ada target tercapai
                outcome = "Miss"

            profits_list.append(profit_pct)

            # Remarks
            cond_vol_above_ma20 = signal_day['Volume'] > signal_day['Volume_MA_20']
            cond_open_equal_prev_close = signal_day['Open'] == prev_day['Close']
            cond_low_greater_prev_low = signal_day['Low'] > prev_day['Low']
            cond_high_greater_prev_high = signal_day['High'] > prev_day['High']
            cond_ma_uptrend = (
                signal_day['MA5'] > signal_day['MA10'] and
                signal_day['MA10'] > signal_day['MA20'] and
                signal_day['MA20'] > signal_day['MA50'] and
                signal_day['MA50'] > signal_day['MA200']
            )
            cond_open_low_greater_high_close = (signal_day['Open'] - signal_day['Low']) > (signal_day['High'] - signal_day['Close'])
            cond_close_above_vwap = signal_day['Close'] > signal_day['VWAP_Daily']
            cond_prev_close_below_prev_vwap = prev_day['Close'] < prev_day['VWAP_Daily']
            cond_vol_above_ma5 = signal_day['Volume'] > signal_day['Volume_MA_5']

            close_pct_change_today = ((signal_day['Close'] - prev_day['Close']) / prev_day['Close']) * 100

            detailed_trades.append({
                'Date': entry_date,
                'Price': f"{round(entry_price):,.0f}",
                'LB': f"{round(signal_day['Lower_Band']):,.0f}" if pd.notna(signal_day['Lower_Band']) else "",
                '%H': f"{round(pct_next_day_high, 2):.2f}%",
                '%C': f"{round(pct_next_day_close, 2):.2f}%",
                '%O': f"{round(pct_next_day_open, 2):.2f}%",
                '%L': f"{round(pct_next_day_low, 2):.2f}%",
                'Result': f"{profit_pct:.2f}%",
                'Outcome': outcome,
                '1. PR': "☑" if cond_prev_red_candle else "",
                '2. V>MA20': "☑" if cond_vol_above_ma20 else "",
                '3. MA+': "☑" if cond_ma_uptrend else "",
                '4. L>PL': "☑" if cond_low_greater_prev_low else "",
                '5. H>PH': "☑" if cond_high_greater_prev_high else "",
                '6. O=PC': "☑" if cond_open_equal_prev_close else "",
                '7. OL>HC': "☑" if cond_open_low_greater_high_close else "",
                '%C vs PC': f"{close_pct_change_today:.2f}%",
                '8. C>VWAP': "☑" if cond_close_above_vwap else "",
                '9. PC<PVWAP': "☑" if cond_prev_close_below_prev_vwap else "",
                '10. V>MA5': "☑" if cond_vol_above_ma5 else ""
            })

    return detailed_trades, profits_list


def run_backtest_bb_reversal_for_ticker(ticker_symbol, period="5y"):
    """
    Menjalankan backtest BB Reversal untuk ticker tertentu dan mengembalikan DataFrame hasil.
    """
    if not ticker_symbol.upper().endswith('.JK'):
        ticker_symbol = ticker_symbol.upper() + '.JK'

    try:
        df = yf.download(ticker_symbol, period=period, interval="1d", auto_adjust=True, progress=False)

        if df.empty:
            return None, None

        detailed_trades, profits_list = backtest_bb_reversal_strategy(df.copy())

        if not detailed_trades:
            return None, None

        df_trades = pd.DataFrame(detailed_trades)
        df_trades['Date'] = pd.to_datetime(df_trades['Date'])
        df_trades = df_trades.sort_values(by='Date', ascending=False).reset_index(drop=True)
        df_trades['Date'] = df_trades['Date'].dt.strftime('%d/%m/%Y')

        # Calculate summary statistics dari profits_list
        total_trades = len(detailed_trades)
        winning_trades = sum(1 for p in profits_list if p > 0)
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
        avg_profit_loss = sum(profits_list) / total_trades if total_trades > 0 else 0.0

        summary = {
            'ticker': ticker_symbol.replace('.JK', ''),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_profit_loss': avg_profit_loss
        }

        display_cols = [
            'Date', 'Price', 'LB', '%C vs PC', '%H', '%C', '%O', '%L', 'Result', 'Outcome',
            '1. PR', '2. V>MA20', '3. MA+', '4. L>PL', '5. H>PH',
            '6. O=PC', '7. OL>HC', '8. C>VWAP', '9. PC<PVWAP', '10. V>MA5'
        ]
        df_display = df_trades[display_cols]

        return df_display, summary

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None, None


def get_ticker_list():
    """Mengembalikan list ticker yang tersedia untuk backtest."""
    return [t.replace('.JK', '') for t in tickers]
