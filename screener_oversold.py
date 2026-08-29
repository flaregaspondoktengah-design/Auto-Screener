# Screener Oversold - RSI & Stochastic
# Mendeteksi saham yang sedang dalam kondisi oversold
# RSI < 30 = Oversold
# Stochastic %K < 20 = Oversold

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Daftar saham IDX (yang sering aktif)
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']


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


# --- ATR Functions for Compression Ratio ---
def calculate_atr(df, period=14):
    """
    Menghitung Average True Range (ATR).
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


def calculate_compression_ratio(df):
    """
    Menghitung Compression Ratio = ATR 5 / ATR 20
    """
    try:
        atr_5 = calculate_atr(df, period=5)
        atr_20 = calculate_atr(df, period=20)
        
        atr_5_today = float(atr_5.iloc[-1])
        atr_20_today = float(atr_20.iloc[-1])
        
        if pd.isna(atr_5_today) or pd.isna(atr_20_today) or atr_20_today == 0:
            return None
        
        return atr_5_today / atr_20_today
    except Exception:
        return None


# --- Inflow Ratio Function ---
def calculate_inflow_ratio(df):
    """
    Menghitung Inflow Ratio = Value hari ini / (Price MA 20 x Volume MA 20)
    """
    try:
        if df is None or len(df) < 20:
            return None
        
        df_copy = df.tail(21).copy()
        
        if len(df_copy) < 20:
            return None
        
        # Calculate Price MA 20
        df_copy['Price_MA20'] = df_copy['Close'].rolling(window=20).mean()
        
        # Calculate Volume MA 20
        df_copy['Volume_MA20'] = df_copy['Volume'].rolling(window=20).mean()
        
        latest = df_copy.iloc[-1]
        prev = df_copy.iloc[-2] if len(df_copy) > 1 else None
        
        if prev is None:
            return None
        
        # Value hari ini = Close x Volume
        current_value = latest['Close'] * latest['Volume']
        
        # Price MA 20 dan Volume MA 20 dari hari sebelumnya
        price_ma20 = prev['Price_MA20']
        volume_ma20 = prev['Volume_MA20']
        
        if pd.isna(price_ma20) or pd.isna(volume_ma20):
            return None
        
        denominator = price_ma20 * volume_ma20
        
        if denominator == 0:
            return None
        
        inflow_ratio = current_value / denominator
        
        return inflow_ratio
        
    except Exception:
        return None


def calculate_rsi(data, period=14):
    """
    Menghitung RSI (Relative Strength Index)
    
    Args:
        data: DataFrame dengan kolom 'Close'
        period: Periode RSI (default 14)
    
    Returns:
        RSI value terakhir
    """
    try:
        close = data['Close']
        
        # Hitung perubahan harga
        delta = close.diff()
        
        # Pisahkan gain dan loss
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        # Hitung rata-rata gain dan loss (menggunakan EMA / Wilder's smoothing)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        # Untuk data setelah periode pertama, gunakan smoothing
        for i in range(period, len(gain)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
        
        # Hitung RS dan RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
        
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return None


def calculate_stochastic(data, k_period=10, k_smooth=5, d_period=5):
    """
    Menghitung Stochastic Oscillator
    
    Args:
        data: DataFrame dengan kolom 'High', 'Low', 'Close'
        k_period: Periode %K Length (default 10)
        k_smooth: Periode %K Smoothing (default 5)
        d_period: Periode %D Smoothing (default 5)
    
    Returns:
        Tuple (%K, %D)
    """
    try:
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Hitung raw %K
        lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
        highest_high = high.rolling(window=k_period, min_periods=k_period).max()
        
        raw_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        
        # Apply %K Smoothing
        smooth_k = raw_k.rolling(window=k_smooth, min_periods=k_smooth).mean()
        
        # Hitung %D (moving average dari smoothed %K)
        smooth_d = smooth_k.rolling(window=d_period, min_periods=d_period).mean()
        
        k_value = smooth_k.iloc[-1] if not pd.isna(smooth_k.iloc[-1]) else None
        d_value = smooth_d.iloc[-1] if not pd.isna(smooth_d.iloc[-1]) else None
        
        return k_value, d_value
        
    except Exception as e:
        print(f"Error calculating Stochastic: {e}")
        return None, None


def run_oversold_screener(symbol, min_price=100, min_value_billion=5):
    """
    Screener untuk mendeteksi saham oversold berdasarkan RSI dan Stochastic
    
    Oversold Criteria:
    - RSI < 30 = Oversold
    - RSI < 20 = Extremely Oversold
    - Stochastic %K < 20 = Oversold
    - Stochastic %K < 10 = Extremely Oversold
    
    Args:
        symbol: Kode saham (e.g., "BBCA.JK")
        min_price: Harga minimum
        min_value_billion: Nilai transaksi minimum (dalam miliar)
    
    Returns:
        Dictionary dengan hasil screening
    """
    try:
        # Download data 1 tahun terakhir untuk zone detection
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty or len(data) < 60:
            return None
        
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            data = data.loc[:, ~data.columns.duplicated()]
        
        # Ambil data terakhir
        last_close = data['Close'].iloc[-1]
        last_volume = data['Volume'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
        
        # Calculate %C vs PC
        pct_change_vs_pc = ((last_close - prev_close) / prev_close) * 100 if prev_close > 0 else 0
        
        # Filter harga minimum
        if last_close < min_price:
            return None
        
        # Hitung nilai transaksi
        transaction_value = last_close * last_volume
        transaction_value_billion = transaction_value / 1_000_000_000
        
        # Filter nilai transaksi minimum
        if transaction_value_billion < min_value_billion:
            return None
        
        # Hitung RSI
        rsi_value = calculate_rsi(data, period=14)
        if rsi_value is None:
            return None
        
        # Hitung Stochastic
        stoch_k, stoch_d = calculate_stochastic(data, k_period=10, k_smooth=5, d_period=5)
        if stoch_k is None:
            return None
        
        # Tentukan kondisi oversold
        rsi_oversold = rsi_value < 30
        stoch_oversold = stoch_k < 20
        
        # Hanya return jika salah satu atau keduanya oversold
        if not rsi_oversold and not stoch_oversold:
            return None
        
        # Calculate MA20 for Inflow Ratio
        data['MA20'] = data['Close'].rolling(window=20).mean()
        ma20 = float(data['MA20'].iloc[-1])
        
        # Calculate Inflow Ratio
        inflow_ratio = calculate_inflow_ratio(data)
        inflow_ratio_str = f"{inflow_ratio:.2f}x" if inflow_ratio else "-"
        
        # Calculate Compression Ratio
        compression_ratio = calculate_compression_ratio(data)
        compression_ratio_str = f"{compression_ratio:.2f}" if compression_ratio else "-"
        
        # Get Demand and Supply Zones
        try:
            demand_zone, supply_zone = get_demand_supply_zones(data, last_close)
        except Exception:
            demand_zone, supply_zone = None, None
        
        # Calculate zone values and RRR
        try:
            if demand_zone:
                demand_low = apply_fraksi_harga(demand_zone.low)
                demand_high = apply_fraksi_harga(demand_zone.high)
                demand_str = f"{int(demand_high):,} - {int(demand_low):,}"
                risk = last_close - demand_zone.low
            else:
                demand_str = "-"
                risk = None
        except Exception:
            demand_str = "-"
            risk = None
        
        try:
            if supply_zone:
                supply_low = apply_fraksi_harga(supply_zone.low)
                supply_high = apply_fraksi_harga(supply_zone.high)
                supply_str = f"{int(supply_high):,} - {int(supply_low):,}"
                reward = supply_zone.low - last_close
            else:
                supply_str = "-"
                reward = None
        except Exception:
            supply_str = "-"
            reward = None
        
        # Calculate RRR (Risk-Reward Ratio)
        if risk is not None and reward is not None and risk > 0:
            rrr = reward / risk
            rrr_str = f"{rrr:.2f}"
        else:
            rrr_str = "-"
        
        # Format output
        result = {
            'Date': data.index[-1].strftime('%d/%m/%Y'),
            'Ticker': symbol.replace('.JK', ''),
            'Price': f"{apply_fraksi_harga(last_close):,.0f}",
            '%C vs PC': f"{pct_change_vs_pc:+.2f}%",
            'RSI': f"{rsi_value:.1f}",
            'RSI OS': '☑' if rsi_oversold else '',
            'Stoch %K': f"{stoch_k:.1f}" if stoch_k else '-',
            'Stoch %D': f"{stoch_d:.1f}" if stoch_d else '-',
            'Stoch OS': '☑' if stoch_oversold else '',
            'Demand': demand_str,
            'Supply': supply_str,
            'Inflow Ratio': inflow_ratio_str,
            'Compression Ratio': compression_ratio_str,
            'RRR': rrr_str,
            'Signal': ''
        }
        
        # Tentukan signal
        if rsi_oversold and stoch_oversold:
            result['Signal'] = 'STRONG BUY'
        elif rsi_oversold or stoch_oversold:
            result['Signal'] = 'BUY'
        
        return result
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None


def get_ticker_list():
    """Mengembalikan list ticker untuk backtest"""
    return [t.replace('.JK', '') for t in tickers]


if __name__ == "__main__":
    # Test run
    print("Running Oversold Screener...")
    print("-" * 60)
    
    results = []
    for ticker in tickers[:10]:  # Test 10 ticker pertama
        output = run_oversold_screener(ticker)
        if output:
            results.append(output)
            print(f"{output['Ticker']}: RSI={output['RSI']} ({output['RSI OS']}), Stoch={output['Stoch %K']} ({output['Stoch OS']})")
    
    if results:
        df = pd.DataFrame(results)
        print("\nResults:")
        print(df.to_string(index=False))
    else:
        print("No oversold stocks found in sample")