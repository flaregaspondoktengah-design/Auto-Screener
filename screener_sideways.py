# BSJP : Sideways Screener - Live Screening Module
# Module ini berisi fungsi-fungsi untuk live screening saham Indonesia
# dengan strategi deteksi saham yang sedang sideways
# 
# Strategi:
# - Deteksi saham yang sedang sideways (MA Cluster: MA5, MA10, MA20 berdekatan)

import yfinance as yf
import pandas as pd
import numpy as np

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']


# --- Constants ---
MA_CLUSTER_TOLERANCE = 0.1  # 10% tolerance for MA clustering
SWING_DAYS = 5               # Days to hold for swing trade
ATR_SHORT = 5                # ATR short period
ATR_LONG = 20                # ATR long period

# --- MACD Constants ---
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# --- Demand & Supply Zone Constants ---
ATR_PERIOD_ZONE = 50
BOX_WIDTH = 2.5
SWING_LEN = 10
ATR_THRESHOLD_MULT = 2


# --- Demand & Supply Zone Functions ---
def atr_zone(df, period):
    """Calculate ATR for zone detection."""
    hl = df['High'] - df['Low']
    hc = abs(df['High'] - df['Close'].shift())
    lc = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def pivot_high(df, n):
    """Detect pivot high points."""
    return df['High'] == df['High'].rolling(n*2+1, center=True).max()


def pivot_low(df, n):
    """Detect pivot low points."""
    return df['Low'] == df['Low'].rolling(n*2+1, center=True).min()


class Zone:
    """Zone class for demand/supply tracking."""
    def __init__(self, ztype, low, high, created_idx):
        self.type = ztype
        self.low = low
        self.high = high
        self.created = created_idx
        self.active = True
        self.mitigated = False
        self.bos = False


def build_zones(df):
    """Build demand and supply zones from price data."""
    df = df.copy()
    df['ATR_zone'] = atr_zone(df, ATR_PERIOD_ZONE)
    df['pivH'] = pivot_high(df, SWING_LEN)
    df['pivL'] = pivot_low(df, SWING_LEN)

    zones = []

    for i in range(len(df)):
        if i < ATR_PERIOD_ZONE or pd.isna(df['ATR_zone'].iloc[i]):
            continue

        price_close = float(df['Close'].iloc[i])
        atr_val = float(df['ATR_zone'].iloc[i])
        buffer = atr_val * (BOX_WIDTH / 10)
        threshold = atr_val * ATR_THRESHOLD_MULT

        # Create Supply Zone
        if df['pivH'].iloc[i]:
            top = float(df['High'].iloc[i])
            bottom = top - buffer
            poi = (top + bottom) / 2

            if not any(abs((z.low+z.high)/2 - poi) < threshold for z in zones if z.active):
                zones.append(Zone('supply', bottom, top, i))

        # Create Demand Zone
        if df['pivL'].iloc[i]:
            bottom = float(df['Low'].iloc[i])
            top = bottom + buffer
            poi = (top + bottom) / 2

            if not any(abs((z.low+z.high)/2 - poi) < threshold for z in zones if z.active):
                zones.append(Zone('demand', bottom, top, i))

        # Zone Lifecycle
        for z in zones:
            if not z.active:
                continue

            # Mitigation
            if z.low <= price_close and price_close <= z.high:
                z.mitigated = True

            # Invalidation / BOS
            if z.type == 'supply' and price_close > z.high:
                z.active = False
                z.bos = True

            if z.type == 'demand' and price_close < z.low:
                z.active = False
                z.bos = True

    return zones


def get_demand_supply_zones(df, current_price):
    """
    Get nearest demand and supply zones for current price.
    Returns: (demand_zone, supply_zone) - can be None individually
    
    Demand Zone: zona di BAWAH harga saat ini, yang high-nya paling dekat dengan harga
    Supply Zone: zona di ATAS harga saat ini, yang low-nya paling dekat dengan harga
    """
    if len(df) < ATR_PERIOD_ZONE + 2:
        return None, None
    
    zones = build_zones(df)
    
    if not zones:
        return None, None
    
    demand_zones = [z for z in zones if z.type == 'demand' and z.active]
    supply_zones = [z for z in zones if z.type == 'supply' and z.active]

    # Find demand zone - zona di BAWAH current price
    dz = None
    demand_below = [z for z in demand_zones if z.high < current_price]
    
    if demand_below:
        # Pilih zona yang HIGH-nya paling dekat dengan current price (zona terdekat dari atas)
        dz = min(demand_below, key=lambda z: current_price - z.high)

    # Find supply zone - zona di ATAS current price
    sz = None
    supply_above = [z for z in supply_zones if z.low > current_price]
    
    if supply_above:
        # Pilih zona yang LOW-nya paling dekat dengan current price (zona terdekat dari bawah)
        sz = min(supply_above, key=lambda z: z.low - current_price)

    return dz, sz


# --- Helper Functions ---
def apply_fraksi_harga(price):
    """Menentukan tick size berdasarkan harga untuk Bursa Efek Indonesia."""
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


def is_ma_clustered(ma5 ,ma10, ma20, price_or_tolerance=None, tolerance=MA_CLUSTER_TOLERANCE):
    """
    Memeriksa apakah MA5, MA10, MA20 berdempetan (clustered).
    Clustered = (max MA - min MA) / min MA <= tolerance
    
    Args:
        ma5, ma10, ma20: Nilai Moving Average
        price_or_tolerance: Bisa berupa price (untuk backward compatibility) atau tolerance
        tolerance: Toleransi spread (default 10%)
    
    Returns:
        bool: True jika MA clustered
    """
    if any(pd.isna([ma5, ma10, ma20])):
        return False
    
    ma_values = [float(ma5), float(ma10), float(ma20)]
    min_ma = min(ma_values)
    
    # Backward compatibility: jika price_or_tolerance adalah number, gunakan sebagai tolerance
    # jika tidak, gunakan default tolerance
    actual_tolerance = tolerance
    if price_or_tolerance is not None and isinstance(price_or_tolerance, (int, float)):
        actual_tolerance = price_or_tolerance
    
    return (max(ma_values) - min_ma) / min_ma <= actual_tolerance


def check_ma_cluster_duration(df, days=5, tolerance=MA_CLUSTER_TOLERANCE):
    """
    Memeriksa apakah MA cluster bertahan selama N hari berturut-turut.
    
    Args:
        df: DataFrame dengan kolom 'MA5', 'MA10', 'MA20'
        days: Jumlah hari minimal untuk MA cluster (default 5)
        tolerance: Toleransi spread (default 3%)
    
    Returns:
        tuple: (is_clustered_duration, cluster_days, avg_spread_pct)
    """
    if len(df) < days + 20:  # Need enough data for MA calculation
        return False, 0, None
    
    cluster_count = 0
    spread_values = []
    
    # Check last N days
    for i in range(-days, 0):
        ma5 = df['MA5'].iloc[i]
        ma10 = df['MA10'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        
        # Skip if any value is NaN
        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
            continue
        
        ma_values = [float(ma5), float(ma10), float(ma20)]
        min_ma = min(ma_values)
        spread = (max(ma_values) - min_ma) / min_ma
        spread_values.append(spread * 100)  # Convert to percentage
        
        if spread <= tolerance:
            cluster_count += 1
    
    # Calculate average spread
    avg_spread = sum(spread_values) / len(spread_values) if spread_values else None
    
    # Must be clustered for all N days
    is_valid = cluster_count >= days
    
    return is_valid, cluster_count, avg_spread


def get_ma_position(ma5, ma10, ma20, close_price):
    """
    Mendapatkan posisi MA (bullish/bearish/neutral alignment).
    """
    if any(pd.isna([ma5, ma10, ma20, close_price])):
        return 'N/A'
    
    ma5, ma10, ma20, close_price = float(ma5), float(ma10), float(ma20), float(close_price)
    
    # Bullish alignment: MA5 > MA10 > MA20 and price above all
    if ma5 > ma10 > ma20 and close_price > ma5:
        return 'Bullish'
    # Bearish alignment: MA5 < MA10 < MA20 and price below all
    elif ma5 < ma10 < ma20 and close_price < ma5:
        return 'Bearish'
    else:
        return 'Neutral'


def calculate_macd_histogram(df, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL):
    """
    Menghitung MACD Histogram.
    
    Args:
        df: DataFrame dengan kolom 'Close'
        fast: Periode MACD fast (default 12)
        slow: Periode MACD slow (default 26)
        signal: Periode signal line (default 9)
    
    Returns:
        DataFrame: DataFrame dengan kolom 'MACD', 'MACD_Signal', 'MACD_Histogram'
    """
    df = df.copy()
    
    # Calculate MACD Line
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = ema_fast - ema_slow
    
    # Calculate Signal Line
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    
    # Calculate Histogram
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    return df


def calculate_atr(df, period=14):
    """
    Menghitung Average True Range (ATR).
    
    Args:
        df: DataFrame dengan kolom 'High', 'Low', 'Close'
        period: Periode ATR (default 14)
    
    Returns:
        Series: Nilai ATR
    """
    df = df.copy()
    
    # Calculate True Range
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    
    # Calculate ATR using Wilder's smoothing (RMA)
    df['ATR'] = df['TR'].ewm(alpha=1/period, adjust=False).mean()
    
    return df['ATR']


def check_atr_conditions(df, atr_short=ATR_SHORT, atr_long=ATR_LONG):
    """
    Memeriksa kondisi ATR:
    1. ATR 5 / ATR 20 <= 1 (Compression Ratio)
    2. ATR 5 dalam 3 hari terakhir terus menurun
    
    Returns:
        tuple: (compression_ratio, atr_5_today, cond_1_met, cond_2_met, all_met)
    """
    if len(df) < atr_long + 3:
        return None, None, False, False, False
    
    try:
        # Calculate ATR 5 and ATR 20
        atr_5 = calculate_atr(df, period=atr_short)
        atr_20 = calculate_atr(df, period=atr_long)
        
        # Get latest values
        atr_5_today = float(atr_5.iloc[-1])
        atr_5_yesterday = float(atr_5.iloc[-2])
        atr_5_2days_ago = float(atr_5.iloc[-3])
        atr_20_today = float(atr_20.iloc[-1])
        
        if pd.isna(atr_5_today) or pd.isna(atr_20_today):
            return None, None, False, False, False
        
        # Compression Ratio: ATR 5 / ATR 20
        compression_ratio = atr_5_today / atr_20_today
        
        # Condition 1: ATR 5 / ATR 20 <= 1
        cond_1 = compression_ratio <= 1
        
        # Condition 2: ATR 5 decreasing for 3 consecutive days
        # Today < Yesterday < 2 days ago (menurun = nilai makin kecil)
        cond_2 = atr_5_today < atr_5_yesterday < atr_5_2days_ago
        
        return compression_ratio, atr_5_today, cond_1, cond_2, (cond_1 and cond_2)
    except Exception as e:
        return None, None, False, False, False


# --- Main Screener Function ---
def run_sideways_screener(df, ticker_item, target_date=None):
    """
    Menjalankan screener untuk mencari saham yang sedang sideways (MA cluster).
    
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
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    if df is None:
        if ticker_item is None:
            return None
        df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=True, progress=False)

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

    if len(df_copy) < 50:
        return None
    
    # Filter data sampai target_date
    df_copy = df_copy[df_copy.index.date <= target_date]
    
    if len(df_copy) < 50:
        return None

    # Calculate MA for clustering
    df_copy['MA5'] = df_copy['Close'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['Close'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['Close'].rolling(window=20).mean()

    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20'])
    
    if len(df_copy) < 20:
        return None

    latest = df_copy.iloc[-1]
    current_price = float(latest['Close'])
    latest_volume = float(latest['Volume'])
    
    # Calculate average 20-day transaction value
    df_copy['Value'] = df_copy['Close'] * df_copy['Volume']
    avg_value_20d = df_copy['Value'].iloc[-20:].mean()
    avg_value_20d_billion = avg_value_20d / 1_000_000_000
    
    # Calculate %C vs PC (Percentage Change vs Previous Close)
    prev_close = float(df_copy['Close'].iloc[-2]) if len(df_copy) > 1 else current_price
    pct_change_vs_pc = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0

    # Basic filters: average 20-day value >= 5 billion rupiah
    if pd.isna(avg_value_20d_billion) or avg_value_20d_billion < 5:
    	return None

    ma5 = float(latest['MA5'])
    ma10 = float(latest['MA10'])
    ma20 = float(latest['MA20'])

    # Check MA clustering duration (minimum 20 days)
    ma_cluster_duration, cluster_days, avg_spread = check_ma_cluster_duration(df_copy, days=20)

    # Main criteria check - must be sideways for at least 20 days
    if not ma_cluster_duration:
        return None

    # Get MA position
    ma_position = get_ma_position(ma5, ma10, ma20, current_price)

    # Calculate MA spread percentage (relative to min MA)
    ma_values = [ma5, ma10, ma20]
    min_ma = min(ma_values)
    ma_spread_pct = (max(ma_values) - min_ma) / min_ma * 100

    # Calculate Volume MA 20 and Inflow Ratio
    df_copy['Vol_MA20'] = df_copy['Volume'].rolling(window=20).mean()
    vol_ma20 = float(df_copy['Vol_MA20'].iloc[-1])
    # Inflow Ratio = Value hari ini / (Price MA 20 * Volume MA 20)
    value_today = current_price * latest_volume
    avg_value_20 = ma20 * vol_ma20
    inflow_ratio = value_today / avg_value_20 if avg_value_20 > 0 else 0

    # Check ATR conditions
    compression_ratio, atr_5_today, atr_cond_1, atr_cond_2, atr_all_cond = check_atr_conditions(df_copy)
    
    # ATR conditions must be met
    if not atr_all_cond:
        return None

    # Determine signal strength based on MA spread
    signal_score = 0
    
    # Tighter MA spread = stronger sideways signal
    if ma_spread_pct <= 2:
        signal_score += 2
    elif ma_spread_pct <= 3:
        signal_score += 1
    
    # MA position bonus
    if ma_position == 'Bullish':
        signal_score += 1

    if signal_score >= 3:
        signal = 'STRONG BUY'
    elif signal_score >= 2:
        signal = 'BUY'
    else:
        signal = 'CONSIDER'

    # Get Demand and Supply Zones (for display only, not a filtering criteria)
    try:
        demand_zone, supply_zone = get_demand_supply_zones(df_copy, current_price)
    except Exception:
        demand_zone, supply_zone = None, None
    
    # Calculate zone values (format: high - low)
    try:
        if demand_zone:
            demand_low = apply_fraksi_harga(demand_zone.low)
            demand_high = apply_fraksi_harga(demand_zone.high)
            demand_str = f"{int(demand_high):,} - {int(demand_low):,}"
        else:
            demand_str = "-"
    except Exception:
        demand_str = "-"
    
    try:
        if supply_zone:
            supply_low = apply_fraksi_harga(supply_zone.low)
            supply_high = apply_fraksi_harga(supply_zone.high)
            supply_str = f"{int(supply_high):,} - {int(supply_low):,}"
        else:
            supply_str = "-"
    except Exception:
        supply_str = "-"

    # Column order: Date, Tickers, Price, %C vs PC, Compression Ratio, Spread%, Inflow Ratio, Avg Val 20D (B), Demand, Supply, MA5, MA10, MA20, Position, Side Days, Signal
    return {
        'Date': latest.name.strftime('%d/%m/%Y'),
        'Tickers': ticker_item.replace('.JK', ''),
        'Price': f"{apply_fraksi_harga(current_price):,.0f}",
        '%C vs PC': f"{pct_change_vs_pc:+.2f}%",
        'Compression Ratio': f"{compression_ratio:.2f}",
        'Spread%': f"{ma_spread_pct:.2f}%",
        'Inflow Ratio': f"{inflow_ratio:.2f}x",
        'Avg Val 20D (B)': f"{avg_value_20d_billion:.1f}",
        'Demand': demand_str,
        'Supply': supply_str,
        'MA5': f"{apply_fraksi_harga(ma5):,.0f}",
        'MA10': f"{apply_fraksi_harga(ma10):,.0f}",
        'MA20': f"{apply_fraksi_harga(ma20):,.0f}",
        'Position': ma_position,
        'Side Days': f"{cluster_days}",
        'Signal': signal
    }


# --- Main Screener Logic ---
def run_full_screener():
    """Menjalankan full screener untuk semua ticker."""
    results = []

    print("Starting Sideways Screener...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=True, progress=False)

            if df.empty or len(df) < 50:
                continue

            screener_output = run_sideways_screener(df.copy(), ticker_item)

            if screener_output:
                results.append(screener_output)

        except Exception:
            pass

    print("Sideways Screener finished.")

    if results:
        df_screener_results = pd.DataFrame(results)

        # Sort by Spread% (tighter spread = better)
        df_screener_results['Spread_numeric'] = df_screener_results['Spread%'].str.rstrip('%').astype(float)
        df_screener_results = df_screener_results.sort_values(
            by=['Spread_numeric'],
            ascending=[True]
        ).reset_index(drop=True)
        df_screener_results = df_screener_results.drop(columns=['Spread_numeric'])

        return df_screener_results

    return None