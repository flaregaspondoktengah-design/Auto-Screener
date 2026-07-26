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
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']


# --- Constants ---
MA_CLUSTER_TOLERANCE = 0.03  # 3% tolerance for MA clustering
SWING_DAYS = 5               # Days to hold for swing trade


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


def is_ma_clustered(ma5, ma10, ma20, close_price, tolerance=MA_CLUSTER_TOLERANCE):
    """
    Memeriksa apakah MA5, MA10, MA20 berdempetan (clustered).
    Clustered = range (max-min) <= tolerance * close_price
    """
    if any(pd.isna([ma5, ma10, ma20, close_price])):
        return False
    
    ma_values = np.array([float(ma5), float(ma10), float(ma20)])
    close_price = float(close_price)
    
    return np.ptp(ma_values) / close_price <= tolerance


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


# --- Backtest Summary Function ---
def _calculate_backtest_summary(df, holding_days=SWING_DAYS):
    """
    Menghitung metrik ringkasan backtest untuk strategi sideways swing.
    Entry ketika MA clustered, exit setelah holding_days atau trail stop.
    """
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'avg_holding_days': 0}

    if len(df_copy) < 50:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'avg_holding_days': 0}

    # Calculate MA
    df_copy['MA5'] = df_copy['Close'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['Close'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['Close'].rolling(window=20).mean()

    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20'])
    
    if len(df_copy) < 30:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'avg_holding_days': 0}

    trade_results = []
    holding_days_list = []

    for i in range(20, len(df_copy) - holding_days):
        current_price = float(df_copy['Close'].iloc[i])
        latest_volume = float(df_copy['Volume'].iloc[i])
        transaction_value_billion = (current_price * latest_volume) / 1_000_000_000

        # Basic filters
        if current_price < 100 or transaction_value_billion < 1:
            continue

        # Get MA values
        ma5 = df_copy['MA5'].iloc[i]
        ma10 = df_copy['MA10'].iloc[i]
        ma20 = df_copy['MA20'].iloc[i]

        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20):
            continue

        # Check MA clustering (sideways)
        if not is_ma_clustered(ma5, ma10, ma20, current_price):
            continue

        # Simulate swing trade - buy at close, sell after holding_days
        entry_price = current_price
        
        # Look forward for exit
        trade_result = None
        actual_holding = 0
        
        for j in range(i + 1, min(i + 1 + holding_days, len(df_copy))):
            actual_holding = j - i
            future_close = float(df_copy['Close'].iloc[j])
            future_ma20 = float(df_copy['MA20'].iloc[j])
            
            # Trail stop: Close below MA20 (exit early)
            if future_close < future_ma20 and actual_holding >= 2:
                trade_result = ((future_close - entry_price) / entry_price) * 100
                break
            
            # Max holding days reached
            if actual_holding >= holding_days:
                trade_result = ((future_close - entry_price) / entry_price) * 100
                break

        if trade_result is not None:
            trade_results.append(trade_result)
            holding_days_list.append(actual_holding)

    total_trades_count = len(trade_results)
    if total_trades_count == 0:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'avg_holding_days': 0}

    winning_trades_count = sum(1 for r in trade_results if r > 0)
    overall_win_rate = (winning_trades_count / total_trades_count) * 100
    overall_avg_profit_loss = sum(trade_results) / total_trades_count
    avg_holding = sum(holding_days_list) / len(holding_days_list) if holding_days_list else 0

    return {
        'win_rate': overall_win_rate,
        'avg_profit_loss': overall_avg_profit_loss,
        'total_trades': total_trades_count,
        'avg_holding_days': avg_holding
    }


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
        target_date = datetime.strptime(target_date, '%d-%m-%Y').date()

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
    
    if len(df_copy) < 5:
        return None

    latest = df_copy.iloc[-1]
    current_price = float(latest['Close'])
    latest_volume = float(latest['Volume'])
    transaction_value_billion = (current_price * latest_volume) / 1_000_000_000

    # Basic filters
    if current_price < 100 or transaction_value_billion < 1:
        return None

    ma5 = float(latest['MA5'])
    ma10 = float(latest['MA10'])
    ma20 = float(latest['MA20'])

    # Check MA clustering (sideways)
    ma_clustered = is_ma_clustered(ma5, ma10, ma20, current_price)

    # Main criteria check - must be sideways
    if not ma_clustered:
        return None

    # Get MA position
    ma_position = get_ma_position(ma5, ma10, ma20, current_price)

    # Calculate MA spread percentage
    ma_values = [ma5, ma10, ma20]
    ma_spread_pct = (max(ma_values) - min(ma_values)) / current_price * 100

    # Calculate backtest metrics
    backtest_df = yf.download(ticker_item, period="5y", interval="1d", auto_adjust=True, progress=False)
    backtest_metrics = _calculate_backtest_summary(backtest_df)

    if backtest_metrics['total_trades'] == 0:
        return None

    # Determine signal strength based on MA spread and backtest performance
    signal_score = 0
    
    # Tighter MA spread = stronger sideways signal
    if ma_spread_pct <= 1:
        signal_score += 2
    elif ma_spread_pct <= 2:
        signal_score += 1
    
    # Win rate consideration
    if backtest_metrics['win_rate'] >= 60:
        signal_score += 2
    elif backtest_metrics['win_rate'] >= 50:
        signal_score += 1
    
    # MA position bonus
    if ma_position == 'Bullish':
        signal_score += 1

    if signal_score >= 4:
        signal = 'STRONG BUY'
    elif signal_score >= 3:
        signal = 'BUY'
    elif signal_score >= 2:
        signal = 'CONSIDER'
    else:
        signal = 'WEAK'

    return {
        'Date': latest.name.strftime('%d/%m/%Y'),
        'Tickers': ticker_item.replace('.JK', ''),
        'Price': f"{apply_fraksi_harga(current_price):,.0f}",
        'WR': f"{backtest_metrics['win_rate']:.1f}%",
        'Trades': f"{backtest_metrics['total_trades']:.0f}",
        'Avg P/L': f"{backtest_metrics['avg_profit_loss']:.2f}%",
        'MA5': f"{apply_fraksi_harga(ma5):,.0f}",
        'MA10': f"{apply_fraksi_harga(ma10):,.0f}",
        'MA20': f"{apply_fraksi_harga(ma20):,.0f}",
        'Spread%': f"{ma_spread_pct:.2f}%",
        'Position': ma_position,
        '1. Side': "☑" if ma_clustered else "",
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