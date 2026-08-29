# BSJP : Decreasing Highs Screener - Live Screening Module
# Module ini berisi fungsi-fungsi untuk live screening saham Indonesia
# dengan strategi Decreasing Highs (4 hari high menurun berturut-turut)

import yfinance as yf
import pandas as pd
import numpy as np

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']


# --- Helper Functions ---
def apply_fraksi_harga(price):
    """
    Menentukan tick size berdasarkan harga untuk Bursa Efek Indonesia.
    """
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


# --- Backtest Function for Summary Metrics ---
def _calculate_backtest_summary(df, min_gain_pct=1.36, stop_loss_pct=2.0):
    """
    Menghitung metrik ringkasan backtest untuk strategi Decreasing Highs.
    Mengembalikan win rate, average profit/loss, dan total trades.
    """
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}

    # Need at least 5 data points for 4 days of decreasing highs
    if len(df_copy) < 5 + 1:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}

    trade_profits = []

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

            entry_price = current_price
            target_profit_price = entry_price * (1 + min_gain_pct / 100)

            high_next_day = float(next_day['High'])
            close_next_day = float(next_day['Close'])

            if high_next_day >= target_profit_price:
                trade_profits.append(min_gain_pct)
            else:
                trade_profits.append(((close_next_day - entry_price) / entry_price) * 100)

    total_trades_count = len(trade_profits)
    if total_trades_count == 0:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}

    # WR: High >= Target (1.36%) = Winning Trade
    winning_trades_count = sum(1 for pnl in trade_profits if pnl >= min_gain_pct)
    overall_win_rate = (winning_trades_count / total_trades_count) * 100
    overall_avg_profit_loss = sum(trade_profits) / total_trades_count

    return {
        'win_rate': overall_win_rate,
        'avg_profit_loss': overall_avg_profit_loss,
        'total_trades': total_trades_count
    }


# --- Main Decreasing Highs Screener Function (Live Screening) ---
def run_decreasing_highs_screener(df, ticker_item, target_date=None):
    """
    Memeriksa apakah saham memenuhi kriteria Decreasing Highs untuk hari terakhir.
    
    Kriteria:
    1. Price >= 100
    2. Transaction Value >= 5 Billion
    3. High Today < High Yesterday
    4. High Yesterday < High Day Before Yesterday
    5. High Day Before Yesterday < High Two Days Ago
    6. High Two Days Ago < High Three Days Ago
    
    Args:
        df: DataFrame dengan data saham (bisa None)
        ticker_item: Kode ticker saham
        target_date: Tanggal target untuk screening (default: hari ini)
    """
    from datetime import datetime, date
    
    # Set default target_date ke hari ini
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%d-%m-%Y').date()

    if df is None:
        if ticker_item is None:
            return None
        df = yf.download(ticker_item, period="6mo", interval="1d", auto_adjust=True, progress=False)

    if df.empty:
        return None

    df_copy = df.copy()

    # Flatten MultiIndex columns
    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return None

    # Need at least 5 data points for 4 days of decreasing highs
    if len(df_copy) < 5:
        return None
    
    # Filter data sampai target_date
    df_copy = df_copy[df_copy.index.date <= target_date]

    if len(df_copy) < 5:
        return None

    # Get the last 5 bars
    latest_bar = df_copy.iloc[-1]
    prev_bar = df_copy.iloc[-2]
    day_before_prev_bar = df_copy.iloc[-3]
    two_days_ago_bar = df_copy.iloc[-4]
    three_days_ago_bar = df_copy.iloc[-5]

    current_price = float(latest_bar['Close'])
    latest_volume = float(latest_bar['Volume'])
    transaction_value_billion = (current_price * latest_volume) / 1_000_000_000

    high_today = float(latest_bar['High'])
    high_yesterday = float(prev_bar['High'])
    high_day_before_yesterday = float(day_before_prev_bar['High'])
    high_two_days_ago = float(two_days_ago_bar['High'])
    high_three_days_ago = float(three_days_ago_bar['High'])

    # Apply filtering criteria
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

        # Backtest untuk ticker ini
        backtest_df = yf.download(ticker_item, period="5y", interval="1d", auto_adjust=True, progress=False)
        backtest_metrics = _calculate_backtest_summary(backtest_df)

        if backtest_metrics['total_trades'] == 0:
            return None

        # Calculate additional metrics for remarks
        latest_open = float(latest_bar['Open'])
        latest_low = float(latest_bar['Low'])
        prev_close = float(prev_bar['Close'])
        prev_open = float(prev_bar['Open'])
        prev_low = float(prev_bar['Low'])

        # Remarks conditions
        cond_prev_red = prev_close < prev_open
        cond_low_gt_prev_low = latest_low > prev_low
        cond_close_gt_open = current_price > latest_open

        # Calculate percentage change
        pct_change = ((current_price - prev_close) / prev_close) * 100

        return {
            'Date': latest_bar.name.strftime('%d/%m/%Y'),
            'Tickers': ticker_item.replace('.JK', ''),
            'Price': f"{apply_fraksi_harga(current_price):,.0f}",
            'WR': f"{backtest_metrics['win_rate']:.1f}%",
            'Trades': f"{backtest_metrics['total_trades']:.0f}",
            '%C vs PC': f"{pct_change:.2f}%",
            'H Today': f"{apply_fraksi_harga(high_today):,.0f}",
            'H Prev': f"{apply_fraksi_harga(high_yesterday):,.0f}",
            'H 2D Ago': f"{apply_fraksi_harga(high_day_before_yesterday):,.0f}",
            'H 3D Ago': f"{apply_fraksi_harga(high_two_days_ago):,.0f}",
            'H 4D Ago': f"{apply_fraksi_harga(high_three_days_ago):,.0f}",
            'Value (B)': f"{transaction_value_billion:,.2f}",
            '1. H<Prev': "☑" if cond_decreasing_high_today else "",
            '2. Prev<H-2': "☑" if cond_decreasing_high_yesterday else "",
            '3. H-2<H-3': "☑" if cond_decreasing_high_two_days_ago else "",
            '4. H-3<H-4': "☑" if cond_decreasing_high_three_days_ago else "",
            '5. PrevRed': "☑" if cond_prev_red else "",
            '6. L>PL': "☑" if cond_low_gt_prev_low else "",
            '7. Green': "☑" if cond_close_gt_open else ""
        }
    return None


# --- Main Screener Logic (Live Scan) ---
def run_full_screener():
    """
    Menjalankan full screener untuk semua ticker dan mengembalikan hasil.
    """
    results = []

    print("Starting Decreasing Highs Screener (Live Scan)...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="6mo", interval="1d", auto_adjust=True, progress=False)

            if df.empty or len(df) < 5:
                continue

            screener_output = run_decreasing_highs_screener(df.copy(), ticker_item)

            if screener_output:
                results.append(screener_output)

        except Exception as e:
            pass

    print("Decreasing Highs Screener (Live Scan) finished.")

    if results:
        df_screener_results = pd.DataFrame(results)

        # Sort by WR
        df_screener_results['WR_numeric'] = df_screener_results['WR'].str.rstrip('%').astype(float)
        df_screener_results = df_screener_results.sort_values(
            by=['WR_numeric'],
            ascending=[False]
        ).reset_index(drop=True)
        df_screener_results = df_screener_results.drop(columns=['WR_numeric'])

        return df_screener_results

    return None