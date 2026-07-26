# BSJP : Decreasing Highs Screener - Live Screening Module
# Module ini berisi fungsi-fungsi untuk live screening saham Indonesia
# dengan strategi Decreasing Highs (4 hari high menurun berturut-turut)

import yfinance as yf
import pandas as pd
import numpy as np

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']


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