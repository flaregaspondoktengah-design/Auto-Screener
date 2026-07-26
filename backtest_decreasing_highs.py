# BSJP : Backtest Decreasing Highs - Historical Trade Analysis Module
# Module ini berisi fungsi-fungsi untuk menganalisis historical trades berdasarkan strategi Decreasing Highs

import yfinance as yf
import pandas as pd
import numpy as np
from screener_decreasing_highs import tickers, apply_fraksi_harga

# --- Strategy Parameters ---
HIGH_TARGET_PCT = 1.36    # Target profit jika high tercapai
CLOSE_TARGET_PCT = 0.36   # Target profit jika close tercapai


# --- Backtest Function for Detailed Trade Analysis ---
def backtest_decreasing_highs_strategy(df, min_gain_pct=HIGH_TARGET_PCT, close_target_pct=CLOSE_TARGET_PCT):
    """
    Simulasi trades berdasarkan buy signal Decreasing Highs.
    
    Exit Strategy:
    - Jika Open besok >= target high (1.36%): Profit = pct_next_open (Gap Up)
    - Jika High besok >= target high (1.36%): Profit = max(1.36%, pct_next_close)
    - Jika Close besok >= target close (0.36%): Profit = pct_next_close
    - Jika tidak: Profit = pct_next_close (bisa negatif)
    
    Kriteria:
    1. Price >= 100
    2. Transaction Value >= 5 Billion
    3. High Today < High Yesterday
    4. High Yesterday < High Day Before Yesterday
    5. High Day Before Yesterday < High Two Days Ago
    6. High Two Days Ago < High Three Days Ago
    """
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return [], []

    # Need at least 5 data points for 4 days of decreasing highs
    if len(df_copy) < 5 + 1:
        return [], []

    detailed_trades = []
    profits_list = []

    for i in range(4, len(df_copy) - 1):
        signal_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i - 1]
        day_before_prev = df_copy.iloc[i - 2]
        two_days_ago = df_copy.iloc[i - 3]
        three_days_ago = df_copy.iloc[i - 4]
        next_day = df_copy.iloc[i + 1]

        current_price = float(signal_day['Close'])
        latest_volume = float(signal_day['Volume'])
        transaction_value_billion = (current_price * latest_volume) / 1_000_000_000

        high_today = float(signal_day['High'])
        high_yesterday = float(prev_day['High'])
        high_day_before_yesterday = float(day_before_prev['High'])
        high_two_days_ago = float(two_days_ago['High'])
        high_three_days_ago = float(three_days_ago['High'])

        # Kriteria Decreasing Highs
        cond_price_above_100 = current_price >= 100
        cond_high_transaction_value = transaction_value_billion >= 5
        cond_decreasing_high_today = high_today < high_yesterday
        cond_decreasing_high_yesterday = high_yesterday < high_day_before_yesterday
        cond_decreasing_high_two_days_ago = high_day_before_yesterday < high_two_days_ago
        cond_decreasing_high_three_days_ago = high_two_days_ago < high_three_days_ago

        if (cond_price_above_100 and
            cond_high_transaction_value and
            cond_decreasing_high_today and
            cond_decreasing_high_yesterday and
            cond_decreasing_high_two_days_ago and
            cond_decreasing_high_three_days_ago):

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

            # Remarks conditions
            latest_open = float(signal_day['Open'])
            latest_low = float(signal_day['Low'])
            prev_close = float(prev_day['Close'])
            prev_open = float(prev_day['Open'])
            prev_low = float(prev_day['Low'])

            cond_prev_red = prev_close < prev_open
            cond_low_gt_prev_low = latest_low > prev_low
            cond_close_gt_open = current_price > latest_open

            close_pct_change_today = ((current_price - prev_close) / prev_close) * 100

            detailed_trades.append({
                'Date': entry_date,
                'Price': f"{round(entry_price):,.0f}",
                '%H': f"{round(pct_next_day_high, 2):.2f}%",
                '%C': f"{round(pct_next_day_close, 2):.2f}%",
                '%O': f"{round(pct_next_day_open, 2):.2f}%",
                '%L': f"{round(pct_next_day_low, 2):.2f}%",
                'Result': f"{profit_pct:.2f}%",
                'Outcome': outcome,
                'H Today': f"{apply_fraksi_harga(high_today):,.0f}",
                'H Prev': f"{apply_fraksi_harga(high_yesterday):,.0f}",
                'H 2D': f"{apply_fraksi_harga(high_day_before_yesterday):,.0f}",
                'H 3D': f"{apply_fraksi_harga(high_two_days_ago):,.0f}",
                'H 4D': f"{apply_fraksi_harga(high_three_days_ago):,.0f}",
                '1. H<Prev': "☑" if cond_decreasing_high_today else "",
                '2. Prev<H-2': "☑" if cond_decreasing_high_yesterday else "",
                '3. H-2<H-3': "☑" if cond_decreasing_high_two_days_ago else "",
                '4. H-3<H-4': "☑" if cond_decreasing_high_three_days_ago else "",
                '5. PrevRed': "☑" if cond_prev_red else "",
                '6. L>PL': "☑" if cond_low_gt_prev_low else "",
                '7. Green': "☑" if cond_close_gt_open else "",
                '%C vs PC': f"{close_pct_change_today:.2f}%"
            })

    return detailed_trades, profits_list


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

        detailed_trades, profits_list = backtest_decreasing_highs_strategy(df.copy())

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
            'Date', 'Price', '%C vs PC', '%H', '%C', '%O', '%L', 'Result', 'Outcome',
            'H Today', 'H Prev', 'H 2D', 'H 3D', 'H 4D',
            '1. H<Prev', '2. Prev<H-2', '3. H-2<H-3', '4. H-3<H-4',
            '5. PrevRed', '6. L>PL', '7. Green'
        ]
        df_display = df_trades[display_cols]

        return df_display, summary

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None, None


def get_ticker_list():
    """Mengembalikan list ticker yang tersedia untuk backtest."""
    return [t.replace('.JK', '') for t in tickers]
