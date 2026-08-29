# Volume Trend Screener
# Mendeteksi aktivitas akumulasi dan distribusi berdasarkan analisis volume
#
# Indikator:
# - Volume Ratio (Volume / VMA 20)
# - On-Balance Volume (OBV)
# - Chaikin Money Flow (CMF)
# - Price-Volume Trend (PVT)
# - Accumulation/Distribution Line

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']


# --- Indicator Functions ---

def calculate_volume_ratio(df, period=20):
    """
    Menghitung Volume Ratio = Volume / Volume MA
    """
    df = df.copy()
    df['Vol_MA'] = df['Volume'].rolling(window=period).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Vol_MA']
    return df


def calculate_obv(df):
    """
    Menghitung On-Balance Volume (OBV).
    OBV naik jika close > close kemarin, turun jika close < close kemarin.
    """
    df = df.copy()
    df['OBV'] = 0.0
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] + df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1] - df['Volume'].iloc[i]
        else:
            df.loc[df.index[i], 'OBV'] = df['OBV'].iloc[i-1]
    
    return df


def calculate_obv_trend(df, days=5):
    """
    Menghitung tren OBV dalam N hari terakhir.
    Returns: 'Up', 'Down', 'Flat', atau 'Mixed'
    """
    if len(df) < days + 1:
        return 'N/A', 0
    
    obv_values = df['OBV'].iloc[-days:].values
    up_days = 0
    down_days = 0
    
    for i in range(1, len(obv_values)):
        if obv_values[i] > obv_values[i-1]:
            up_days += 1
        elif obv_values[i] < obv_values[i-1]:
            down_days += 1
    
    # Calculate OBV change percentage
    obv_start = df['OBV'].iloc[-days]
    obv_end = df['OBV'].iloc[-1]
    if obv_start != 0:
        obv_change_pct = ((obv_end - obv_start) / abs(obv_start)) * 100
    else:
        obv_change_pct = 0
    
    # Determine trend
    if up_days >= days - 1:
        return 'Up', obv_change_pct
    elif down_days >= days - 1:
        return 'Down', obv_change_pct
    elif up_days > down_days:
        return 'Up', obv_change_pct
    elif down_days > up_days:
        return 'Down', obv_change_pct
    else:
        return 'Flat', obv_change_pct


def calculate_cmf(df, period=20):
    """
    Menghitung Chaikin Money Flow (CMF).
    CMF = Sum(MF Volume) / Sum(Volume) dalam periode tertentu
    
    MF Volume = Volume × CLV
    CLV (Close Location Value) = ((Close - Low) - (High - Close)) / (High - Low)
    """
    df = df.copy()
    
    # Calculate CLV
    df['CLV'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df['CLV'] = df['CLV'].fillna(0)  # Handle division by zero
    
    # Calculate MF Volume
    df['MF_Volume'] = df['CLV'] * df['Volume']
    
    # Calculate CMF
    df['CMF'] = df['MF_Volume'].rolling(window=period).sum() / df['Volume'].rolling(window=period).sum()
    
    return df


def calculate_pvt(df):
    """
    Menghitung Price-Volume Trend (PVT).
    PVT = PVT kemarin + (Volume × % Perubahan Harga)
    """
    df = df.copy()
    df['PVT'] = 0.0
    
    for i in range(1, len(df)):
        pct_change = (df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1]
        df.loc[df.index[i], 'PVT'] = df['PVT'].iloc[i-1] + (df['Volume'].iloc[i] * pct_change)
    
    return df


def calculate_pvt_trend(df, days=5):
    """
    Menghitung tren PVT dalam N hari terakhir.
    """
    if len(df) < days + 1:
        return 'N/A'
    
    pvt_values = df['PVT'].iloc[-days:].values
    up_days = 0
    down_days = 0
    
    for i in range(1, len(pvt_values)):
        if pvt_values[i] > pvt_values[i-1]:
            up_days += 1
        elif pvt_values[i] < pvt_values[i-1]:
            down_days += 1
    
    if up_days >= days - 1:
        return 'Up'
    elif down_days >= days - 1:
        return 'Down'
    elif up_days > down_days:
        return 'Up'
    elif down_days > up_days:
        return 'Down'
    else:
        return 'Flat'


def calculate_ad_line(df):
    """
    Menghitung Accumulation/Distribution Line.
    A/D = A/D kemarin + (CLV × Volume)
    """
    df = df.copy()
    
    # Calculate CLV
    df['CLV'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    df['CLV'] = df['CLV'].fillna(0)
    
    # Calculate A/D
    df['AD_Line'] = 0.0
    for i in range(1, len(df)):
        df.loc[df.index[i], 'AD_Line'] = df['AD_Line'].iloc[i-1] + (df['CLV'].iloc[i] * df['Volume'].iloc[i])
    
    return df


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Menghitung MACD (Moving Average Convergence Divergence).
    
    MACD Line = EMA(fast) - EMA(slow)
    Signal Line = EMA(signal) dari MACD Line
    Histogram = MACD Line - Signal Line
    """
    df = df.copy()
    
    # Calculate EMAs
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD components
    df['MACD_Line'] = ema_fast - ema_slow
    df['MACD_Signal'] = df['MACD_Line'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD_Line'] - df['MACD_Signal']
    
    return df


def detect_macd_divergence(df, lookback=20):
    """
    Mendeteksi MACD Divergence (MYCD - Michael Yeoh style).
    
    Konsep MYCD menggunakan MACD Line dan Signal Line:
    - Cari pivot points pada MACD Line (bukan histogram)
    - Signal Line digunakan untuk konfirmasi
    
    Bullish Divergence:
    - MACD Line membuat Higher Low (pivot low di MACD Line)
    - Harga membuat Lower Low pada titik yang sama
    - Konfirmasi: MACD Line crossover di atas Signal Line atau mendekati
    
    Bearish Divergence:
    - MACD Line membuat Lower High (pivot high di MACD Line)
    - Harga membuat Higher High pada titik yang sama
    - Konfirmasi: MACD Line crossover di bawah Signal Line atau mendekati
    
    Args:
        df: DataFrame dengan data harga dan MACD
        lookback: Periode pencarian pivot points (default 20 hari)
    
    Returns:
        'Bullish Divergence', 'Bearish Divergence', atau 'No Divergence'
    """
    if len(df) < lookback + 5:
        return 'N/A'
    
    # Ambil data lookback hari terakhir
    recent_data = df.iloc[-lookback:].copy()
    recent_data = recent_data.reset_index(drop=True)
    
    # Cari pivot points pada MACD Line (bukan histogram)
    # Ini adalah kunci dari MYCD - pivot didasarkan pada MACD Line
    def find_macd_pivots(data, left=3, right=3):
        """Menemukan pivot highs dan lows pada MACD Line"""
        highs = []
        lows = []
        
        for i in range(left, len(data) - right):
            # Pivot High pada MACD Line
            # MACD Line lebih tinggi dari left dan right neighbors
            if all(data['MACD_Line'].iloc[i] >= data['MACD_Line'].iloc[i-j] for j in range(1, left+1)) and \
               all(data['MACD_Line'].iloc[i] >= data['MACD_Line'].iloc[i+j] for j in range(1, right+1)):
                highs.append({
                    'idx': i, 
                    'macd_line': data['MACD_Line'].iloc[i], 
                    'macd_signal': data['MACD_Signal'].iloc[i],
                    'price_high': data['High'].iloc[i],
                    'price_low': data['Low'].iloc[i],
                    'close': data['Close'].iloc[i]
                })
            
            # Pivot Low pada MACD Line
            # MACD Line lebih rendah dari left dan right neighbors
            if all(data['MACD_Line'].iloc[i] <= data['MACD_Line'].iloc[i-j] for j in range(1, left+1)) and \
               all(data['MACD_Line'].iloc[i] <= data['MACD_Line'].iloc[i+j] for j in range(1, right+1)):
                lows.append({
                    'idx': i, 
                    'macd_line': data['MACD_Line'].iloc[i], 
                    'macd_signal': data['MACD_Signal'].iloc[i],
                    'price_high': data['High'].iloc[i],
                    'price_low': data['Low'].iloc[i],
                    'close': data['Close'].iloc[i]
                })
        
        return highs, lows
    
    try:
        highs, lows = find_macd_pivots(recent_data)
        
        # Bullish Divergence:
        # MACD Line membuat Higher Low (pivot low di MACD Line)
        # Harga membuat Lower Low pada titik yang sama
        if len(lows) >= 2:
            recent_lows = lows[-2:]
            
            # MACD Line membuat higher low
            macd_higher_low = recent_lows[1]['macd_line'] > recent_lows[0]['macd_line']
            
            # Harga membuat lower low (bandingkan close)
            price_lower_low = recent_lows[1]['close'] < recent_lows[0]['close']
            
            if macd_higher_low and price_lower_low:
                return 'Bullish Divergence'
        
        # Bearish Divergence:
        # MACD Line membuat Lower High (pivot high di MACD Line)
        # Harga membuat Higher High pada titik yang sama
        if len(highs) >= 2:
            recent_highs = highs[-2:]
            
            # MACD Line membuat lower high
            macd_lower_high = recent_highs[1]['macd_line'] < recent_highs[0]['macd_line']
            
            # Harga membuat higher high
            price_higher_high = recent_highs[1]['close'] > recent_highs[0]['close']
            
            if macd_lower_high and price_higher_high:
                return 'Bearish Divergence'
        
        return 'No Divergence'
        
    except Exception:
        return 'No Divergence'


def detect_divergence(df, days=10):
    """
    Mendeteksi divergensi antara harga dan OBV dalam 10 hari terakhir.
    
    Bullish Divergence: Harga turun + OBV naik
    Bearish Divergence: Harga naik + OBV turun
    
    Contoh:
    - Harga hari-9 = 1000, harga hari ini = 500 (turun)
    - OBV hari-9 = -400M, OBV hari ini = 300M (naik)
    - Hasil: Bullish Divergence
    """
    if len(df) < days + 1:
        return 'N/A'
    
    # Ambil nilai hari-9 dan hari ini
    price_start = df['Close'].iloc[-days]
    price_end = df['Close'].iloc[-1]
    
    obv_start = df['OBV'].iloc[-days]
    obv_end = df['OBV'].iloc[-1]
    
    # Bullish Divergence: Harga turun, OBV naik
    if price_end < price_start and obv_end > obv_start:
        return 'Bullish Divergence'
    
    # Bearish Divergence: Harga naik, OBV turun
    elif price_end > price_start and obv_end < obv_start:
        return 'Bearish Divergence'
    
    else:
        return 'No Divergence'


def generate_signal(volume_ratio, obv_trend, cmf, pvt_trend, divergence, macd_divergence, price_change_5d):
    """
    Generate trading signal berdasarkan kombinasi indikator.
    """
    score = 0
    
    # Volume Ratio scoring
    if volume_ratio > 2.0:
        score += 2
    elif volume_ratio > 1.5:
        score += 1
    elif volume_ratio < 0.5:
        score -= 1
    
    # OBV Trend scoring
    if obv_trend == 'Up':
        score += 2
    elif obv_trend == 'Down':
        score -= 2
    
    # CMF scoring
    if cmf > 0.25:
        score += 3
    elif cmf > 0.1:
        score += 2
    elif cmf > 0:
        score += 1
    elif cmf < -0.25:
        score -= 3
    elif cmf < -0.1:
        score -= 2
    elif cmf < 0:
        score -= 1
    
    # PVT Trend scoring
    if pvt_trend == 'Up':
        score += 1
    elif pvt_trend == 'Down':
        score -= 1
    
    # OBV Divergence scoring
    if divergence == 'Bullish Divergence':
        score += 3
    elif divergence == 'Bearish Divergence':
        score -= 3
    
    # MACD Divergence scoring (MYCD - Michael Yeoh)
    if macd_divergence == 'Bullish Divergence':
        score += 4  # MACD Divergence lebih kuat
    elif macd_divergence == 'Bearish Divergence':
        score -= 4
    
    # Hidden accumulation/distribution detection
    if abs(price_change_5d) < 3:  # Price sideways
        if obv_trend == 'Up' and cmf > 0.1:
            return 'HIDDEN ACCUMULATION'
        elif obv_trend == 'Down' and cmf < -0.1:
            return 'HIDDEN DISTRIBUTION'
    
    # Generate signal based on score
    if score >= 7:
        return 'STRONG ACCUMULATION'
    elif score >= 4:
        return 'ACCUMULATION'
    elif score <= -7:
        return 'STRONG DISTRIBUTION'
    elif score <= -4:
        return 'DISTRIBUTION'
    else:
        return 'NEUTRAL'


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


# --- Main Screener Function ---

def run_volume_trend_screener(symbol, min_price=100, min_avg_value_billion=5, target_date=None):
    """
    Screener untuk mendeteksi aktivitas akumulasi dan distribusi berdasarkan volume.
    
    Args:
        symbol: Kode saham (e.g., "BBCA.JK")
        min_price: Harga minimum
        min_avg_value_billion: Nilai transaksi rata-rata 20 hari minimum (dalam miliar)
        target_date: Tanggal target untuk screening (default: hari ini)
    
    Returns:
        Dictionary dengan hasil screening
    """
    from datetime import datetime, date
    
    try:
        # Download data 6 bulan terakhir
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty or len(data) < 50:
            return None
        
        # Filter by target_date if provided
        if target_date is not None:
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            data = data[data.index.date <= target_date]
        
        if len(data) < 50:
            return None
        
        # Ambil data terakhir
        last_close = data['Close'].iloc[-1]
        last_volume = data['Volume'].iloc[-1]
        last_date = data.index[-1]
        
        # Filter harga minimum
        if last_close < min_price:
            return None
        
        # Hitung nilai transaksi hari ini
        transaction_value = last_close * last_volume
        transaction_value_billion = transaction_value / 1_000_000_000
        
        # Hitung nilai transaksi rata-rata 20 hari terakhir
        data['Value'] = data['Close'] * data['Volume']
        avg_value_20d = data['Value'].iloc[-20:].mean()
        avg_value_20d_billion = avg_value_20d / 1_000_000_000
        
        # Filter nilai transaksi rata-rata 20 hari minimum
        if avg_value_20d_billion < min_avg_value_billion:
            return None
        
        # Calculate %C vs PC
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
        pct_change_vs_pc = ((last_close - prev_close) / prev_close) * 100 if prev_close > 0 else 0
        
        # Calculate all indicators
        data = calculate_volume_ratio(data, period=20)
        data = calculate_obv(data)
        data = calculate_cmf(data, period=20)
        data = calculate_pvt(data)
        data = calculate_ad_line(data)
        data = calculate_macd(data)  # MACD for MYCD Divergence
        
        # Get indicator values
        volume_ratio = data['Volume_Ratio'].iloc[-1]
        obv_trend, obv_change_pct = calculate_obv_trend(data, days=5)
        cmf = data['CMF'].iloc[-1]
        pvt_trend = calculate_pvt_trend(data, days=5)
        divergence = detect_divergence(data, days=10)  # OBV Divergence
        macd_divergence = detect_macd_divergence(data, lookback=20)  # MYCD Divergence
        
        # Calculate price change 5 days
        price_5d_ago = data['Close'].iloc[-6] if len(data) >= 6 else data['Close'].iloc[0]
        price_change_5d = ((last_close - price_5d_ago) / price_5d_ago) * 100 if price_5d_ago > 0 else 0
        
        # Generate signal
        signal = generate_signal(volume_ratio, obv_trend, cmf, pvt_trend, divergence, macd_divergence, price_change_5d)
        
        # Format output
        result = {
            'Date': last_date.strftime('%d/%m/%Y'),
            'Ticker': symbol.replace('.JK', ''),
            'Price': f"{apply_fraksi_harga(last_close):,.0f}",
            '%C vs PC': f"{pct_change_vs_pc:+.2f}%",
            'Vol Ratio': f"{volume_ratio:.2f}x",
            'OBV Trend': obv_trend,
            'OBV Chg%': f"{obv_change_pct:+.1f}%",
            'CMF': f"{cmf:.2f}",
            'PVT Trend': pvt_trend,
            'OBV Div': divergence,
            'MACD Div': macd_divergence,
            'Avg Val 20D (B)': f"{avg_value_20d_billion:.1f}",
            'Signal': signal
        }
        
        return result
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None


def run_full_volume_trend_screener(min_price=100, min_avg_value_billion=5, target_date=None):
    """
    Menjalankan full screener untuk semua ticker.
    """
    results = []
    
    print("Starting Volume Trend Screener...")
    for ticker_item in tickers:
        try:
            output = run_volume_trend_screener(
                ticker_item, 
                min_price=min_price, 
                min_avg_value_billion=min_avg_value_billion,
                target_date=target_date
            )
            if output:
                results.append(output)
        except Exception:
            pass
    
    print("Volume Trend Screener finished.")
    
    if results:
        df_results = pd.DataFrame(results)
        
        # Sort by Signal priority
        signal_order = {
            'STRONG ACCUMULATION': 1,
            'ACCUMULATION': 2,
            'HIDDEN ACCUMULATION': 3,
            'NEUTRAL': 4,
            'HIDDEN DISTRIBUTION': 5,
            'DISTRIBUTION': 6,
            'STRONG DISTRIBUTION': 7
        }
        df_results['Signal_Order'] = df_results['Signal'].map(signal_order)
        df_results = df_results.sort_values(by=['Signal_Order', 'Vol Ratio'], ascending=[True, False])
        df_results = df_results.drop(columns=['Signal_Order'])
        df_results = df_results.reset_index(drop=True)
        
        return df_results
    
    return None


def get_ticker_list():
    """Mengembalikan list ticker untuk backtest"""
    return [t.replace('.JK', '') for t in tickers]


if __name__ == "__main__":
    # Test run
    print("Running Volume Trend Screener...")
    print("-" * 60)
    
    results = run_full_volume_trend_screener()
    
    if results is not None:
        print(f"\nFound {len(results)} stocks")
        print("\nResults:")
        print(results.to_string(index=False))
    else:
        print("No stocks found")