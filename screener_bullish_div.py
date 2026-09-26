# BSJP : Bullish Divergence Screener - Live Screening Module

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- Stock List (IDX Stocks) ---
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']

# --- Helper Functions ---
def apply_fraksi_harga(price):
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

def get_mintick(price):
    price = float(price)
    if price < 200: return 1
    elif 200 <= price <= 500: return 2
    elif 500 < price <= 2000: return 5
    elif 2000 < price <= 5000: return 10
    else: return 25

# --- Main Screener Function ---
def run_bullish_divergence_screener(df, ticker_item, target_date=None):
    if target_date is None:
        target_date = date.today()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()

    if df is None:
        if ticker_item is None:
            return None
        df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=False, progress=False)

    if df.empty:
        return None

    df_copy = df.copy()
    if isinstance(df_copy.columns, pd.MultiIndex):
        df_copy.columns = df_copy.columns.get_level_values(0)
        df_copy = df_copy.loc[:, ~df_copy.columns.duplicated()]

    required_cols = ['High', 'Low', 'Close', 'Volume', 'Open']
    if not all(col in df_copy.columns for col in required_cols):
        return None

    if len(df_copy) < 50:
        return None
    
    df_copy = df_copy[df_copy.index.date <= target_date]
    if len(df_copy) < 50:
        return None

    latest = df_copy.iloc[-1]
    prev = df_copy.iloc[-2]
    current_price = float(latest['Close'])

    low_today = float(latest['Low'])
    low_yesterday = float(prev['Low'])
    high_today = float(latest['High'])
    close_today = float(latest['Close'])
    
    # KRITERIA 1: Low hari ini < Low kemarin (Membuat Lower Low)
    if not (low_today < low_yesterday):
        return None
        
    # KRITERIA 2: Close hari ini harus berada di setengah atas bar (Upper Half)
    if not (close_today >= ((high_today + low_today) / 2.0)):
        return None

    # Hitung Harga Buy dan Stop Loss berdasarkan bar hari ini
    tick = get_mintick(current_price)
    buy_price = high_today + tick
    sl_price = low_today - tick
    
    prev_close = float(df_copy['Close'].iloc[-2]) if len(df_copy) > 1 else current_price
    pct_change_vs_pc = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0

    return {
        'Date': latest.name.strftime('%d/%m/%Y'),
        'Tickers': ticker_item.replace('.JK', ''),
        'Price': f"{apply_fraksi_harga(current_price):,.0f}",
        'Low Today': f"{apply_fraksi_harga(low_today):,.0f}",
        'Low Yesterday': f"{apply_fraksi_harga(low_yesterday):,.0f}",
        'Buy Price': f"{apply_fraksi_harga(buy_price):,.0f}",
        'SL Price': f"{apply_fraksi_harga(sl_price):,.0f}",
        '%C vs PC': f"{pct_change_vs_pc:+.2f}%"
    }

def run_full_screener():
    results = []
    print("Starting Bullish Divergence Screener...")
    for ticker_item in tickers:
        try:
            df = yf.download(ticker_item, period="1y", interval="1d", auto_adjust=False, progress=False)
            if df.empty or len(df) < 50:
                continue
            screener_output = run_bullish_divergence_screener(df.copy(), ticker_item)
            if screener_output:
                results.append(screener_output)
        except Exception:
            pass
            
    print("Screener finished.")
    if results:
        return pd.DataFrame(results)
    return None