# FVG Screener - Fair Value Gap Detection
# Screener untuk mendeteksi Bullish Fair Value Gap (FVG)
# FVG terjadi ketika ada gap antara High candle sebelumnya dan Low candle berikutnya

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from datetime import date, timedelta

# Suppress FutureWarning from yfinance
warnings.simplefilter(action='ignore', category=FutureWarning)

# List of IDX stocks
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']


def apply_fraksi_harga(price):
    """Determines the tick size and applies rounding based on Indonesian stock exchange rules."""
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


def calculate_fvg(df):
    """
    Mengidentifikasi dan menghitung Fair Value Gap (FVG) bullish dan bearish
    berdasarkan pola 3 candlestick.

    Bullish FVG: High candle i-1 < Low candle i+1 (gap ke atas)
    Bearish FVG: Low candle i-1 > High candle i+1 (gap ke bawah)

    Args:
        df (pd.DataFrame): DataFrame harga saham dengan kolom 'High' dan 'Low'.

    Returns:
        pd.DataFrame: DataFrame yang telah ditambahkan kolom 'Bullish_FVG' dan 'Bearish_FVG'.
    """
    df_copy = df.copy()

    if 'High' not in df_copy.columns or 'Low' not in df_copy.columns:
        raise ValueError("DataFrame harus memiliki kolom 'High' dan 'Low'.")

    df_copy['Bullish_FVG'] = np.nan
    df_copy['Bearish_FVG'] = np.nan

    for i in range(1, len(df_copy) - 1):
        high_prev = df_copy['High'].iloc[i-1]
        low_prev = df_copy['Low'].iloc[i-1]
        high_next = df_copy['High'].iloc[i+1]
        low_next = df_copy['Low'].iloc[i+1]

        # Bullish FVG: High candle i-1 < Low candle i+1
        if high_prev < low_next:
            fvg_bullish_value = low_next - high_prev
            df_copy.loc[df_copy.index[i], 'Bullish_FVG'] = fvg_bullish_value

        # Bearish FVG: Low candle i-1 > High candle i+1
        if low_prev > high_next:
            fvg_bearish_value = low_prev - high_next
            df_copy.loc[df_copy.index[i], 'Bearish_FVG'] = fvg_bearish_value

    return df_copy


def calculate_wr(df, lookback=100):
    """
    Calculate Win Rate berdasarkan histori FVG.
    Win Rate = persentase FVG yang berhasil ditarik (price kembali ke area FVG).
    """
    fvg_signals = df[df['Bullish_FVG'].notna()].copy()
    
    if len(fvg_signals) < 5:
        return 0, 0
    
    wins = 0
    total = 0
    
    for idx in range(len(fvg_signals) - 1):
        fvg_idx = fvg_signals.index[idx]
        fvg_row = fvg_signals.iloc[idx]
        
        # FVG Low = High of candle i-1
        # FVG High = Low of candle i+1
        fvg_low = df.loc[fvg_idx - 1, 'High'] if fvg_idx - 1 in df.index else None
        fvg_high = df.loc[fvg_idx + 1, 'Low'] if fvg_idx + 1 in df.index else None
        
        if fvg_low is None or fvg_high is None:
            continue
        
        # Check if price came back to FVG zone within next 20 candles
        future_df = df.loc[fvg_idx + 2:fvg_idx + 22]
        
        if len(future_df) > 0:
            # Win if price retraced to FVG zone
            hit_fvg = ((future_df['Low'] <= fvg_high) & (future_df['Low'] >= fvg_low)).any()
            if hit_fvg:
                wins += 1
            total += 1
    
    if total == 0:
        return 0, 0
    
    wr = (wins / total) * 100
    return wr, total


def run_fvg_screener(results_list=None, symbol=None, target_date=None):
    """
    Run FVG screener for a single stock.
    
    Args:
        results_list: Not used, kept for compatibility
        symbol: Stock symbol to analyze
        target_date: Target date for analysis (not used in FVG, kept for compatibility)
    
    Returns:
        dict: FVG analysis results or None if criteria not met
    """
    if symbol is None:
        return None
    
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False, auto_adjust=True)
    except Exception:
        return None
    
    if df.empty:
        return None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Standardize column names
    new_columns = []
    for col in df.columns:
        if col.lower() == 'adj close':
            new_columns.append('Close')
        else:
            new_columns.append(col.capitalize())
    df.columns = new_columns
    df = df.loc[:, ~df.columns.duplicated(keep='last')]
    
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_cols):
        return None
    
    if len(df) < 5:
        return None
    
    try:
        df = calculate_fvg(df)
    except ValueError:
        return None
    
    if len(df) < 3:
        return None
    
    # Get latest Bullish FVG from second to last candle (completed pattern)
    latest_bullish_fvg_size = df['Bullish_FVG'].iloc[-2]
    
    if pd.isna(latest_bullish_fvg_size):
        return None
    
    # Get the candles involved in the latest Bullish FVG
    # Bull FVG (L) is High of candle i-1 (df.iloc[-3])
    # Bull FVG (H) is Low of candle i+1 (df.iloc[-1])
    bull_fvg_low = float(df['High'].iloc[-3])
    bull_fvg_high = float(df['Low'].iloc[-1])
    
    current_price = float(df['Close'].iloc[-1])
    latest_volume = float(df['Volume'].iloc[-1])
    transaction_value_billion = (current_price * latest_volume) / 1_000_000_000
    
    # Calculate %C vs PC (Percentage Change vs Previous Close)
    prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
    pct_change_vs_pc = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
    
    # Filter criteria
    if transaction_value_billion < 5:
        return None
    
    if current_price < 100:
        return None
    
    # Calculate Win Rate
    wr, trades = calculate_wr(df)
    
    # Calculate FVG Size as percentage of price
    fvg_size_pct = (bull_fvg_high - bull_fvg_low) / current_price * 100
    
    # Calculate position relative to FVG
    # Price above FVG = 1, Price in FVG = 0.5, Price below FVG = 0
    if current_price > bull_fvg_high:
        price_position = "Above"
    elif current_price >= bull_fvg_low:
        price_position = "In FVG"
    else:
        price_position = "Below"
    
    # Calculate recent trend (last 5 days)
    recent_close = df['Close'].iloc[-6:-1]
    ma5 = recent_close.mean()
    trend = "Bullish" if current_price > ma5 else "Bearish"
    
    # Calculate distance to FVG
    if current_price > bull_fvg_high:
        distance_to_fvg = ((current_price - bull_fvg_high) / current_price) * 100
    elif current_price < bull_fvg_low:
        distance_to_fvg = ((bull_fvg_low - current_price) / current_price) * 100
    else:
        distance_to_fvg = 0  # Price is in FVG
    
    return {
        'Tickers': symbol.replace('.JK', ''),
        'Price': f'{apply_fraksi_harga(current_price):,.0f}',
        '%C vs PC': f"{pct_change_vs_pc:+.2f}%",
        'Bull FVG (L)': f'{apply_fraksi_harga(bull_fvg_low):,.0f}',
        'Bull FVG (H)': f'{apply_fraksi_harga(bull_fvg_high):,.0f}',
        'FVG Size%': f'{fvg_size_pct:.2f}%',
        'Position': price_position,
        'Dist to FVG': f'{distance_to_fvg:.2f}%',
        'Trend': trend,
        'Value (B)': f'{transaction_value_billion:.2f}',
        'WR': f'{wr:.1f}%',
        'Trades': str(trades),
    }


def get_ticker_list():
    """Return list of available tickers for backtest."""
    return [t.replace('.JK', '') for t in tickers]


if __name__ == "__main__":
    # Test the screener
    print("Running FVG Screener...")
    results = []
    
    for s in tickers[:50]:  # Test with first 50 stocks
        r = run_fvg_screener(symbol=s)
        if r:
            results.append(r)
            print(f"Found: {r['Tickers']} - FVG: {r['Bull FVG (L)']} - {r['Bull FVG (H)']}")
    
    print(f"\nTotal found: {len(results)} stocks")
    
    if results:
        df = pd.DataFrame(results)
        print("\nResults:")
        print(df.to_string(index=False))
