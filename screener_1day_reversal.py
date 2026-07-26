# BSJP : 1 Day Reversal Screener - Live Screening Module
# Strategi berdasarkan pola reversal 1 hari (red candle diikuti green candle dengan volume naik)
# Entry: Previous red + Current green + Volume up + High Value

import yfinance as yf
import pandas as pd
import numpy as np

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']

# --- Strategy Parameters ---
HIGH_TARGET_PCT = 1.36    # Target profit jika high tercapai
CLOSE_TARGET_PCT = 0.36   # Target profit jika close tercapai
MIN_VALUE_BILLION = 5     # Minimum transaction value (billion)
MIN_PRICE = 100           # Minimum price


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _standardize_dataframe(df):
    """Standardisasi nama kolom DataFrame."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    new_columns = []
    for col in df.columns:
        if col.lower() == 'adj close':
            new_columns.append('Close')
        else:
            new_columns.append(col.capitalize())
    
    df.columns = new_columns
    df = df.loc[:, ~df.columns.duplicated(keep='last')]
    return df


def calculate_moving_averages(df):
    """Menghitung Moving Averages dan VWAP."""
    df_copy = df.copy()
    
    # Moving Averages
    df_copy['MA5'] = df_copy['Close'].rolling(window=5).mean()
    df_copy['MA10'] = df_copy['Close'].rolling(window=10).mean()
    df_copy['MA20'] = df_copy['Close'].rolling(window=20).mean()
    df_copy['MA50'] = df_copy['Close'].rolling(window=50).mean()
    df_copy['MA200'] = df_copy['Close'].rolling(window=200).mean()
    
    # VWAP Daily
    if 'High' in df_copy.columns and 'Low' in df_copy.columns:
        df_copy['VWAP_Daily'] = (df_copy['High'] + df_copy['Low'] + df_copy['Close']) / 3
    else:
        df_copy['VWAP_Daily'] = np.nan
    
    # Volume MA
    df_copy['Volume_MA_5'] = df_copy['Volume'].rolling(window=5).mean()
    df_copy['Volume_MA_20'] = df_copy['Volume'].rolling(window=20).mean()
    
    return df_copy


def get_15min_data(ticker, period='1mo'):
    """Mengambil data 15 menit untuk analisis intraday."""
    try:
        df = yf.download(ticker, period=period, interval='15m', progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None


def calculate_intraday_score(df_15m, daily_high, daily_low, daily_close):
    """Menghitung skor intraday (0-10) untuk overnight trading."""
    if df_15m is None or len(df_15m) < 10:
        return {
            'score': 0,
            'position': 'N/A',
            'momentum': 'N/A',
            'volume_ratio': 'N/A',
            'signal': 'NO DATA'
        }
    
    try:
        last_date = df_15m.index[-1].date()
        df_today = df_15m[df_15m.index.date == last_date]
        
        if len(df_today) < 5:
            return {
                'score': 0,
                'position': 'N/A',
                'momentum': 'N/A',
                'volume_ratio': 'N/A',
                'signal': 'INSUFFICIENT DATA'
            }
        
        score = 0
        
        # 1. Close Position (Max 3)
        today_range = daily_high - daily_low
        if today_range > 0:
            close_position = (daily_close - daily_low) / today_range
        else:
            close_position = 0.5
        
        if close_position > 0.7:
            score += 3
            position_status = 'High'
        elif close_position > 0.5:
            score += 2
            position_status = 'Good'
        elif close_position > 0.3:
            score += 1
            position_status = 'Fair'
        else:
            position_status = 'Low'
        
        # 2. Momentum Hybrid (Max 3)
        last = df_today.iloc[-1]
        prev = df_today.iloc[-2] if len(df_today) >= 2 else None
        
        momentum_score = 0
        candle_15m_bullish = last['Close'] > last['Open']
        if candle_15m_bullish:
            momentum_score += 1
        
        momentum_15m = (last['Close'] - last['Open']) / last['Open'] * 100 if last['Open'] > 0 else 0
        if momentum_15m > 0:
            momentum_score += 1
        
        if prev is not None:
            prev_bullish = prev['Close'] > prev['Open']
            if candle_15m_bullish and prev_bullish:
                momentum_score += 1
        
        score += momentum_score
        momentum_status = f"+{momentum_15m:.2f}%" if momentum_15m >= 0 else f"{momentum_15m:.2f}%"
        
        # 3. Volume Ratio (Max 2)
        avg_volume = df_today['Volume'].mean()
        last_volume = last['Volume']
        volume_ratio = last_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:
            score += 2
            volume_status = 'High'
        elif volume_ratio > 1.0:
            score += 1
            volume_status = 'Normal'
        else:
            volume_status = 'Low'
        
        # 4. Sore Trend (Max 2)
        try:
            afternoon = df_today.between_time('12:00', '15:30')
            if len(afternoon) > 1:
                aft_open = afternoon['Open'].iloc[0]
                aft_close = afternoon['Close'].iloc[-1]
                afternoon_trend = (aft_close - aft_open) / aft_open * 100 if aft_open > 0 else 0
            else:
                afternoon_trend = 0
        except Exception:
            afternoon_trend = 0
        
        if afternoon_trend > 0.5:
            score += 2
        elif afternoon_trend > 0:
            score += 1
        
        # Signal Determination
        if score >= 9:
            signal = 'STRONG BUY'
        elif score >= 7:
            signal = 'BUY'
        elif score >= 5:
            signal = 'CONSIDER'
        elif score >= 3:
            signal = 'WEAK'
        else:
            signal = 'AVOID'
        
        return {
            'score': score,
            'position': f"{close_position*100:.0f}%",
            'momentum': momentum_status,
            'volume_ratio': f"{volume_ratio:.1f}x",
            'signal': signal
        }
        
    except Exception:
        return {
            'score': 0,
            'position': 'N/A',
            'momentum': 'N/A',
            'volume_ratio': 'N/A',
            'signal': 'ERROR'
        }


# ==========================================
# BACKTEST SUMMARY FUNCTION
# ==========================================

def _calculate_backtest_summary(df, high_target=HIGH_TARGET_PCT, close_target=CLOSE_TARGET_PCT):
    """Menghitung metrik ringkasan backtest untuk strategi 1 Day Reversal."""
    df_copy = df.copy()
    df_copy = _standardize_dataframe(df_copy)
    
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df_copy.columns for col in required_cols):
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}
    
    try:
        df_copy = calculate_moving_averages(df_copy)
    except Exception:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}
    
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5'])
    
    if len(df_copy) < 3:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}
    
    trade_profits = []
    
    for i in range(1, len(df_copy) - 1):
        current_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i-1]
        next_day = df_copy.iloc[i+1]
        
        # Get values
        current_close = float(current_day['Close'])
        current_open = float(current_day['Open'])
        current_volume = float(current_day['Volume'])
        prev_close = float(prev_day['Close'])
        prev_open = float(prev_day['Open'])
        prev_volume = float(prev_day['Volume'])
        
        next_high = float(next_day['High'])
        next_close = float(next_day['Close'])
        next_open = float(next_day['Open'])
        
        # Entry Conditions
        cond_volume_up = current_volume > prev_volume
        cond_prev_red = prev_close < prev_open
        cond_current_green = current_close > current_open
        cond_price_min = current_close >= MIN_PRICE
        transaction_value = (current_close * current_volume) / 1_000_000_000
        cond_high_value = transaction_value >= MIN_VALUE_BILLION
        
        # Check all conditions
        if cond_volume_up and cond_prev_red and cond_current_green and cond_price_min and cond_high_value:
            entry_price = current_close
            target_high = entry_price * (1 + high_target / 100)
            target_close = entry_price * (1 + close_target / 100)
            
            # Exit logic
            if next_open >= target_high:
                trade_profits.append(high_target)
            elif next_high >= target_high:
                trade_profits.append(high_target)
            elif next_close >= target_close:
                trade_profits.append(close_target)
            else:
                trade_profits.append(((next_close - entry_price) / entry_price) * 100)
    
    total_trades_count = len(trade_profits)
    if total_trades_count == 0:
        return {'win_rate': 0.0, 'avg_profit_loss': 0.0, 'total_trades': 0}
    
    winning_trades_count = sum(1 for pnl in trade_profits if pnl > 0)
    overall_win_rate = (winning_trades_count / total_trades_count) * 100
    overall_avg_profit_loss = sum(trade_profits) / total_trades_count
    
    return {
        'win_rate': overall_win_rate,
        'avg_profit_loss': overall_avg_profit_loss,
        'total_trades': total_trades_count
    }


# ==========================================
# MAIN SCREENER FUNCTION
# ==========================================

def run_1day_reversal_screener(df, ticker_item, target_date=None):
    """
    Memeriksa apakah saham memenuhi kriteria 1 Day Reversal untuk hari terakhir.
    
    Entry Conditions:
    1. Volume Up: Current volume > Previous volume
    2. Previous Red Candle: Previous close < Previous open
    3. Current Green Candle: Current close > Current open
    4. Price >= 100
    5. Transaction Value >= 5 Billion
    
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
    df_copy = _standardize_dataframe(df_copy)
    
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df_copy.columns for col in required_cols):
        return None
    
    try:
        df_copy = calculate_moving_averages(df_copy)
    except Exception:
        return None
    
    df_copy = df_copy.dropna(subset=['MA5', 'MA10', 'MA20', 'MA50', 'MA200', 'Volume', 'Close', 'Open', 'High', 'Low', 'Volume_MA_20', 'VWAP_Daily', 'Volume_MA_5'])
    
    if len(df_copy) < 2:
        return None
    
    # Filter data sampai target_date
    df_copy = df_copy[df_copy.index.date <= target_date]
    
    if len(df_copy) < 2:
        return None
    
    latest = df_copy.iloc[-1]
    previous = df_copy.iloc[-2]
    
    # Get latest values
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
    
    prev_close = float(previous['Close'])
    prev_open = float(previous['Open'])
    prev_volume = float(previous['Volume'])
    prev_high = float(previous['High'])
    prev_low = float(previous['Low'])
    prev_vwap = float(previous['VWAP_Daily'])
    
    transaction_value = (latest_close * latest_volume) / 1_000_000_000
    
    # Entry Conditions
    cond_volume_up = latest_volume > prev_volume
    cond_prev_red = prev_close < prev_open
    cond_current_green = latest_close > latest_open
    cond_price_min = latest_close >= MIN_PRICE
    cond_high_value = transaction_value >= MIN_VALUE_BILLION
    
    # Check all conditions
    if cond_volume_up and cond_prev_red and cond_current_green and cond_price_min and cond_high_value:
        
        # Calculate backtest summary
        backtest_df = yf.download(ticker_item, period="5y", interval="1d", auto_adjust=True, progress=False)
        backtest_metrics = _calculate_backtest_summary(backtest_df)
        
        # Intraday Analysis
        df_15m = get_15min_data(ticker_item)
        intraday = calculate_intraday_score(df_15m, latest_high, latest_low, latest_close)
        
        # Additional metrics
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        pct_h_vs_c = abs(latest_high - latest_close) / latest_close * 100 if latest_close > 0 else 0
        pct_o_vs_l = abs(latest_open - latest_low) / latest_low * 100 if latest_low > 0 else 0
        
        # Remarks (not filters)
        cond_ma_uptrend = (latest_ma5 > latest_ma10 and latest_ma10 > latest_ma20 and 
                          latest_ma20 > latest_ma50 and latest_ma50 > latest_ma200)
        cond_vol_above_ma20 = latest_volume > latest_volume_ma_20
        cond_low_above_prev_low = latest_low > prev_low
        cond_high_above_prev_high = latest_high > prev_high
        cond_open_eq_prev_close = latest_open == prev_close
        cond_ol_gt_hc = (latest_open - latest_low) > (latest_high - latest_close)
        cond_close_above_vwap = latest_close > latest_vwap
        cond_prev_close_below_prev_vwap = prev_close < prev_vwap
        cond_vol_above_ma5 = latest_volume > latest_volume_ma_5
        
        return {
            'Date': latest.name.strftime('%d/%m/%Y'),
            'Tickers': ticker_item.replace('.JK', ''),
            'Price': f"{latest_close:,.0f}",
            'WR': f"{backtest_metrics['win_rate']:.1f}%",
            'Trades': f"{backtest_metrics['total_trades']:.0f}",
            '%C vs PC': f"{pct_change:.2f}%",
            'Value(B)': f"{transaction_value:.2f}",
            '%H vs C': f"{pct_h_vs_c:.2f}%",
            '%O vs L': f"{pct_o_vs_l:.2f}%",
            '1. PR': "☑" if cond_prev_red else "",
            '2. V>MA20': "☑" if cond_vol_above_ma20 else "",
            '3. MA+': "☑" if cond_ma_uptrend else "",
            '4. L>PL': "☑" if cond_low_above_prev_low else "",
            '5. H>PH': "☑" if cond_high_above_prev_high else "",
            '6. O=PC': "☑" if cond_open_eq_prev_close else "",
            '7. OL>HC': "☑" if cond_ol_gt_hc else "",
            '8. C>VWAP': "☑" if cond_close_above_vwap else "",
            '9. PC<PVWAP': "☑" if cond_prev_close_below_prev_vwap else "",
            '10. V>MA5': "☑" if cond_vol_above_ma5 else "",
            # Intraday Analysis
            'Score': f"{intraday['score']}/10",
            'Position': intraday['position'],
            'Momentum': intraday['momentum'],
            'Vol Ratio': intraday['volume_ratio'],
            'Signal': intraday['signal']
        }
    
    return None


# --- Main Screener Logic (Live Scan) ---
def run_full_1day_reversal_screener():
    """Menjalankan full screener untuk semua ticker."""
    results = []
    
    print("Starting 1 Day Reversal Screener (Live Scan)...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=True, progress=False)
            
            if df.empty or len(df) < 200:
                continue
            
            screener_output = run_1day_reversal_screener(df.copy(), ticker_item)
            
            if screener_output:
                results.append(screener_output)
        
        except Exception:
            pass
    
    print("1 Day Reversal Screener (Live Scan) finished.")
    
    if results:
        df_results = pd.DataFrame(results)
        
        # Sort by WR
        df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
        df_results = df_results.sort_values(by=['WR_numeric'], ascending=[False]).reset_index(drop=True)
        df_results = df_results.drop(columns=['WR_numeric'])
        
        return df_results
    
    return None