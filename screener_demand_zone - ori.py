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
tickers = ['AADI.JK', 'AALI.JK', 'ABMM.JK', 'ACES.JK', 'ADCP.JK', 'ADES.JK', 'ADMG.JK', 'ADMR.JK', 'ADRO.JK', 'AGAR.JK', 'AGII.JK', 'AISA.JK', 'AKPI.JK', 'AKRA.JK', 'AKSI.JK', 'ALDO.JK', 'ALKA.JK', 'AMAN.JK', 'AMFG.JK', 'AMIN.JK', 'ANTM.JK', 'APII.JK', 'APLI.JK', 'APLN.JK', 'ARCI.JK', 'AREA.JK', 'ARII.JK', 'ARNA.JK', 'ASGR.JK', 'ASHA.JK', 'ASLC.JK', 'ASLI.JK', 'ASPI.JK', 'ASPR.JK', 'ASRI.JK', 'ASSA.JK', 'ATAP.JK', 'ATIC.JK', 'ATLA.JK', 'AUTO.JK', 'AVIA.JK', 'AWAN.JK', 'AXIO.JK', 'AYAM.JK', 'AYLS.JK', 'BABY.JK', 'BACH.JK', 'BAIK.JK', 'BALI.JK', 'BANK.JK', 'BAPI.JK', 'BATR.JK', 'BAUT.JK', 'BAYU.JK', 'BBRM.JK', 'BBSS.JK', 'BCIP.JK', 'BDKR.JK', 'BELI.JK', 'BELL.JK', 'BESS.JK', 'BEST.JK', 'BIKE.JK', 'BINO.JK', 'BIPP.JK', 'BIRD.JK', 'BISI.JK', 'BKDP.JK', 'BKSL.JK', 'BLES.JK', 'BLOG.JK', 'BLTA.JK', 'BLTZ.JK', 'BLUE.JK', 'BMHS.JK', 'BMSR.JK', 'BMTR.JK', 'BOAT.JK', 'BOBA.JK', 'BOGA.JK', 'BOLT.JK', 'BRAM.JK', 'BRIS.JK', 'BRMS.JK', 'BRNA.JK', 'BRRC.JK', 'BSBK.JK', 'BSDE.JK', 'BSML.JK', 'BSSR.JK', 'BTPS.JK', 'BUAH.JK', 'BUDI.JK', 'BULL.JK', 'BUMI.JK', 'BWPT.JK', 'BYAN.JK', 'CAKK.JK', 'CAMP.JK', 'CANI.JK', 'CARE.JK', 'CASS.JK', 'CCSI.JK', 'CEKA.JK', 'CGAS.JK', 'CHEK.JK', 'CHEM.JK', 'CINT.JK', 'CITA.JK', 'CITY.JK', 'CLEO.JK', 'CLPI.JK', 'CMNP.JK', 'CMPP.JK', 'CMRY.JK', 'CNMA.JK', 'COAL.JK', 'CPIN.JK', 'CPRO.JK', 'CRSN.JK', 'CSAP.JK', 'CSIS.JK', 'CSMI.JK', 'CSRA.JK', 'CTBN.JK', 'CTRA.JK', 'CYBR.JK', 'DADA.JK', 'DATA.JK', 'DAYA.JK', 'DCII.JK', 'DEFI.JK', 'DEPO.JK', 'DEWA.JK', 'DEWI.JK', 'DGIK.JK', 'DGNS.JK', 'DGWG.JK', 'DILD.JK', 'DIVA.JK', 'DKFT.JK', 'DMAS.JK', 'DMMX.JK', 'DMND.JK', 'DOOH.JK', 'DOSS.JK', 'DRMA.JK', 'DSFI.JK', 'DSNG.JK', 'DSSA.JK', 'DUTI.JK', 'DVLA.JK', 'DWGL.JK', 'DYAN.JK', 'EAST.JK', 'ECII.JK', 'EKAD.JK', 'ELIT.JK', 'ELPI.JK', 'ELSA.JK', 'ELTY.JK', 'EMDE.JK', 'ENAK.JK', 'ENRG.JK', 'EPAC.JK', 'EPMT.JK', 'ERAA.JK', 'ERAL.JK', 'ERTX.JK', 'ESIP.JK', 'ESSA.JK', 'ESTA.JK', 'EXCL.JK', 'FAST.JK', 'FASW.JK', 'FILM.JK', 'FIRE.JK', 'FISH.JK', 'FMII.JK', 'FOLK.JK', 'FOOD.JK', 'FORE.JK', 'FPNI.JK', 'FWCT.JK', 'GDST.JK', 'GDYR.JK', 'GEMA.JK', 'GEMS.JK', 'GGRP.JK', 'GHON.JK', 'GIAA.JK', 'GJTL.JK', 'GLVA.JK', 'GMTD.JK', 'GOLD.JK', 'GOLF.JK', 'GOOD.JK', 'GPRA.JK', 'GPSO.JK', 'GRIA.JK', 'GRPH.JK', 'GTRA.JK', 'GULA.JK', 'GUNA.JK', 'GWSA.JK', 'GZCO.JK', 'HADE.JK', 'HAIS.JK', 'HALO.JK', 'HATM.JK', 'HDIT.JK', 'HEAL.JK', 'HELI.JK', 'HERO.JK', 'HEXA.JK', 'HOKI.JK', 'HOMI.JK', 'HOPE.JK', 'HRTA.JK', 'HRUM.JK', 'HYGN.JK', 'IATA.JK', 'IBST.JK', 'ICBP.JK', 'ICON.JK', 'IDPR.JK', 'IFII.JK', 'IFSH.JK', 'IGAR.JK', 'IIKP.JK', 'IKAI.JK', 'IKAN.JK', 'IKBI.JK', 'IKPM.JK', 'IMPC.JK', 'INCI.JK', 'INDF.JK', 'INDR.JK', 'INDS.JK', 'INDY.JK', 'INET.JK', 'INKP.JK', 'INPP.JK', 'INTD.JK', 'INTP.JK', 'IOTF.JK', 'IPCM.JK', 'IPOL.JK', 'IPTV.JK', 'IRRA.JK', 'IRSX.JK', 'ISAT.JK', 'ISSP.JK', 'ITMA.JK', 'ITMG.JK', 'JARR.JK', 'JAST.JK', 'JATI.JK', 'JAWA.JK', 'JAYA.JK', 'JECC.JK', 'JECX.JK', 'JELI.JK', 'JGLE.JK', 'JIHD.JK', 'JKON.JK', 'JMAS.JK', 'JPFA.JK', 'JRPT.JK', 'JSMR.JK', 'JTPE.JK', 'KAQI.JK', 'KARW.JK', 'KBAG.JK', 'KBLI.JK', 'KBLM.JK', 'KDSI.JK', 'KEEN.JK', 'KEJU.JK', 'KETR.JK', 'KIAS.JK', 'KICI.JK', 'KIJA.JK', 'KINO.JK', 'KIOS.JK', 'KJEN.JK', 'KKES.JK', 'KKGI.JK', 'KLAS.JK', 'KLBF.JK', 'KMDS.JK', 'KOBX.JK', 'KOCI.JK', 'KOIN.JK', 'KOKA.JK', 'KONI.JK', 'KOPI.JK', 'KOTA.JK', 'KPIG.JK', 'KREN.JK', 'KUAS.JK', 'LABS.JK', 'LAJU.JK', 'LAND.JK', 'LION.JK', 'LIVE.JK', 'LMPI.JK', 'LMSH.JK', 'LPCK.JK', 'LPIN.JK', 'LPLI.JK', 'LPPF.JK', 'LRNA.JK', 'LSIP.JK', 'LTLS.JK', 'LUCK.JK', 'MAHA.JK', 'MAIN.JK', 'MAPA.JK', 'MAPB.JK', 'MAPI.JK', 'MARK.JK', 'MAXI.JK', 'MBAP.JK', 'MBMA.JK', 'MBTO.JK', 'MCAS.JK', 'MCOL.JK', 'MDIA.JK', 'MDIY.JK', 'MDKA.JK', 'MDKI.JK', 'MDLA.JK', 'MEDC.JK', 'MEDS.JK', 'MERI.JK', 'MERK.JK', 'META.JK', 'MFMI.JK', 'MHKI.JK', 'MICE.JK', 'MIKA.JK', 'MINE.JK', 'MIRA.JK', 'MITI.JK', 'MKAP.JK', 'MKNT.JK', 'MKPI.JK', 'MKTR.JK', 'MLIA.JK', 'MLPL.JK', 'MLPT.JK', 'MMIX.JK', 'MMLP.JK', 'MNCN.JK', 'MORA.JK', 'MPIX.JK', 'MPMX.JK', 'MPOW.JK', 'MPPA.JK', 'MRAT.JK', 'MSIN.JK', 'MSJA.JK', 'MSKY.JK', 'MSTI.JK', 'MTDL.JK', 'MTEL.JK', 'MTLA.JK', 'MTMH.JK', 'MTPS.JK', 'MTSM.JK', 'MUTU.JK', 'MYOH.JK', 'MYOR.JK', 'NAIK.JK', 'NASI.JK', 'NELY.JK', 'NEST.JK', 'NFCX.JK', 'NICE.JK', 'NICL.JK', 'NIKL.JK', 'NRCA.JK', 'NSSS.JK', 'NTBK.JK', 'NZIA.JK', 'OBAT.JK', 'OBMD.JK', 'OKAS.JK', 'OMED.JK', 'PADA.JK', 'PALM.JK', 'PAMG.JK', 'PANR.JK', 'PART.JK', 'PBID.JK', 'PCAR.JK', 'PDES.JK', 'PDPP.JK', 'PEHA.JK', 'PEVE.JK', 'PGAS.JK', 'PGLI.JK', 'PGUN.JK', 'PICO.JK', 'PJAA.JK', 'PJHB.JK', 'PKPK.JK', 'PLIN.JK', 'PMJS.JK', 'PMUI.JK', 'PNBS.JK', 'PNGO.JK', 'POLI.JK', 'POLU.JK', 'PORT.JK', 'POWR.JK', 'PPRE.JK', 'PPRI.JK', 'PRAY.JK', 'PRDA.JK', 'PRIM.JK', 'PSAB.JK', 'PSAT.JK', 'PSDN.JK', 'PSGO.JK', 'PSKT.JK', 'PSSI.JK', 'PTBA.JK', 'PTIS.JK', 'PTMP.JK', 'PTMR.JK', 'PTPP.JK', 'PTPS.JK', 'PTPW.JK', 'PTSN.JK', 'PTSP.JK', 'PURA.JK', 'PURI.JK', 'PZZA.JK', 'RAAM.JK', 'RAJA.JK', 'RALS.JK', 'RANC.JK', 'RATU.JK', 'RBMS.JK', 'REAL.JK', 'RGAS.JK', 'RISE.JK', 'RMKE.JK', 'RMKO.JK', 'ROCK.JK', 'RODA.JK', 'ROTI.JK', 'RSCH.JK', 'RSGK.JK', 'RUIS.JK', 'SAFE.JK', 'SAGE.JK', 'SAME.JK', 'SAMF.JK', 'SAPX.JK', 'SATU.JK', 'SBMA.JK', 'SCCO.JK', 'SCNP.JK', 'SCPI.JK', 'SDPC.JK', 'SEMA.JK', 'SGER.JK', 'SGRO.JK', 'SHID.JK', 'SICO.JK', 'SIDO.JK', 'SILO.JK', 'SIMP.JK', 'SIPD.JK', 'SKBM.JK', 'SKLT.JK', 'SKRN.JK', 'SLIS.JK', 'SMAR.JK', 'SMBR.JK', 'SMCB.JK', 'SMDM.JK', 'SMDR.JK', 'SMGA.JK', 'SMGR.JK', 'SMIL.JK', 'SMKL.JK', 'SMLE.JK', 'SMMT.JK', 'SMRA.JK', 'SMSM.JK', 'SNLK.JK', 'SOCI.JK', 'SOHO.JK', 'SOLA.JK', 'SOSS.JK', 'SOTS.JK', 'SPMA.JK', 'SPTO.JK', 'SRTG.JK', 'SSIA.JK', 'SSTM.JK', 'STAA.JK', 'STTP.JK', 'SULI.JK', 'SUNI.JK', 'SUPR.JK', 'SURI.JK', 'SWID.JK', 'TALF.JK', 'TAMA.JK', 'TAPG.JK', 'TAXI.JK', 'TBMS.JK', 'TCID.JK', 'TCPI.JK', 'TEBE.JK', 'TFAS.JK', 'TFCO.JK', 'TGKA.JK', 'TGUK.JK', 'TINS.JK', 'TIRA.JK', 'TIRT.JK', 'TKIM.JK', 'TLDN.JK', 'TLKM.JK', 'TMAS.JK', 'TMPO.JK', 'TNCA.JK', 'TOBA.JK', 'TOOL.JK', 'TOSK.JK', 'TOTL.JK', 'TOTO.JK', 'TPIA.JK', 'TPMA.JK', 'TRIS.JK', 'TRJA.JK', 'TRON.JK', 'TRST.JK', 'TRUK.JK', 'TSPC.JK', 'TYRE.JK', 'UANG.JK', 'UCID.JK', 'UFOE.JK', 'ULTJ.JK', 'UNIC.JK', 'UNIQ.JK', 'UNTR.JK', 'UNVR.JK', 'URBN.JK', 'UVCR.JK', 'VAST.JK', 'VERN.JK', 'VICI.JK', 'VISI.JK', 'VKTR.JK', 'VOKS.JK', 'WAPO.JK', 'WBSA.JK', 'WEGE.JK', 'WEHA.JK', 'WIFI.JK', 'WINR.JK', 'WINS.JK', 'WIRG.JK', 'WOOD.JK', 'WOWS.JK', 'WTON.JK', 'YELO.JK', 'YPAS.JK', 'YUPI.JK', 'ZONE.JK', 'ZYRX.JK']


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