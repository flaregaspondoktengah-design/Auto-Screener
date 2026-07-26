# BSJP : Backtest Magic Screener V1.1 - Historical Trade Analysis Module
# Module ini berisi fungsi-fungsi untuk menganalisis historical trades berdasarkan strategi Magic Screener V1.1

import yfinance as yf
import pandas as pd
import numpy as np
from screener_v11 import calculate_moving_averages, tickers

# --- Strategy Parameters ---
HIGH_TARGET_PCT = 1.36    # Target profit jika high tercapai
CLOSE_TARGET_PCT = 0.36   # Target profit jika close tercapai


# --- Function to Get Intraday Path ---
def get_intraday_path(ticker, target_date):
    """
    Mengambil data intraday 15 menit untuk menentukan path yang sebenarnya.
    
    Returns:
        tuple: (path, high_time, low_time, intraday_data_available)
        path: "↑" (naik dulu), "↓" (turun dulu), atau "N/A"
        high_time: jam berapa high dicapai
        low_time: jam berapa low dicapai
    """
    try:
        # Ambil data intraday 15m untuk tanggal target
        date_str = target_date.strftime('%Y-%m-%d')
        end_date_str = (pd.Timestamp(target_date) + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        
        # Ambil data 15m
        df_intraday = yf.download(ticker, start=date_str, end=end_date_str, 
                                   interval='15m', progress=False)
        
        if df_intraday.empty or len(df_intraday) < 2:
            return "N/A", None, None, False
        
        # Flatten MultiIndex columns jika ada
        if isinstance(df_intraday.columns, pd.MultiIndex):
            df_intraday.columns = df_intraday.columns.get_level_values(0)
        
        # Filter hanya data di tanggal target
        df_intraday = df_intraday[df_intraday.index.date == target_date]
        
        if df_intraday.empty or len(df_intraday) < 2:
            return "N/A", None, None, False
        
        # Cari daily high dan low
        daily_high = df_intraday['High'].max()
        daily_low = df_intraday['Low'].min()
        
        # Cari index pertama kali high dicapai
        high_mask = df_intraday['High'] >= daily_high * 0.9999
        if high_mask.any():
            first_high_idx = high_mask.idxmax()
            high_time = first_high_idx.strftime('%H:%M')
        else:
            high_time = None
            first_high_idx = None
        
        # Cari index pertama kali low dicapai
        low_mask = df_intraday['Low'] <= daily_low * 1.0001
        if low_mask.any():
            first_low_idx = low_mask.idxmax()
            low_time = first_low_idx.strftime('%H:%M')
        else:
            low_time = None
            first_low_idx = None
        
        # Tentukan path berdasarkan waktu
        if first_high_idx is not None and first_low_idx is not None:
            if first_high_idx <= first_low_idx:
                path = "↑"  # High dicapai lebih dulu (naik dulu)
            else:
                path = "↓"  # Low dicapai lebih dulu (turun dulu)
            return path, high_time, low_time, True
        else:
            return "N/A", high_time, low_time, False
            
    except Exception as e:
        return "N/A", None, None, False


# --- Function to Calculate Correlation Metrics ---
def calculate_correlation_metrics(detailed_trades_data):
    """
    Menghitung korelasi setiap kondisi terhadap keberhasilan mencapai Target High.
    
    Returns:
        dict: Win rate per kondisi ketika kondisi TRUE
    """
    if not detailed_trades_data or len(detailed_trades_data) == 0:
        return {}
    
    # Daftar kondisi yang akan dihitung korelasinya
    conditions = [
        '1. PR', '2. V>MA20', '3. MA+', '4. L>PL', '5. H>PH',
        '6. O=PC', '7. OL>HC', '8. C>VWAP', '9. PC<PVWAP', '10. V>MA5'
    ]
    
    correlation_results = {}
    
    for cond in conditions:
        # Hitung trades dengan kondisi TRUE
        trades_with_cond = [t for t in detailed_trades_data if t['conditions'].get(cond, False)]
        # Hitung trades sukses (Target H atau Gap Up) dengan kondisi TRUE
        successful_with_cond = [t for t in trades_with_cond if t['outcome'] in ['Target H', 'Gap Up']]
        
        total_with_cond = len(trades_with_cond)
        successful_count = len(successful_with_cond)
        
        if total_with_cond > 0:
            win_rate = (successful_count / total_with_cond) * 100
            correlation_results[cond] = {
                'win_rate': win_rate,
                'total_trades': total_with_cond,
                'successful': successful_count
            }
        else:
            correlation_results[cond] = {
                'win_rate': 0,
                'total_trades': 0,
                'successful': 0
            }
    
    # Hitung korelasi Inflow Ratio (numerik)
    successful_trades = [t for t in detailed_trades_data if t['outcome'] in ['Target H', 'Gap Up']]
    failed_trades = [t for t in detailed_trades_data if t['outcome'] not in ['Target H', 'Gap Up']]
    
    if successful_trades:
        avg_inflow_success = np.mean([t['inflow_ratio'] for t in successful_trades])
    else:
        avg_inflow_success = 0
    
    if failed_trades:
        avg_inflow_fail = np.mean([t['inflow_ratio'] for t in failed_trades])
    else:
        avg_inflow_fail = 0
    
    correlation_results['Inflow Ratio'] = {
        'avg_inflow_success': avg_inflow_success,
        'avg_inflow_fail': avg_inflow_fail,
        'inflow_diff': avg_inflow_success - avg_inflow_fail
    }
    
    return correlation_results


# --- Backtest Function for Detailed Trade Analysis ---
def backtest_screener_strategy(df, ticker_symbol=None, min_gain_pct=HIGH_TARGET_PCT, close_target_pct=CLOSE_TARGET_PCT, use_intraday=True):
    """
    Simulasi trades berdasarkan buy signal Magic Screener dan memeriksa profit atau stop loss.
    Trade dimasukkan pada closing price di hari signal.
    
    Exit Strategy:
    - Jika Open besok >= target high (1.36%): Profit = pct_next_open (Gap Up)
    - Jika High besok >= target high (1.36%): Profit = max(1.36%, pct_next_close)
    - Jika Close besok >= target close (0.36%): Profit = pct_next_close
    - Jika tidak: Profit = pct_next_close (bisa negatif)

    Args:
        df (pd.DataFrame): Historical stock data dengan kolom 'Open', 'High', 'Low', 'Close', 'Volume'.
        ticker_symbol (str): Symbol ticker untuk fetch intraday data.
        min_gain_pct (float): Persentase minimum gain untuk target high.
        close_target_pct (float): Persentase minimum gain untuk target close.
        use_intraday (bool): Apakah menggunakan data intraday untuk path yang akurat.

    Returns:
        tuple: (list detailed_trades, list profits_list, list raw_data_for_correlation)
    """
    df_copy = df.copy()

    # Flatten MultiIndex columns jika ada
    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    # Pastikan kolom essensial ada
    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return [], [], []

    # Hitung MAs
    try:
        df_copy = calculate_moving_averages(df_copy)
    except ValueError:
        return [], [], []

    # Drop NaNs dari rolling calculations
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5'])

    # Pastikan cukup data
    if len(df_copy) < 5 + 2:
        return [], [], []

    detailed_trades = []
    profits_list = []
    raw_data_for_correlation = []

    # Iterasi melalui DataFrame, mencari signals pada `i` dan mengevaluasi pada `i+1`
    for i in range(1, len(df_copy) - 1):
        signal_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i - 1]
        next_day = df_copy.iloc[i + 1]

        # Kriteria real-time screener (untuk entry signal)
        cond_volume_up = signal_day['Volume'] > prev_day['Volume']
        cond_close_up = signal_day['Close'] > prev_day['Close']
        cond_close_above_ma5 = signal_day['Close'] > signal_day['MA5']
        cond_high_value = (signal_day['Close'] * signal_day['Volume']) / 1_000_000_000 > 5

        # Kondisi tambahan untuk backtesting
        cond_prev_red_candle = prev_day['Close'] < prev_day['Open']
        cond_prev_close_below_ma5 = prev_day['Close'] < prev_day['MA5']
        cond_current_day_green_candle = signal_day['Close'] > signal_day['Open']
        cond_vol_above_ma20 = signal_day['Volume'] > signal_day['Volume_MA_20']
        cond_open_equal_prev_close = signal_day['Open'] == prev_day['Close']
        cond_low_greater_prev_low = signal_day['Low'] > prev_day['Low']
        cond_high_greater_prev_high = signal_day['High'] > prev_day['High']
        cond_open_low_greater_high_close = (signal_day['Open'] - signal_day['Low']) > (signal_day['High'] - signal_day['Close'])

        # Kriteria remarks (BUKAN bagian dari filter logic)
        cond_close_above_vwap = signal_day['Close'] > signal_day['VWAP_Daily']
        cond_prev_close_below_prev_vwap = prev_day['Close'] < prev_day['VWAP_Daily']
        cond_vol_above_ma5 = signal_day['Volume'] > signal_day['Volume_MA_5']
        
        # MA Uptrend condition
        cond_ma_uptrend = (
            signal_day['MA5'] > signal_day['MA10'] and
            signal_day['MA10'] > signal_day['MA20'] and
            signal_day['MA20'] > signal_day['MA50'] and
            signal_day['MA50'] > signal_day['MA200']
        )

        # Kombinasi semua kondisi untuk 'buy' signal
        if cond_volume_up and cond_close_up and cond_close_above_ma5 and cond_high_value and \
           cond_prev_close_below_ma5 and cond_current_day_green_candle and signal_day['Close'] >= 100:

            entry_date = signal_day.name.strftime('%Y-%m-%d')
            entry_price = float(signal_day['Close'])
            target_high_price = entry_price * (1 + min_gain_pct / 100)
            target_close_price = entry_price * (1 + close_target_pct / 100)
            
            # Calculate Inflow Ratio: Value hari ini / (Price MA20 * Volume MA20)
            signal_ma20 = float(signal_day['MA20'])
            signal_volume_ma20 = float(signal_day['Volume_MA_20'])
            signal_volume = float(signal_day['Volume'])
            if signal_ma20 > 0 and signal_volume_ma20 > 0:
                inflow_ratio = (entry_price * signal_volume) / (signal_ma20 * signal_volume_ma20)
            else:
                inflow_ratio = 0
            
            # Calculate Vol Ratio: Today's Volume / Volume MA 20
            if signal_volume_ma20 > 0:
                vol_ratio = signal_volume / signal_volume_ma20
            else:
                vol_ratio = 0

            next_day_open = float(next_day['Open'])
            high_next_day = float(next_day['High'])
            low_next_day = float(next_day['Low'])
            close_next_day = float(next_day['Close'])

            # Hitung % changes untuk Next Day
            pct_next_day_open = ((next_day_open - entry_price) / entry_price) * 100
            pct_next_day_high = ((high_next_day - entry_price) / entry_price) * 100
            pct_next_day_low = ((low_next_day - entry_price) / entry_price) * 100
            pct_next_day_close = ((close_next_day - entry_price) / entry_price) * 100

            # Determine path: naik dulu atau turun dulu (menggunakan intraday data REAL)
            next_day_date = next_day.name.date()
            high_time = "-"
            low_time = "-"
            path = "-"  # Default kosong
            
            if use_intraday and ticker_symbol:
                # Gunakan data intraday untuk path yang akurat
                path, high_time, low_time, intraday_ok = get_intraday_path(ticker_symbol, next_day_date)
                if not intraday_ok:
                    # Jika intraday tidak tersedia, biarkan kosong (tidak pakai estimasi)
                    path = "-"
                    high_time = "-"
                    low_time = "-"
            else:
                # Tanpa intraday, biarkan kosong
                path = "-"
                high_time = "-"
                low_time = "-"

            # EXIT LOGIC & PROFIT CALCULATION
            profit_pct = pct_next_day_close
            outcome = "Closed"

            if next_day_open >= target_high_price:
                profit_pct = pct_next_day_open
                outcome = "Gap Up"
            elif high_next_day >= target_high_price:
                profit_pct = max(min_gain_pct, pct_next_day_close)
                outcome = "Target H"
            elif close_next_day >= target_close_price:
                outcome = "Target C"
            else:
                outcome = "Miss"

            profits_list.append(profit_pct)

            close_pct_change_today = ((signal_day['Close'] - prev_day['Close']) / prev_day['Close']) * 100

            # Simpan kondisi untuk perhitungan korelasi
            conditions_dict = {
                '1. PR': cond_prev_red_candle,
                '2. V>MA20': cond_vol_above_ma20,
                '3. MA+': cond_ma_uptrend,
                '4. L>PL': cond_low_greater_prev_low,
                '5. H>PH': cond_high_greater_prev_high,
                '6. O=PC': cond_open_equal_prev_close,
                '7. OL>HC': cond_open_low_greater_high_close,
                '8. C>VWAP': cond_close_above_vwap,
                '9. PC<PVWAP': cond_prev_close_below_prev_vwap,
                '10. V>MA5': cond_vol_above_ma5
            }
            
            # Simpan raw data untuk korelasi
            raw_data_for_correlation.append({
                'inflow_ratio': inflow_ratio,
                'outcome': outcome,
                'conditions': conditions_dict
            })

            # Append detailed trade information
            detailed_trades.append({
                'Date': entry_date,
                'Price': f"{round(entry_price):,.0f}",
                '%C vs PC': f"{close_pct_change_today:.2f}%",
                '%H': f"{round(pct_next_day_high, 2):.2f}%",
                '%C': f"{round(pct_next_day_close, 2):.2f}%",
                '%O': f"{round(pct_next_day_open, 2):.2f}%",
                '%L': f"{round(pct_next_day_low, 2):.2f}%",
                'Inflow Ratio': f"{inflow_ratio:.2f}",
                'Vol Ratio': f"{vol_ratio:.2f}x",
                'Result': f"{profit_pct:.2f}%",
                'Outcome': outcome,
                'Path': path,
                'conditions_check': conditions_dict  # Keep for Correlation calculation
            })

    return detailed_trades, profits_list, raw_data_for_correlation


def run_backtest_for_ticker(ticker_symbol, period="5y", use_intraday=True):
    """
    Menjalankan backtest untuk ticker tertentu dan mengembalikan DataFrame hasil.

    Args:
        ticker_symbol (str): Symbol ticker (dengan atau tanpa .JK suffix)
        period (str): Period data historis (default: "5y")
        use_intraday (bool): Gunakan data intraday untuk path yang akurat

    Returns:
        tuple: (DataFrame hasil trades, dict summary statistics) atau (None, None) jika error
    """
    # Pastikan ticker memiliki suffix .JK
    if not ticker_symbol.upper().endswith('.JK'):
        ticker_symbol = ticker_symbol.upper() + '.JK'

    try:
        df = yf.download(ticker_symbol, period=period, interval="1d", auto_adjust=True, progress=False)

        if df.empty:
            return None, None

        detailed_trades, profits_list, raw_data = backtest_screener_strategy(
            df.copy(), ticker_symbol, use_intraday=use_intraday
        )

        if not detailed_trades:
            return None, None

        df_trades = pd.DataFrame(detailed_trades)

        # Convert date ke datetime untuk sorting
        df_trades['Date'] = pd.to_datetime(df_trades['Date'])

        # Sort by Date (latest first)
        df_trades = df_trades.sort_values(by='Date', ascending=False).reset_index(drop=True)

        # Reformat dates
        df_trades['Date'] = df_trades['Date'].dt.strftime('%d/%m/%Y')

        # Calculate summary statistics
        total_trades = len(detailed_trades)
        winning_trades = sum(1 for p in profits_list if p > 0)
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
        avg_profit_loss = sum(profits_list) / total_trades if total_trades > 0 else 0.0
        
        # Calculate target high success rate
        target_high_trades = sum(1 for t in raw_data if t['outcome'] in ['Target H', 'Gap Up'])
        target_high_rate = (target_high_trades / total_trades) * 100 if total_trades > 0 else 0.0
        
        # Calculate correlation metrics
        correlation_metrics = calculate_correlation_metrics(raw_data)
        
        # Format correlation string
        correlation_summary = {}
        for cond, metrics in correlation_metrics.items():
            if cond != 'Inflow Ratio':
                correlation_summary[cond] = f"{metrics['win_rate']:.0f}%"
            else:
                correlation_summary['Inflow_Avg_Success'] = f"{metrics['avg_inflow_success']:.2f}"
                correlation_summary['Inflow_Avg_Fail'] = f"{metrics['avg_inflow_fail']:.2f}"

        summary = {
            'ticker': ticker_symbol.replace('.JK', ''),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_profit_loss': avg_profit_loss,
            'target_high_rate': target_high_rate,
            'correlation': correlation_summary
        }

        # Add Correlation column to each trade
        correlation_col = []
        for _, row in df_trades.iterrows():
            win_rates = []
            conditions_check = row['conditions_check']
            for cond in ['1. PR', '2. V>MA20', '3. MA+', '4. L>PL', '5. H>PH', 
                         '6. O=PC', '7. OL>HC', '8. C>VWAP', '9. PC<PVWAP', '10. V>MA5']:
                if conditions_check.get(cond, False):
                    wr = correlation_metrics.get(cond, {}).get('win_rate', 0)
                    win_rates.append(wr)
            
            if win_rates:
                avg_win_rate = sum(win_rates) / len(win_rates)
                correlation_col.append(f"{avg_win_rate:.2f}%")
            else:
                correlation_col.append("0.00%")
        
        df_trades['Correlation'] = correlation_col
        
        # Drop conditions_check column (not for display)
        df_trades = df_trades.drop(columns=['conditions_check'])

        # Select columns for display
        display_cols = [
            'Date', 'Price', '%C vs PC', '%H', '%C', '%O', '%L', 
            'Correlation', 'Inflow Ratio', 'Vol Ratio', 'Result', 'Outcome', 'Path'
        ]
        df_display = df_trades[display_cols]

        return df_display, summary

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None, None


def get_ticker_list():
    """
    Mengembalikan list ticker yang tersedia untuk backtest.
    """
    return [t.replace('.JK', '') for t in tickers]