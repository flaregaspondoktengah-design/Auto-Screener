# Screener Demand Zone
# Mendeteksi saham yang berada di area demand zone
# Harga saat ini berada dalam range demand zone (demand_low <= price <= demand_high)

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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


def get_current_demand_zone(df, current_price):
    """
    Get demand zone that contains current price.
    Returns demand zone if current_price is within zone range (demand_low <= price <= demand_high)
    """
    if len(df) < ATR_PERIOD_ZONE + 2:
        return None
    
    zones = build_zones(df)
    
    if not zones:
        return None
    
    # Get all active demand zones
    demand_zones = [z for z in zones if z.type == 'demand' and z.active]
    
    # Find demand zone that contains current price
    # price is within zone: z.low <= current_price <= z.high
    containing_zones = [z for z in demand_zones if z.low <= current_price <= z.high]
    
    if containing_zones:
        # Return the most recent zone (highest created index)
        return max(containing_zones, key=lambda z: z.created)
    
    return None


def get_nearest_supply_zone(df, current_price):
    """
    Get nearest supply zone above current price for RRR calculation.
    """
    if len(df) < ATR_PERIOD_ZONE + 2:
        return None
    
    zones = build_zones(df)
    
    if not zones:
        return None
    
    supply_zones = [z for z in zones if z.type == 'supply' and z.active]
    
    # Find supply zone above current price
    supply_above = [z for z in supply_zones if z.low > current_price]
    
    if supply_above:
        return min(supply_above, key=lambda z: z.low - current_price)
    
    return None


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


# Daftar saham IDX
tickers = ['AADI.JK', 'ACES.JK', 'ADMR.JK', 'ADRO.JK', 'AKRA.JK', 'ANTM.JK', 'ARCI.JK', 'AVIA.JK', 'BKSL.JK', 'BRIS.JK', 'BRMS.JK', 'BSDE.JK', 'BTPS.JK', 'BUMI.JK', 'CMRY.JK', 'CPIN.JK', 'CTRA.JK', 'DEWA.JK', 'DKFT.JK', 'DSNG.JK', 'ELSA.JK', 'ENRG.JK', 'ERAA.JK', 'ESSA.JK', 'EXCL.JK', 'HEAL.JK', 'HRTA.JK', 'HRUM.JK', 'ICBP.JK', 'IMPC.JK', 'INDF.JK', 'INDY.JK', 'INKP.JK', 'INTP.JK', 'ISAT.JK', 'ITMG.JK', 'JPFA.JK', 'JSMR.JK', 'KIJA.JK', 'KLBF.JK', 'KPIG.JK', 'LSIP.JK', 'MAPA.JK', 'MAPI.JK', 'MARK.JK', 'MBMA.JK', 'MDKA.JK', 'MEDC.JK', 'MIKA.JK', 'MTEL.JK', 'MYOR.JK', 'PGAS.JK', 'PTBA.JK', 'RAJA.JK', 'RATU.JK', 'SIDO.JK', 'SMGR.JK', 'SMRA.JK', 'SRTG.JK', 'SSIA.JK', 'TAPG.JK', 'TCPI.JK', 'TINS.JK', 'TKIM.JK', 'TLKM.JK', 'TOBA.JK', 'TPIA.JK', 'UNTR.JK', 'UNVR.JK', 'WIFI.JK']


def run_demand_zone_screener(symbol, min_price=100, min_value_billion=5):
    """
    Screener untuk mendeteksi saham yang berada di area demand zone.
    
    Criteria:
    - Harga saat ini berada dalam range demand zone (demand_low <= price <= demand_high)
    - Transaction value >= min_value_billion
    
    Args:
        symbol: Kode saham (e.g., "BBCA.JK")
        min_price: Harga minimum
        min_value_billion: Nilai transaksi minimum (dalam miliar)
    
    Returns:
        Dictionary dengan hasil screening
    """
    try:
        # Download data 6 bulan terakhir
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty or len(data) < ATR_PERIOD_ZONE + 10:
            return None
        
        # Ambil data terakhir
        last_close = data['Close'].iloc[-1]
        last_volume = data['Volume'].iloc[-1]
        last_date = data.index[-1]
        
        # Calculate %C vs PC (Percentage Change vs Previous Close)
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
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
        
        # Get demand zone that contains current price
        demand_zone = get_current_demand_zone(data, last_close)
        
        if demand_zone is None:
            return None
        
        # Get nearest supply zone for RRR calculation
        supply_zone = get_nearest_supply_zone(data, last_close)
        
        # Calculate ATR for Compression Ratio
        data['H-L'] = data['High'] - data['Low']
        data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
        data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # ATR 5 and ATR 20
        data['ATR_5'] = data['TR'].ewm(alpha=1/5, adjust=False).mean()
        data['ATR_20'] = data['TR'].ewm(alpha=1/20, adjust=False).mean()
        
        atr_5_today = data['ATR_5'].iloc[-1] if not pd.isna(data['ATR_5'].iloc[-1]) else None
        atr_20_today = data['ATR_20'].iloc[-1] if not pd.isna(data['ATR_20'].iloc[-1]) else None
        
        compression_ratio = None
        if atr_5_today and atr_20_today:
            compression_ratio = atr_5_today / atr_20_today
        
        # Calculate MA20 and Volume MA20 for Inflow Ratio
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['Vol_MA20'] = data['Volume'].rolling(window=20).mean()
        
        ma20 = data['MA20'].iloc[-1] if not pd.isna(data['MA20'].iloc[-1]) else last_close
        vol_ma20 = data['Vol_MA20'].iloc[-1] if not pd.isna(data['Vol_MA20'].iloc[-1]) else last_volume
        
        # Inflow Ratio = Value hari ini / (Price MA 20 * Volume MA 20)
        value_today = last_close * last_volume
        avg_value_20 = ma20 * vol_ma20
        inflow_ratio = value_today / avg_value_20 if avg_value_20 > 0 else 0
        
        # Calculate RRR
        rrr = None
        if supply_zone and demand_zone:
            # Distance to supply (reward)
            distance_supply = supply_zone.low - last_close
            # Distance to demand low (risk)
            distance_demand = last_close - demand_zone.low
            
            if distance_demand > 0:
                rrr = distance_supply / distance_demand
        
        # Format Demand zone string (format: tinggi - rendah)
        demand_low = apply_fraksi_harga(demand_zone.low)
        demand_high = apply_fraksi_harga(demand_zone.high)
        demand_str = f"{int(demand_high):,} - {int(demand_low):,}"
        
        # Format Supply zone string (format: tinggi - rendah)
        supply_str = ""
        if supply_zone:
            supply_low = apply_fraksi_harga(supply_zone.low)
            supply_high = apply_fraksi_harga(supply_zone.high)
            supply_str = f"{int(supply_high):,} - {int(supply_low):,}"
        
        # Format output
        result = {
            'Date': last_date.strftime('%d/%m/%Y'),
            'Ticker': symbol.replace('.JK', ''),
            'Price': f"{apply_fraksi_harga(last_close):,.0f}",
            '%C vs PC': f"{pct_change_vs_pc:+.2f}%",
            'Demand': demand_str,
            'Supply': supply_str,
            'Inflow Ratio': f"{inflow_ratio:.2f}x",
            'Compression Ratio': f"{compression_ratio:.2f}" if compression_ratio is not None else "",
            'RRR': f"{rrr:.2f}x" if rrr is not None else ""
        }
        
        return result
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None


def get_ticker_list():
    """Mengembalikan list ticker untuk backtest"""
    return [t.replace('.JK', '') for t in tickers]


def get_stock_demand_supply(symbol, days=180):
    """
    Mendapatkan informasi demand dan supply zone untuk saham tertentu.
    Fungsi ini untuk lookup saham individual, bukan screening.
    Menggunakan logika yang sama dengan Screener Demand Zone (harga harus berada di dalam demand zone).
    
    Args:
        symbol: Kode saham (e.g., "BBCA.JK" atau "BBCA")
        days: Jumlah hari data historis (default 180)
    
    Returns:
        Dictionary dengan informasi demand/supply zone, atau None jika error
    """
    try:
        # Pastikan symbol memiliki .JK
        if not symbol.endswith('.JK'):
            symbol = symbol + '.JK'
        
        # Download data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty or len(data) < ATR_PERIOD_ZONE + 10:
            return None
        
        # Ambil data terakhir
        last_close = data['Close'].iloc[-1]
        last_volume = data['Volume'].iloc[-1]
        last_date = data.index[-1]
        
        # Calculate %C vs PC
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
        pct_change_vs_pc = ((last_close - prev_close) / prev_close) * 100 if prev_close > 0 else 0
        
        # =========================================================
        # PERUBAHAN UTAMA DI SINI:
        # Menggunakan fungsi yang sama dengan Screener Demand Zone
        # =========================================================
        demand_zone = get_current_demand_zone(data, last_close)
        supply_zone = get_nearest_supply_zone(data, last_close)
        
        # Calculate ATR for Compression Ratio
        data['H-L'] = data['High'] - data['Low']
        data['H-PC'] = abs(data['High'] - data['Close'].shift(1))
        data['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
        data['TR'] = data[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # ATR 5 and ATR 20
        data['ATR_5'] = data['TR'].ewm(alpha=1/5, adjust=False).mean()
        data['ATR_20'] = data['TR'].ewm(alpha=1/20, adjust=False).mean()
        
        atr_5_today = data['ATR_5'].iloc[-1] if not pd.isna(data['ATR_5'].iloc[-1]) else None
        atr_20_today = data['ATR_20'].iloc[-1] if not pd.isna(data['ATR_20'].iloc[-1]) else None
        
        compression_ratio = None
        if atr_5_today and atr_20_today:
            compression_ratio = atr_5_today / atr_20_today
        
        # Calculate MA20 and Volume MA20 for Inflow Ratio
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['Vol_MA20'] = data['Volume'].rolling(window=20).mean()
        
        ma20 = data['MA20'].iloc[-1] if not pd.isna(data['MA20'].iloc[-1]) else last_close
        vol_ma20 = data['Vol_MA20'].iloc[-1] if not pd.isna(data['Vol_MA20'].iloc[-1]) else last_volume
        
        # Inflow Ratio
        value_today = last_close * last_volume
        avg_value_20 = ma20 * vol_ma20
        inflow_ratio = value_today / avg_value_20 if avg_value_20 > 0 else 0
        
        # Calculate RRR
        rrr = None
        rrr_demand = None
        rrr_supply = None
        
        if demand_zone and supply_zone:
            # Distance to supply (reward)
            distance_supply = supply_zone.low - last_close
            # Distance to demand low (risk)
            distance_demand = last_close - demand_zone.low
            
            if distance_demand > 0:
                rrr = distance_supply / distance_demand
        elif demand_zone:
            rrr_demand = last_close - demand_zone.low
        elif supply_zone:
            rrr_supply = supply_zone.low - last_close
        
        # Transaction value
        transaction_value = last_close * last_volume
        transaction_value_billion = transaction_value / 1_000_000_000
        
        # Format results
        result = {
            'Date': last_date.strftime('%d/%m/%Y'),
            'Ticker': symbol.replace('.JK', ''),
            'Price': apply_fraksi_harga(last_close),
            'Price Raw': last_close,
            '%C vs PC': pct_change_vs_pc,
            'Value (B)': transaction_value_billion,
            'Demand Zone': None,
            'Demand High': None,
            'Demand Low': None,
            'Supply Zone': None,
            'Supply High': None,
            'Supply Low': None,
            'Inflow Ratio': inflow_ratio,
            'Compression Ratio': compression_ratio,
            'RRR': rrr,
            'Distance to Demand': rrr_demand,
            'Distance to Supply': rrr_supply,
            'In Demand Zone': False,
            'In Supply Zone': False
        }
        
        # Fill demand zone info
        if demand_zone:
            demand_high = apply_fraksi_harga(demand_zone.high)
            demand_low = apply_fraksi_harga(demand_zone.low)
            result['Demand Zone'] = f"{int(demand_high):,} - {int(demand_low):,}"
            result['Demand High'] = demand_zone.high
            result['Demand Low'] = demand_zone.low
            # Karena menggunakan get_current_demand_zone, harga PASTI di dalam zone
            result['In Demand Zone'] = True
        
        # Fill supply zone info
        if supply_zone:
            supply_high = apply_fraksi_harga(supply_zone.high)
            supply_low = apply_fraksi_harga(supply_zone.low)
            result['Supply Zone'] = f"{int(supply_high):,} - {int(supply_low):,}"
            result['Supply High'] = supply_zone.high
            result['Supply Low'] = supply_zone.low
            # Mengecek apakah harga kebetulan juga ada di dalam supply zone (sangat jarang)
            result['In Supply Zone'] = supply_zone.low <= last_close <= supply_zone.high
        
        return result
        
    except Exception as e:
        print(f"Error getting demand/supply for {symbol}: {e}")
        return None


if __name__ == "__main__":
    # Test run
    print("Running Demand Zone Screener...")
    print("-" * 60)
    
    results = []
    for ticker in tickers[:10]:  # Test 10 ticker pertama
        output = run_demand_zone_screener(ticker)
        if output:
            results.append(output)
            print(f"{output['Ticker']}: Price={output['Price']}, Demand={output['Demand']}")
    
    if results:
        df = pd.DataFrame(results)
        print("\nResults:")
        print(df.to_string(index=False))
    else:
        print("No stocks in demand zone found in sample")