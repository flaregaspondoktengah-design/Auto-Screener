# BSJP : Backtest Bullish Harami - Historical Trade Analysis Module
# Module untuk backtest strategi Bullish Harami per ticker

import yfinance as yf
import pandas as pd
import numpy as np

# --- Strategy Parameters ---
HIGH_TARGET_PCT = 1.36    # Target profit jika high tercapai
CLOSE_TARGET_PCT = 0.36   # Target profit jika close tercapai
MIN_VALUE_BILLION = 1     # Minimum transaction value (billion)
MIN_PRICE = 100           # Minimum price

# --- Stock List ---
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ACST.JK', 'ADCP.JK', 'ADES.JK', 'ADHI.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AIMS.JK', 'AISA.JK', 'AKKU.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANDI.JK', 'ANJT.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARGO.JK', 'ARII.JK', 'ARNA.JK', 'ARTA.JK', 'ASGR.JK', 'ASHA.JK', 'ASII.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BAIK.JK', 'BANK.JK', 'BAPI.JK', 'BATA.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BEEF.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BNBR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRPT.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUKK.JK', 'BULL.JK', 'BUMI.JK', 'BUVA.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CBDK.JK', 'CBPE.JK', 'CBRE.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNKO.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRAB.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DAAZ.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DKHH.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EDGE.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FITT.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FUTR.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTBO.JK', 'GTRA.JK', 'GTSI.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HERO.JK', 'HEXA.JK', 'HGII.JK', 'HITS.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRME.JK', 'HRUM.JK', 'HUMI.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INCO.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDX.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCC.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JSPT.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KDTN.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KRYA.JK', 'KSIX.JK', 'KUAS.JK', 'LABA.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LCKM.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPKR.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MGNA.JK', 'MHKI.JK', 'MICE.JK', 'MIDI.JK', 'MIKA.JK', 'MINA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MPRO.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTFN.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASA.JK', 'NASI.JK', 'NCKL.JK', 'NELY.JK', 'NEST.JK', 'NETV.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NPGF.JK', 'NRCA.JK', 'NTBK.JK', 'NZIA.JK', 'OASA.JK', 'OBAT.JK', 'OBMD.JK', 'OILS.JK', 'OKAS.JK', 'OMED.JK', 'OMRE.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANI.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PBSA.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGEO.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PIPA.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'PNSE.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PPRO.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PWON.JK', 'PZZA.JK', 'RAAM.JK', 'RAFI.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'RDTX.JK', 'RGAS.JK', 'RIGS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'RONY.JK', 'ROTI.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SHIP.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SONA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAMU.JK', 'TAPG.JK', 'TARA.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUE.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WEGE.JK', 'WEHA.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WMUU.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZATA.JK', 'ZONE.JK', 'ZYRX.JK']


def get_ticker_list():
    """Return ticker list for dropdown."""
    return [t.replace('.JK', '') for t in tickers]


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


# ==========================================
# MAIN BACKTEST FUNCTION
# ==========================================

def run_backtest_for_ticker(ticker_symbol, period='5y', 
                            high_target=HIGH_TARGET_PCT,
                            close_target=CLOSE_TARGET_PCT):
    """
    Menjalankan backtest untuk satu ticker.
    
    Exit Strategy:
    - Jika Open besok >= target high (1.36%): Profit = high_target
    - Jika High besok >= target high (1.36%): Profit = high_target
    - Jika Close besok >= target close (0.36%): Profit = close_target
    - Jika tidak: Profit = actual close (bisa negatif)
    
    Returns:
        tuple: (DataFrame trades, dict summary)
    """
    # Add .JK suffix if not present
    if not ticker_symbol.endswith('.JK'):
        ticker_symbol = ticker_symbol + '.JK'
    
    # Download data
    df = yf.download(ticker_symbol, period=period, interval="1d", auto_adjust=True, progress=False)
    
    if df.empty:
        return pd.DataFrame(), {'ticker': ticker_symbol.replace('.JK', ''), 'total_trades': 0, 'winning_trades': 0, 'win_rate': 0.0, 'avg_profit_loss': 0.0}
    
    df_copy = df.copy()
    df_copy = _standardize_dataframe(df_copy)
    
    # Check required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df_copy.columns for col in required_cols):
        return pd.DataFrame(), {'ticker': ticker_symbol.replace('.JK', ''), 'total_trades': 0, 'winning_trades': 0, 'win_rate': 0.0, 'avg_profit_loss': 0.0}
    
    if len(df_copy) < 3:
        return pd.DataFrame(), {'ticker': ticker_symbol.replace('.JK', ''), 'total_trades': 0, 'winning_trades': 0, 'win_rate': 0.0, 'avg_profit_loss': 0.0}
    
    detailed_trades = []
    profits_list = []
    
    # Iterate through data
    for i in range(1, len(df_copy) - 1):
        current_day = df_copy.iloc[i]
        prev_day = df_copy.iloc[i-1]
        next_day = df_copy.iloc[i+1]
        
        # Get values
        prev_open = float(prev_day['Open'])
        prev_close = float(prev_day['Close'])
        prev_high = float(prev_day['High'])
        prev_low = float(prev_day['Low'])
        
        current_open = float(current_day['Open'])
        current_close = float(current_day['Close'])
        current_high = float(current_day['High'])
        current_low = float(current_day['Low'])
        current_volume = float(current_day['Volume'])
        
        next_high = float(next_day['High'])
        next_close = float(next_day['Close'])
        next_open = float(next_day['Open'])
        next_low = float(next_day['Low'])
        
        # --- Condition 1: Previous day is a long bearish candle ---
        cond_prev_bearish = prev_close < prev_open
        prev_body_size = abs(prev_open - prev_close)
        prev_range = prev_high - prev_low
        cond_prev_long_body = prev_body_size >= (prev_range * 0.3) if prev_range > 0 else False
        
        # --- Condition 2: Current day is a small bullish candle ---
        cond_current_bullish = current_close > current_open
        current_body_size = abs(current_open - current_close)
        cond_current_small_body = current_body_size < (prev_range * 0.15) if prev_range > 0 else True
        
        # --- Condition 3: Current body engulfed by previous body ---
        cond_engulfed_open = current_open > prev_close and current_open < prev_open
        cond_engulfed_close = current_close < prev_open and current_close > prev_close
        cond_engulfed = cond_engulfed_open and cond_engulfed_close
        
        # --- Condition 4: Additional filters ---
        cond_price_min = current_close >= MIN_PRICE
        transaction_value = (current_close * current_volume) / 1_000_000_000
        cond_high_value = transaction_value >= MIN_VALUE_BILLION
        
        # Check all conditions
        if (cond_prev_bearish and cond_prev_long_body and
            cond_current_bullish and cond_current_small_body and
            cond_engulfed and cond_price_min and cond_high_value):
            
            entry_price = current_close
            target_high_price = entry_price * (1 + high_target / 100)
            target_close_price = entry_price * (1 + close_target / 100)
            
            # Calculate percentages
            pct_vs_pc = ((entry_price - prev_close) / prev_close) * 100
            pct_next_high = ((next_high - entry_price) / entry_price) * 100
            pct_next_close = ((next_close - entry_price) / entry_price) * 100
            pct_next_open = ((next_open - entry_price) / entry_price) * 100
            pct_next_low = ((next_low - entry_price) / entry_price) * 100
            
            # ==========================================
            # EXIT LOGIC & PROFIT CALCULATION
            # ==========================================
            profit_pct = pct_next_close  # default: actual close
            outcome = "Closed"
            
            if next_open >= target_high_price:
                # Gap up beyond target
                profit_pct = pct_next_open
                outcome = "Gap Up"
            elif next_high >= target_high_price:
                # Target high tercapai
                profit_pct = max(high_target, pct_next_close)
                outcome = "Target H"
            elif next_close >= target_close_price:
                # Target close tercapai
                outcome = "Target C"
            else:
                # Tidak ada target tercapai
                outcome = "Miss"
            
            profits_list.append(profit_pct)
            
            # Calculate body percentages for display
            prev_body_pct = (prev_body_size / prev_close) * 100 if prev_close > 0 else 0
            curr_body_pct = (current_body_size / current_close) * 100 if current_close > 0 else 0
            
            detailed_trades.append({
                'Date': current_day.name.strftime('%d-%m-%Y'),
                'Price': f"{round(entry_price):,.0f}",
                '%C vs PC': f"{pct_vs_pc:.2f}%",
                '%H': f"{pct_next_high:.2f}%",
                '%C': f"{pct_next_close:.2f}%",
                '%O': f"{pct_next_open:.2f}%",
                '%L': f"{pct_next_low:.2f}%",
                'Result': f"{profit_pct:.2f}%",
                'Outcome': outcome,
                '1. Prev Red': "☑" if cond_prev_bearish else "",
                '2. Prev Long': "☑" if cond_prev_long_body else "",
                '3. Curr Grn': "☑" if cond_current_bullish else "",
                '4. Curr Sml': "☑" if cond_current_small_body else "",
                '5. Engulf': "☑" if cond_engulfed else ""
            })
    
    # Calculate summary
    total_trades = len(detailed_trades)
    if total_trades == 0:
        return pd.DataFrame(), {
            'ticker': ticker_symbol.replace('.JK', ''),
            'total_trades': 0,
            'winning_trades': 0,
            'win_rate': 0.0,
            'avg_profit_loss': 0.0
        }
    
    # Create DataFrame
    df_trades = pd.DataFrame(detailed_trades)
    
    # Convert date and sort
    df_trades['Date'] = pd.to_datetime(df_trades['Date'])
    df_trades = df_trades.sort_values(by='Date', ascending=False).reset_index(drop=True)
    df_trades['Date'] = df_trades['Date'].dt.strftime('%d/%m/%Y')
    
    # Calculate summary statistics dari profits_list
    winning_trades = sum(1 for p in profits_list if p > 0)
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
    avg_profit_loss = sum(profits_list) / total_trades if total_trades > 0 else 0.0
    
    summary = {
        'ticker': ticker_symbol.replace('.JK', ''),
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate': win_rate,
        'avg_profit_loss': avg_profit_loss
    }
    
    # Select columns for display
    display_cols = [
        'Date', 'Price', '%C vs PC', '%H', '%C', '%O', '%L', 'Result', 'Outcome',
        '1. Prev Red', '2. Prev Long', '3. Curr Grn', '4. Curr Sml', '5. Engulf'
    ]
    df_display = df_trades[display_cols]
    
    return df_display, summary
