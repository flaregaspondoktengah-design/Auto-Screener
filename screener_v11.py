# BSJP : Magic Screener V1.1 - Live Screening Module
# Module ini berisi fungsi-fungsi untuk live screening saham Indonesia

import yfinance as yf
import pandas as pd
import numpy as np

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']

# ==========================================
# INTRADAY ANALYSIS FUNCTION (DIOPTIMASI)
# ==========================================
def get_15min_data(ticker, period='1mo'):
    try:
        df = yf.download(ticker, period=period, interval='15m', progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

def calculate_intraday_score(df_15m, daily_high, daily_low, daily_close):
    """
    Menghitung nilai Intraday HANYA untuk kolom yang ditampilkan di tabel:
    1. Position (Posisi Close di rentang harian)
    2. Volume Ratio (Rasio volume 15 menit terakhir dibanding rata-rata harian)
    Perhitungan skor, momentum, TP/SL dihapus karena tidak ditampilkan di tabel akhir.
    """
    if df_15m is None or len(df_15m) < 10:
        return {'position': 0, 'volume_ratio': 0}
    
    try:
        last_date = df_15m.index[-1].date()
        df_today = df_15m[df_15m.index.date == last_date]
        
        if len(df_today) < 5:
            return {'position': 0, 'volume_ratio': 0}
        
        # 1. CLOSE POSITION
        today_range = daily_high - daily_low
        if today_range > 0:
            close_position = (daily_close - daily_low) / today_range
        else:
            close_position = 0.5
        
        # 2. VOLUME RATIO (Max 2)
        avg_volume = df_today['Volume'].mean()
        last_volume = df_today.iloc[-1]['Volume']
        volume_ratio = last_volume / avg_volume if avg_volume > 0 else 1
        
        return {
            'position': close_position * 100,
            'volume_ratio': volume_ratio
        }
        
    except Exception:
        return {'position': 0, 'volume_ratio': 0}

# --- Helper Functions ---
def calculate_moving_averages(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()]

    if 'Close' not in df.columns:
        if 'Adj Close' in df.columns:
            df = df.rename(columns={'Adj Close': 'Close'})
        else:
            raise ValueError("Close column not found after processing DataFrame.")

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    if 'High' in df.columns and 'Low' in df.columns:
        df['VWAP_Daily'] = (df['High'] + df['Low'] + df['Close']) / 3
    else:
        df['VWAP_Daily'] = np.nan

    df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
    df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()

    return df

# --- Backtest Function for Summary Metrics ---
def _calculate_backtest_summary(df, min_gain_pct=1.36, stop_loss_pct=2.0):
    df_copy = df.copy()

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'correlation': {}}

    try:
        df_copy = calculate_moving_averages(df_copy)
    except ValueError:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'correlation': {}}

    df_copy['Volume_MA_20'] = df_copy['Volume'].rolling(window=20).mean()
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5'])

    if len(df_copy) < 200 + 2:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'correlation': {}}

    trade_profits = []
    
    conditions_data = {
        '1. PR': {'total': 0, 'success': 0},
        '2. V>MA20': {'total': 0, 'success': 0},
        '3. MA+': {'total': 0, 'success': 0},
        '4. L>PL': {'total': 0, 'success': 0},
        '5. H>PH': {'total': 0, 'success': 0},
        '6. O=PC': {'total': 0, 'success': 0},
        '7. OL>HC': {'total': 0, 'success': 0},
        '8. C>VWAP': {'total': 0, 'success': 0},
        '9. PC<PVWAP': {'total': 0, 'success': 0},
        '10. V>MA5': {'total': 0, 'success': 0},
        'Inflow Ratio': {'success_inflow': [], 'fail_inflow': []}
    }

    for i in range(1, len(df_copy) - 1):
        signal_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i - 1]
        next_day = df_copy.iloc[i + 1]

        cond_volume_up = signal_day['Volume'] > prev_day['Volume']
        cond_close_up = signal_day['Close'] > prev_day['Close']
        cond_close_above_ma5 = signal_day['Close'] > signal_day['MA5']
        cond_high_value = (signal_day['Close'] * signal_day['Volume']) / 1_000_000_000 > 5
        cond_prev_close_below_ma5 = prev_day['Close'] < prev_day['MA5']
        cond_current_day_green_candle = signal_day['Close'] > signal_day['Open']

        if cond_volume_up and cond_close_up and cond_close_above_ma5 and cond_high_value and \
           cond_prev_close_below_ma5 and cond_current_day_green_candle and signal_day['Close'] >= 100:

            entry_price = signal_day['Close']
            target_profit_price = entry_price * (1 + min_gain_pct / 100)

            high_next_day = float(next_day['High'])
            close_next_day = float(next_day['Close'])

            target_hit = high_next_day >= target_profit_price

            if target_hit:
                trade_profits.append(min_gain_pct)
            else:
                trade_profits.append(((close_next_day - entry_price) / entry_price) * 100)
            
            signal_ma20 = float(signal_day['MA20'])
            signal_volume_ma20 = float(signal_day['Volume_MA_20'])
            signal_volume = float(signal_day['Volume'])
            if signal_ma20 > 0 and signal_volume_ma20 > 0:
                inflow_ratio = (entry_price * signal_volume) / (signal_ma20 * signal_volume_ma20)
            else:
                inflow_ratio = 0
            
            cond_prev_red_candle = prev_day['Close'] < prev_day['Open']
            cond_vol_above_ma20 = signal_day['Volume'] > signal_day['Volume_MA_20']
            cond_ma_uptrend = (
                signal_day['MA5'] > signal_day['MA10'] and
                signal_day['MA10'] > signal_day['MA20'] and
                signal_day['MA20'] > signal_day['MA50'] and
                signal_day['MA50'] > signal_day['MA200']
            )
            cond_low_greater_prev_low = signal_day['Low'] > prev_day['Low']
            cond_high_greater_prev_high = signal_day['High'] > prev_day['High']
            cond_open_equal_prev_close = signal_day['Open'] == prev_day['Close']
            cond_open_low_greater_high_close = (signal_day['Open'] - signal_day['Low']) > (signal_day['High'] - signal_day['Close'])
            cond_close_above_vwap = signal_day['Close'] > signal_day['VWAP_Daily']
            cond_prev_close_below_prev_vwap = prev_day['Close'] < prev_day['VWAP_Daily']
            cond_vol_above_ma5 = signal_day['Volume'] > signal_day['Volume_MA_5']
            
            conditions_map = {
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
            
            for cond_name, cond_value in conditions_map.items():
                if cond_value:
                    conditions_data[cond_name]['total'] += 1
                    if target_hit:
                        conditions_data[cond_name]['success'] += 1
            
            if target_hit:
                conditions_data['Inflow Ratio']['success_inflow'].append(inflow_ratio)
            else:
                conditions_data['Inflow Ratio']['fail_inflow'].append(inflow_ratio)

    total_trades_count = len(trade_profits)
    if total_trades_count == 0:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0, 'correlation': {}}

    winning_trades_count = sum(1 for pnl in trade_profits if pnl >= min_gain_pct)
    overall_win_rate = (winning_trades_count / total_trades_count) * 100
    overall_avg_profit_loss = sum(trade_profits) / total_trades_count
    
    correlation_metrics = {}
    for cond_name, data in conditions_data.items():
        if cond_name != 'Inflow Ratio':
            if data['total'] > 0:
                wr = (data['success'] / data['total']) * 100
                correlation_metrics[cond_name] = {
                    'win_rate': wr,
                    'total': data['total'],
                    'success': data['success']
                }
            else:
                correlation_metrics[cond_name] = {'win_rate': 0, 'total': 0, 'success': 0}
        else:
            avg_success = np.mean(data['success_inflow']) if data['success_inflow'] else 0
            avg_fail = np.mean(data['fail_inflow']) if data['fail_inflow'] else 0
            correlation_metrics['Inflow Ratio'] = {
                'avg_success': avg_success,
                'avg_fail': avg_fail
            }

    return {
        'win_rate': overall_win_rate,
        'avg_profit_loss': overall_avg_profit_loss,
        'total_trades': total_trades_count,
        'correlation': correlation_metrics
    }

# --- Main Magic Screener Function (Live Screening) ---
def run_magic_screener(df, ticker_item, target_date=None):
    from datetime import datetime, date
    
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

    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return None

    try:
        df_copy = calculate_moving_averages(df_copy)
    except ValueError:
        return None

    df_copy['Volume_MA_20'] = df_copy['Volume'].rolling(window=20).mean()
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5'])

    if len(df_copy) < 2:
        return None
    
    df_copy = df_copy[df_copy.index.date <= target_date]
    
    if len(df_copy) < 2:
        return None

    latest = df_copy.iloc[-1]
    previous = df_copy.iloc[-2]

    latest_close = float(latest['Close'])
    latest_open = float(latest['Open'])
    latest_high = float(latest['High'])
    latest_low = float(latest['Low'])
    latest_volume = float(latest['Volume'])
    latest_ma5 = float(latest['MA5'])
    latest_ma10 = float(latest['MA10'])
    latest_ma20 = float(latest['MA20'])
    latest_ma50 = float(latest['MA50'])
    latest_ma200 = float(latest['MA200'])
    latest_volume_ma_20 = float(latest['Volume_MA_20'])
    latest_vwap = float(latest['VWAP_Daily'])
    latest_volume_ma_5 = float(latest['Volume_MA_5'])
    
    if latest_ma20 > 0 and latest_volume_ma_20 > 0:
        inflow_ratio = (latest_close * latest_volume) / (latest_ma20 * latest_volume_ma_20)
    else:
        inflow_ratio = 0

    # PERHITUNGAN VOL RATIO (Permintaan poin 3)
    vol_ratio = latest_volume / latest_volume_ma_20 if latest_volume_ma_20 > 0 else 0

    previous_close = float(previous['Close'])
    previous_volume = float(previous['Volume'])
    previous_open = float(previous['Open'])
    previous_ma5 = float(previous['MA5'])
    previous_high = float(previous['High'])
    previous_low = float(previous['Low'])
    previous_vwap = float(previous['VWAP_Daily'])

    transaction_value_billion = (latest_close * latest_volume) / 1_000_000_000

    cond_volume_up = latest_volume > previous_volume
    cond_close_up = latest_close > previous_close
    cond_close_above_ma5 = latest_close > latest_ma5
    cond_high_value = transaction_value_billion > 5
    cond_prev_close_below_ma5 = previous_close < previous_ma5
    cond_current_day_green_candle = latest_close > latest['Open']

    cond_prev_red_candle = previous_close < previous_open
    cond_vol_above_ma20 = latest_volume > latest_volume_ma_20
    cond_open_equal_prev_close = latest_open == previous_close
    cond_low_greater_prev_low = latest_low > previous_low
    cond_high_greater_prev_high = latest_high > previous_high
    cond_ma_uptrend = (
        latest_ma5 > latest_ma10 and
        latest_ma10 > latest_ma20 and
        latest_ma20 > latest_ma50 and
        latest_ma50 > latest_ma200
    )
    cond_open_low_greater_high_close = (latest_open - latest_low) > (latest_high - latest_close)
    cond_close_above_vwap = latest_close > latest_vwap
    cond_prev_close_below_prev_vwap = previous_close < previous_vwap
    cond_vol_above_ma5 = latest_volume > latest_volume_ma_5

    if cond_volume_up and cond_close_up and cond_close_above_ma5 and cond_high_value and \
       cond_prev_close_below_ma5 and cond_current_day_green_candle and latest_close >= 100:

        backtest_df = yf.download(ticker_item, period="5y", interval="1d", auto_adjust=True, progress=False)
        backtest_metrics = _calculate_backtest_summary(backtest_df)

        if backtest_metrics['total_trades'] == 0:
            return None

        df_15m = get_15min_data(ticker_item)
        intraday = calculate_intraday_score(df_15m, latest_high, latest_low, latest_close)
        
        correlation = backtest_metrics.get('correlation', {})
        
        conditions_check = [
            ('1. PR', cond_prev_red_candle),
            ('2. V>MA20', cond_vol_above_ma20),
            ('3. MA+', cond_ma_uptrend),
            ('4. L>PL', cond_low_greater_prev_low),
            ('5. H>PH', cond_high_greater_prev_high),
            ('6. O=PC', cond_open_equal_prev_close),
            ('7. OL>HC', cond_open_low_greater_high_close),
            ('8. C>VWAP', cond_close_above_vwap),
            ('9. PC<PVWAP', cond_prev_close_below_prev_vwap),
            ('10. V>MA5', cond_vol_above_ma5)
        ]
        
        win_rates = []
        for cond_name, cond_met in conditions_check:
            if cond_met:
                cond_data = correlation.get(cond_name, {})
                wr = cond_data.get('win_rate', 0)
                win_rates.append(wr)
        
        if win_rates:
            avg_win_rate = sum(win_rates) / len(win_rates)
            correlation_str = f"{avg_win_rate:.2f}%"
        else:
            correlation_str = "0.00%"

        return {
            'Date': latest.name.strftime('%d/%m/%Y'),
            'Tickers': ticker_item.replace('.JK', ''),
            'Price': f"{latest_close:,.0f}",
            'Trades': f"{backtest_metrics['total_trades']:.0f}",
            'WR': f"{backtest_metrics['win_rate']:.2f}%",
            '1D Return': f"{((latest_close - previous_close) / previous_close) * 100:.2f}%",
            'Position': f"{intraday['position']:.2f}%",
            'Correlation': correlation_str,
            'Inflow Ratio': f"{inflow_ratio:.2f}x",
            'Daily Vol Ratio': f"{intraday['volume_ratio']:.2f}x",
            'Vol Ratio': f"{vol_ratio:.2f}x"
        }
    return None

# --- Color Styling Functions ---
def get_color_for_percentage(value_str):
    try:
        value = float(str(value_str).replace('%', '').replace('x', ''))
        if value >= 80:
            return 'background-color: #2E7D32; color: white; font-weight: bold'
        elif value >= 50:
            return 'background-color: #ffc107; color: black; font-weight: bold' # Kuning
        else:
            return 'background-color: #E53935; color: white; font-weight: bold'
    except:
        return ''

def get_color_for_ratio(value_str):
    try:
        value_str_clean = str(value_str).replace('x', '').replace('X', '').strip()
        value = float(value_str_clean)
        if value > 2:
            return 'background-color: #2E7D32; color: white; font-weight: bold'
        elif value >= 1:
            return 'background-color: #81C784; color: black; font-weight: bold'
        else:
            return 'background-color: #E53935; color: white; font-weight: bold'
    except:
        return ''

def apply_screener_styling(df):
    pct_columns = ['WR', 'Position', 'Correlation']
    ratio_columns = ['Inflow Ratio', 'Daily Vol Ratio', 'Vol Ratio']
    
    styled_df = df.copy()
    
    def style_column(col):
        if col.name in pct_columns:
            return [get_color_for_percentage(v) for v in col]
        elif col.name in ratio_columns:
            return [get_color_for_ratio(v) for v in col]
        else:
            return [''] * len(col)
    
    return df.style.apply(style_column)

# --- Main Screener Logic (Live Scan) ---
def run_full_screener():
    results = []

    print("Starting Magic Screener (Live Scan)...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=True, progress=False)

            if df.empty or len(df) < 200:
                continue

            screener_output = run_magic_screener(df.copy(), ticker_item)

            if screener_output:
                results.append(screener_output)

        except Exception as e:
            pass

    print("Magic Screener (Live Scan) finished.")

    if results:
        df_screener_results = pd.DataFrame(results)

        df_screener_results['Price_numeric'] = df_screener_results['Price'].str.replace(',', '').astype(float)
        df_screener_results['1D_Return_numeric'] = df_screener_results['1D Return'].str.rstrip('%').astype(float)
        df_screener_results['WR_numeric'] = df_screener_results['WR'].str.rstrip('%').astype(float)
        df_screener_results = df_screener_results.sort_values(
            by=['WR_numeric', '1D_Return_numeric', 'Price_numeric'],
            ascending=[False, False, False]
        ).reset_index(drop=True)
        df_screener_results = df_screener_results.drop(columns=['Price_numeric', '1D_Return_numeric', 'WR_numeric'])

        return apply_screener_styling(df_screener_results)

    return None