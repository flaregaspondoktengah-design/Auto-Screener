# BSJP : Stock Screener Streamlit Application
# Aplikasi untuk screening saham Indonesia dengan berbagai jenis screener:
# 1. Magic Screener V1.1 - Live screening
# 2. Backtest Magic Screener V1.1 - Historical analysis
# 3. Magic Screener V1.3 - Live screening (3 days consecutive green)
# 4. Backtest Magic Screener V1.3 - Historical analysis
# 5. BB Reversal - Live screening (Bollinger Band reversal)
# 6. Backtest BB Reversal - Historical analysis
# 7. IV Rank - Live screening (Implied Volatility Rank)
# 8. Backtest IV Rank - Historical analysis
# 9. Bullish Harami - Live screening (Candlestick pattern)
# 10. Backtest Bullish Harami - Historical analysis
# 11. 1 Day Reversal - Live screening (Red to Green reversal)
# 12. Backtest 1 Day Reversal - Historical analysis
# 13. Decreasing Highs - Live screening (4 days decreasing highs)
# 14. Backtest Decreasing Highs - Historical analysis
# 15. Sideways Screener - Live screening (MA Cluster detection)
# 16. Backtest Sideways Screener - Historical analysis
# 17. FVG Screener - Live screening (Fair Value Gap detection)
# 18. Backtest FVG Screener - Historical analysis
# 19. Oversold Screener - RSI & Stochastic oversold detection
# 20. Backtest Oversold Screener - Historical analysis
# 21. Demand Zone Screener - Stocks in demand zone area
# 22. Volume Profile Screener - Stocks below VAL (Lookback 20)

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime

# Import screener modules
from screener_v11 import run_magic_screener, tickers as tickers_v11
from backtest_screener_v11 import run_backtest_for_ticker, get_ticker_list as get_ticker_list_v11
from screener_v13 import run_magic_screener_v13, tickers as tickers_v13
from backtest_screener_v13 import run_backtest_for_ticker_v13, get_ticker_list as get_ticker_list_v13
from screener_bb_reversal import run_bb_reversal_screener, tickers as tickers_bb
from backtest_bb_reversal import run_backtest_bb_reversal_for_ticker, get_ticker_list as get_ticker_list_bb
from screener_iv_rank import run_iv_rank_screener, tickers as tickers_iv
from backtest_screener_iv_rank import run_backtest_for_ticker as run_backtest_iv_rank, get_ticker_list as get_ticker_list_iv
from screener_bullish_harami import run_bullish_harami_screener, tickers as tickers_bh
from backtest_bullish_harami import run_backtest_for_ticker as run_backtest_bh, get_ticker_list as get_ticker_list_bh
from screener_1day_reversal import run_1day_reversal_screener, tickers as tickers_1dr
from backtest_1day_reversal import run_backtest_for_ticker as run_backtest_1dr, get_ticker_list as get_ticker_list_1dr
from screener_decreasing_highs import run_decreasing_highs_screener, tickers as tickers_dh
from backtest_decreasing_highs import run_backtest_for_ticker as run_backtest_dh, get_ticker_list as get_ticker_list_dh
from screener_sideways import run_sideways_screener, tickers as tickers_dz
from backtest_sideways import run_backtest_for_ticker as run_backtest_dz, get_ticker_list as get_ticker_list_dz
from screener_fvg import run_fvg_screener, tickers as tickers_fvg
from backtest_fvg import run_backtest_for_ticker as run_backtest_fvg, get_ticker_list as get_ticker_list_fvg
from screener_oversold import run_oversold_screener, tickers as tickers_os
from backtest_oversold import run_backtest_for_ticker as run_backtest_os, get_ticker_list as get_ticker_list_os
from screener_demand_zone import run_demand_zone_screener, tickers as tickers_dmz, get_stock_demand_supply
from screener_volume_trend import run_volume_trend_screener, run_full_volume_trend_screener, tickers as tickers_vt, get_ticker_list as get_ticker_list_vt
from screener_vp import run_vp_screener, tickers as tickers_vp

# --- Page Configuration ---
st.set_page_config(
    page_title="Auto Stock Screener",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 10rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #000000;
        background-color: #1E88E5;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .summary-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e3f2fd;
        border: 1px solid #bbdefb;
        color: #0d47a1;
    }
    .screener-section {
        background-color: #fafafa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    /* Gray color for Buy Criteria expander */
    .streamlit-expanderHeader {
        color: #757575 !important;
    }
    div[data-testid="stExpander"] summary p {
        color: #757575 !important;
    }
    /* Custom checkbox styling for dataframe */
    .checkbox-checked {
        font-size: 1.5rem;
        color: #28a745;
        font-weight: bold;
    }
    .checkbox-unchecked {
        font-size: 1.5rem;
        color: #dc3545;
        font-weight: bold;
    }
    /* Style for custom HTML table */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .custom-table th {
        background-color: #1E88E5;
        color: white;
        padding: 8px 6px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #1565C0;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 6px;
        text-align: center;
        border: 1px solid #e0e0e0;
        white-space: nowrap;
    }
    .custom-table tr:nth-child(even) {
        background-color: #f5f5f5;
    }
    .custom-table tr:hover {
        background-color: #e3f2fd;
    }
    .check-yes {
        font-size: 1.4rem;
        color: #28a745;
    }
    .signal-strong-buy {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .signal-buy {
        background-color: #5cb85c;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .signal-consider {
        background-color: #ffc107;
        color: black;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .signal-weak {
        background-color: #fd7e14;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .signal-avoid {
        background-color: #dc3545;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    /* Color cells following signal pattern - badge style */
    .cell-green {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .cell-yellow {
        background-color: #ffc107;
        color: black;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .cell-orange {
        background-color: #fd7e14;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .cell-red {
        background-color: #dc3545;
        color: white;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
# Magic Screener V1.1
if 'v11_results' not in st.session_state:
    st.session_state.v11_results = None

# Backtest V1.1
if 'v11_bt_results' not in st.session_state:
    st.session_state.v11_bt_results = None
if 'v11_bt_summary' not in st.session_state:
    st.session_state.v11_bt_summary = None

# Magic Screener V1.3
if 'v13_results' not in st.session_state:
    st.session_state.v13_results = None

# Backtest V1.3
if 'v13_bt_results' not in st.session_state:
    st.session_state.v13_bt_results = None
if 'v13_bt_summary' not in st.session_state:
    st.session_state.v13_bt_summary = None

# BB Reversal
if 'bb_results' not in st.session_state:
    st.session_state.bb_results = None

# Backtest BB Reversal
if 'bb_bt_results' not in st.session_state:
    st.session_state.bb_bt_results = None
if 'bb_bt_summary' not in st.session_state:
    st.session_state.bb_bt_summary = None

# IV Rank
if 'iv_results' not in st.session_state:
    st.session_state.iv_results = None

# Backtest IV Rank
if 'iv_bt_results' not in st.session_state:
    st.session_state.iv_bt_results = None
if 'iv_bt_summary' not in st.session_state:
    st.session_state.iv_bt_summary = None

# Bullish Harami
if 'bh_results' not in st.session_state:
    st.session_state.bh_results = None

# Backtest Bullish Harami
if 'bh_bt_results' not in st.session_state:
    st.session_state.bh_bt_results = None
if 'bh_bt_summary' not in st.session_state:
    st.session_state.bh_bt_summary = None

# 1 Day Reversal
if 'dr_results' not in st.session_state:
    st.session_state.dr_results = None

# Backtest 1 Day Reversal
if 'dr_bt_results' not in st.session_state:
    st.session_state.dr_bt_results = None
if 'dr_bt_summary' not in st.session_state:
    st.session_state.dr_bt_summary = None

# Decreasing Highs
if 'dh_results' not in st.session_state:
    st.session_state.dh_results = None

# Backtest Decreasing Highs
if 'dh_bt_results' not in st.session_state:
    st.session_state.dh_bt_results = None
if 'dh_bt_summary' not in st.session_state:
    st.session_state.dh_bt_summary = None

# Sideways Screener
if 'dz_results' not in st.session_state:
    st.session_state.dz_results = None

# Backtest Sideways Screener
if 'dz_bt_results' not in st.session_state:
    st.session_state.dz_bt_results = None
if 'dz_bt_summary' not in st.session_state:
    st.session_state.dz_bt_summary = None

# FVG Screener
if 'fvg_results' not in st.session_state:
    st.session_state.fvg_results = None

# Backtest FVG Screener
if 'fvg_bt_results' not in st.session_state:
    st.session_state.fvg_bt_results = None
if 'fvg_bt_summary' not in st.session_state:
    st.session_state.fvg_bt_summary = None

# Oversold Screener
if 'os_results' not in st.session_state:
    st.session_state.os_results = None

# Backtest Oversold Screener
if 'os_bt_results' not in st.session_state:
    st.session_state.os_bt_results = None
if 'os_bt_summary' not in st.session_state:
    st.session_state.os_bt_summary = None

# Demand Zone Screener
if 'dmz_results' not in st.session_state:
    st.session_state.dmz_results = None

# Demand/Supply Lookup
if 'dmz_lookup' not in st.session_state:
    st.session_state.dmz_lookup = None

# Volume Trend Screener
if 'vt_results' not in st.session_state:
    st.session_state.vt_results = None

# Volume Profile Screener
if 'vp_results' not in st.session_state:
    st.session_state.vp_results = None


# --- Helper Functions ---
def scroll_to_section(section_id):
    """JavaScript to scroll to a specific section."""
    js_code = f'''
    <script>
        var section = document.getElementById("{section_id}");
        if (section) {{
            section.scrollIntoView({{behavior: "smooth", block: "start"}});
        }}
    </script>
    '''
    st.components.v1.html(js_code, height=0)

def clear_all():
    """Clear all results"""
    st.session_state.v11_results = None
    st.session_state.v11_bt_results = None
    st.session_state.v11_bt_summary = None
    st.session_state.v13_results = None
    st.session_state.v13_bt_results = None
    st.session_state.v13_bt_summary = None
    st.session_state.bb_results = None
    st.session_state.bb_bt_results = None
    st.session_state.bb_bt_summary = None
    st.session_state.iv_results = None
    st.session_state.iv_bt_results = None
    st.session_state.iv_bt_summary = None
    st.session_state.bh_results = None
    st.session_state.bh_bt_results = None
    st.session_state.bh_bt_summary = None
    st.session_state.dr_results = None
    st.session_state.dr_bt_results = None
    st.session_state.dr_bt_summary = None
    st.session_state.dh_results = None
    st.session_state.dh_bt_results = None
    st.session_state.dh_bt_summary = None
    st.session_state.dz_results = None
    st.session_state.dz_bt_results = None
    st.session_state.dz_bt_summary = None
    st.session_state.fvg_results = None
    st.session_state.fvg_bt_results = None
    st.session_state.fvg_bt_summary = None
    st.session_state.os_results = None
    st.session_state.os_bt_results = None
    st.session_state.os_bt_summary = None
    st.session_state.dmz_results = None
    st.session_state.dmz_lookup = None
    st.session_state.vt_results = None
    st.session_state.vp_results = None


def get_dates_in_range(date_input):
    """
    Mengembalikan list tanggal dari date_input.
    Jika single date, kembalikan list dengan 1 tanggal.
    Jika date range (tuple), kembalikan semua tanggal dalam range.
    
    Args:
        date_input: date object atau tuple (start_date, end_date) atau tuple dengan 1 elemen
    
    Returns:
        list of date objects
    """
    if isinstance(date_input, tuple):
        # Handle tuple dengan panjang berbeda
        if len(date_input) == 0:
            return [date.today()]
        elif len(date_input) == 1:
            # Single date dalam tuple
            single_date = date_input[0]
            if single_date is None:
                return [date.today()]
            return [single_date]
        else:
            # Tuple dengan 2 elemen (start_date, end_date)
            start_date, end_date = date_input
            if start_date is None:
                return [date.today()]
            if end_date is None:
                return [start_date]
            dates = []
            current = start_date
            while current <= end_date:
                dates.append(current)
                current += timedelta(days=1)
            return dates
    else:
        # Single date object
        if date_input is None:
            return [date.today()]
        return [date_input]


def format_signal(signal):
    """Format signal with appropriate CSS class."""
    signal_classes = {
        'STRONG BUY': 'signal-strong-buy',
        'BUY': 'signal-buy',
        'CONSIDER': 'signal-consider',
        'WEAK': 'signal-weak',
        'AVOID': 'signal-avoid'
    }
    cls = signal_classes.get(signal, '')
    return f'<span class="{cls}">{signal}</span>'


def get_color_class_for_percentage(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai persentase.
    Mengikuti pola signal: STRONG BUY/BUY (>=80) = hijau, CONSIDER (60-79.99) = kuning, WEAK (50-59.99) = orange, AVOID (<50) = merah
    """
    try:
        value = float(str(value_str).replace('%', '').replace('x', '').strip())
        if value >= 80:
            return 'cell-green'       # STRONG BUY / BUY
        elif value >= 60:
            return 'cell-yellow'       # CONSIDER
        elif value >= 50:
            return 'cell-orange'       # WEAK
        else:
            return 'cell-red'          # AVOID
    except:
        return ''


def get_color_class_for_ratio(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai rasio.
    Mengikuti pola signal: STRONG BUY/BUY (>2x) = hijau, CONSIDER (1.5-2x) = kuning, WEAK (1-1.49x) = orange, AVOID (<1x) = merah
    """
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value > 2:
            return 'cell-green'        # STRONG BUY / BUY
        elif value >= 1.5:
            return 'cell-yellow'       # CONSIDER
        elif value >= 1:
            return 'cell-orange'       # WEAK
        else:
            return 'cell-red'          # AVOID
    except:
        return ''


def get_color_class_for_rrr(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai RRR (Risk-Reward Ratio).
    Kriteria:
    - >=2.0x: Green (target jauh, risk kecil)
    - >1.5x-1.9x: Yellow
    - >=1.0x-1.5x: Orange
    - <1.0x: Red (risk lebih besar dari reward)
    """
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value >= 2:
            return 'cell-green'
        elif value > 1.5:
            return 'cell-yellow'
        elif value >= 1:
            return 'cell-orange'
        else:
            return 'cell-red'
    except:
        return ''


def get_color_class_for_compression_ratio(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai Compression Ratio (ATR 5 / ATR 20).
    Semakin rendah = semakin bagus (volatilitas menurun, potensi breakout).
    Kriteria:
    - <= 0.8: Green (strong compression)
    - 0.81 - 1.0: Yellow
    - 1.01 - 1.2: Orange
    - > 1.2: Red (no compression)
    """
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value <= 0.8:
            return 'cell-green'
        elif value <= 1.0:
            return 'cell-yellow'
        elif value <= 1.2:
            return 'cell-orange'
        else:
            return 'cell-red'
    except:
        return ''


def get_color_class_for_spread(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai Spread% (MA clustering).
    Semakin rendah = semakin bagus (MA lebih rapat, sideways lebih jelas).
    Kriteria:
    - <= 1%: Green (very tight cluster)
    - 1.01% - 2%: Yellow
    - 2.01% - 3%: Orange
    - > 3%: Red (not clustered)
    """
    try:
        value = float(str(value_str).replace('%', '').replace('x', '').strip())
        if value <= 1:
            return 'cell-green'
        elif value <= 2:
            return 'cell-yellow'
        elif value <= 3:
            return 'cell-orange'
        else:
            return 'cell-red'
    except:
        return ''


def get_color_class_for_pct_change(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai persentase perubahan harga (%C vs PC).
    Positif = hijau, negatif = merah.
    """
    try:
        value = float(str(value_str).replace('%', '').replace('+', '').strip())
        if value > 0:
            return 'cell-green'       # Harga naik
        elif value < 0:
            return 'cell-red'         # Harga turun
        else:
            return ''                 # Tidak berubah
    except:
        return ''


def get_color_class_for_position(value_str):
    """
    Mengembalikan class CSS berdasarkan nilai Position.
    Bullish = hijau, Bearish = merah, Neutral = kuning.
    """
    value_str = str(value_str).strip()
    if value_str == 'Bullish':
        return 'cell-green'
    elif value_str == 'Bearish':
        return 'cell-red'         # <-- TAMBAHKAN BARIS INI
    elif value_str == 'Neutral':
        return 'cell-yellow'
    return ''


def get_color_class_for_vt_signal(value_str):
    """
    Mengembalikan class CSS berdasarkan Volume Trend Signal.
    Accumulation = hijau, Distribution = merah, Hidden = kuning.
    """
    value_str = str(value_str).strip()
    if value_str == 'STRONG ACCUMULATION':
        return 'cell-green'
    elif value_str == 'ACCUMULATION':
        return 'cell-green'
    elif value_str == 'HIDDEN ACCUMULATION':
        return 'cell-yellow'
    elif value_str == 'NEUTRAL':
        return ''
    elif value_str == 'HIDDEN DISTRIBUTION':
        return 'cell-yellow'
    elif value_str == 'DISTRIBUTION':
        return 'cell-red'
    elif value_str == 'STRONG DISTRIBUTION':
        return 'cell-red'
    return ''


def format_colored_cell(value, css_class):
    """Format cell with color class."""
    if css_class:
        return f'<span class="{css_class}">{value}</span>'
    return str(value)


def display_results_table(df, key_prefix=""):
    """
    Display results dataframe with styled checkboxes, signal, and colored cells.
    Uses HTML table for better control over styling.
    """
    if df is None or df.empty:
        return
    
    # Kolom yang menggunakan format persentase (>=80, 50-79.99, <50)
    pct_columns = ['WR', 'Correlation']
    
    # Kolom Position dengan warna khusus (Bullish=hijau, Neutral=kuning)
    position_column = 'Position'
    
    # Kolom yang menggunakan format rasio (>2, 1-1.99, <1)
    ratio_columns = ['Inflow Ratio', 'Vol Ratio', 'Daily Vol Ratio']
    
    # Kolom Avg Val 20D dengan kriteria warna khusus
    avg_val_column = 'Avg Val 20D (B)'
    
    # Kolom RRR dengan kriteria warna berbeda
    rrr_column = 'RRR'
    
    # Kolom Compression Ratio dengan kriteria warna khusus (lower is better)
    compression_ratio_column = 'Compression Ratio'
    
    # Kolom Spread% dengan kriteria warna khusus (lower is better)
    spread_column = 'Spread%'
    
    # Kolom %C vs PC dengan warna hijau/merah
    pct_change_column = '%C vs PC'
    
    # Kolom OBV Trend dan PVT Trend
    obv_trend_column = 'OBV Trend'
    pvt_trend_column = 'PVT Trend'
    
    # OBV Divergence column
    obv_div_column = 'OBV Div'
    
    # MACD Divergence column (MYCD)
    macd_div_column = 'MACD Div'
    
    # CMF column
    cmf_column = 'CMF'
    
    # Convert dataframe to HTML table with custom styling
    html = '<table class="custom-table"><thead><tr>'
    
    # Add headers
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    # Add rows
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            
            # Check if this is a criteria column (checkboxes)
            if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) or col in ('RSI OS', 'Stoch OS'):
                if value == '☑':
                    html += f'<td><span class="check-yes">☑</span></td>'
                else:
                    html += f'<td></td>'  # Empty cell for unchecked
            # Check if this is the Signal column
            elif col == 'Signal':
                # Check if this is a Volume Trend signal
                signal_val = str(value).strip()
                if signal_val in ['STRONG ACCUMULATION', 'ACCUMULATION', 'HIDDEN ACCUMULATION', 
                                   'NEUTRAL', 'HIDDEN DISTRIBUTION', 'DISTRIBUTION', 'STRONG DISTRIBUTION']:
                    css_class = get_color_class_for_vt_signal(value)
                    html += f'<td>{format_colored_cell(value, css_class)}</td>'
                else:
                    html += f'<td>{format_signal(value)}</td>'
            # Check if this is Position column (Bullish=hijau, Neutral=kuning)
            elif col == position_column:
                css_class = get_color_class_for_position(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is OBV Trend column
            elif col == obv_trend_column:
                if value == 'Up':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Down':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            # Check if this is PVT Trend column
            elif col == pvt_trend_column:
                if value == 'Up':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Down':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            # Check if this is Divergence column
            elif col == obv_div_column:
                if value == 'Bullish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Bearish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            # Check if this is MACD Divergence column (MYCD)
            elif col == macd_div_column:
                if value == 'Bullish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Bearish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            # Check if this is CMF column
            elif col == cmf_column:
                try:
                    cmf_val = float(str(value).replace('x', '').strip())
                    if cmf_val > 0.25:
                        html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif cmf_val > 0.1:
                        html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif cmf_val > 0:
                        html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    elif cmf_val < -0.25:
                        html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                    elif cmf_val < -0.1:
                        html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                    elif cmf_val < 0:
                        html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    else:
                        html += f'<td>{value}</td>'
                except:
                    html += f'<td>{value}</td>'
            # Check if this is a percentage column that needs coloring
            elif col in pct_columns:
                css_class = get_color_class_for_percentage(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is RRR column with special color logic
            elif col == rrr_column:
                css_class = get_color_class_for_rrr(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is Compression Ratio column
            elif col == compression_ratio_column:
                css_class = get_color_class_for_compression_ratio(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is Spread% column
            elif col == spread_column:
                css_class = get_color_class_for_spread(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is %C vs PC column (green for positive, red for negative)
            elif col == pct_change_column:
                css_class = get_color_class_for_pct_change(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is a ratio column that needs coloring
            elif col in ratio_columns:
                css_class = get_color_class_for_ratio(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            # Check if this is Avg Val 20D column (higher is better)
            elif col == avg_val_column:
                try:
                    val = float(str(value).replace('x', '').strip())
                    if val >= 10:
                        html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif val >= 5:
                        html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    else:
                        html += f'<td>{value}</td>'
                except:
                    html += f'<td>{value}</td>'
            else:
                html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    
    # Display the HTML table
    st.markdown(html, unsafe_allow_html=True)


def display_backtest_table(df):
    """
    Display backtest results dataframe with styled checkboxes.
    Uses HTML table for better control over checkbox styling.
    """
    if df is None or df.empty:
        return
    
    # Convert dataframe to HTML table with custom styling
    html = '<table class="custom-table"><thead><tr>'
    
    # Add headers
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    # Add rows
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            
            # Check if this is a criteria column (checkboxes)
            if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if value == '☑':
                    html += f'<td><span class="check-yes">☑</span></td>'
                else:
                    html += f'<td></td>'  # Empty cell for unchecked
            else:
                html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    
    # Display the HTML table
    st.markdown(html, unsafe_allow_html=True)


# Period options for backtest (defined globally)
period_options = {"1 Year": "1y", "2 Years": "2y", "3 Years": "3y", "5 Years": "5y", "10 Years": "10y"}


# --- Main Application ---
def main():
    # Header
    st.markdown('<p class="main-header">💰 Auto Stock Screener</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    st.sidebar.title("📊 Menu")
    st.sidebar.info(
        "Application for stock screening.\n\n"
        "**Types of Screeners :**\n"
        "1. Sideways Screener\n"
        "2. Oversold Screener\n"
        "3. Demand Zone Screener\n"
        "4. Cari Demand/Supply Zone\n"
        "5. FVG Screener\n"
        "6. Decreasing Highs\n"
        "7. Magic Screener V1.1\n"
        "8. Magic Screener V1.3\n"
        "9. BB Reversal\n"
        "10. IV Rank\n"
        "11. Bullish Harami\n"
        "12. 1 Day Reversal\n"
        "13. Volume Trend Screener\n"
        "14. Volume Profile Screener\n"
        "15. Backtest for each type"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**📍 Navigation**")

    # Navigation buttons with JavaScript scroll
    if st.sidebar.button("📈 Sideways Screener", use_container_width=True):
        scroll_to_section("section_dz")

    if st.sidebar.button("📈 Backtest Sideways", use_container_width=True):
        scroll_to_section("section_dz_bt")

    if st.sidebar.button("📈 Oversold Screener", use_container_width=True):
        scroll_to_section("section_os")

    if st.sidebar.button("📈 Backtest Oversold", use_container_width=True):
        scroll_to_section("section_os_bt")

    if st.sidebar.button("📈 Demand Zone Screener", use_container_width=True):
        scroll_to_section("section_dmz")

    if st.sidebar.button("🔍 Cari Demand/Supply Zone", use_container_width=True):
        scroll_to_section("section_dmz_lookup")

    if st.sidebar.button("📈 FVG Screener", use_container_width=True):
        scroll_to_section("section_fvg")

    if st.sidebar.button("📈 Backtest FVG", use_container_width=True):
        scroll_to_section("section_fvg_bt")

    if st.sidebar.button("📈 Decreasing Highs", use_container_width=True):
        scroll_to_section("section_dh")

    if st.sidebar.button("📈 Backtest Decreasing Highs", use_container_width=True):
        scroll_to_section("section_dh_bt")

    if st.sidebar.button("📈 Magic Screener V1.1", use_container_width=True):
        scroll_to_section("section_v11")

    if st.sidebar.button("📈 Backtest V1.1", use_container_width=True):
        scroll_to_section("section_v11_bt")

    if st.sidebar.button("📈 Magic Screener V1.3", use_container_width=True):
        scroll_to_section("section_v13")

    if st.sidebar.button("📈 Backtest V1.3", use_container_width=True):
        scroll_to_section("section_v13_bt")

    if st.sidebar.button("📈 BB Reversal", use_container_width=True):
        scroll_to_section("section_bb")

    if st.sidebar.button("📈 Backtest BB Reversal", use_container_width=True):
        scroll_to_section("section_bb_bt")

    if st.sidebar.button("📈 IV Rank", use_container_width=True):
        scroll_to_section("section_iv")

    if st.sidebar.button("📈 Backtest IV Rank", use_container_width=True):
        scroll_to_section("section_iv_bt")

    if st.sidebar.button("📈 Bullish Harami", use_container_width=True):
        scroll_to_section("section_bh")

    if st.sidebar.button("📈 Backtest Bullish Harami", use_container_width=True):
        scroll_to_section("section_bh_bt")

    if st.sidebar.button("📈 1 Day Reversal", use_container_width=True):
        scroll_to_section("section_dr")

    if st.sidebar.button("📈 Backtest 1 Day Reversal", use_container_width=True):
        scroll_to_section("section_dr_bt")

    if st.sidebar.button("📈 Volume Trend Screener", use_container_width=True):
        scroll_to_section("section_vt")
        
    if st.sidebar.button("📈 Volume Profile Screener", use_container_width=True):
        scroll_to_section("section_vp")

    st.sidebar.markdown("---")
    
    # Column Legend
    st.sidebar.markdown("**📋 Keterangan Kolom :**")
    with st.sidebar.expander("Lihat Keterangan", expanded=False):
        st.markdown("""
        **Tickers** : Kode emiten
        
        **Price** : Harga penutupan terakhir
        
        **LB** : Lower Band Bollinger (khusus BB Reversal)
        
        **IV Rank** : Implied Volatility Rank (0-100)
        
        **HV** : Historical Volatility (annualized)
        
        **WR** : Win Rate
        
        **Trades** : Jumlah transaksi historis dengan setup sesuai kriteria
        
        **%C vs PC** : Persentase perubahan harga dari harga kemarin
        
        **1. PR** : Previous Red
        
        **2. V>MA20** : Volume > MA20
        
        **3. MA+** : MA5 > MA10 > MA20 > MA50 > MA200
        
        **4. L>PL** : Low > Previous Low
        
        **5. H>PH** : High > Previous High
        
        **6. O=PC** : Open = Previous Close
        
        **7. OL>HC** : Open - Low > High - Close
        
        **8. C>VWAP** : Close > VWAP
        
        **9. PC<PVWAP** : Previous Close < Previous VWAP
        
        **10. V>MA5** : Volume > MA5
        
        **IV Rank Columns:**
        - **1. IV↑** : IV Rank crossover above 50
        - **2. C>EMA** : Close above EMA(144)
        - **3. Green** : Current day green candle
        - **4. Prev Red** : Previous day red candle
        
        **Score** : Skor intraday (0-10)
        
        **Position** : Posisi close dalam range harian
        
        **Momentum** : Momentum 15 menit terakhir
        
        **Vol Ratio** : Ratio volume terhadap rata-rata
        
        **Signal** : Sinyal trading (STRONG BUY/BUY/CONSIDER/WEAK/AVOID)

        **Date** : Tanggal data terakhir
        
        **POC** : Point of Control (harga dengan volume terbanyak)
        
        **VAH** : Value Area High (batas atas area value 70%)
        
        **VAL** : Value Area Low (batas bawah area value 70%)
        """)

    st.sidebar.markdown("---")

    if st.sidebar.button("🗑️ Clear All Results", use_container_width=True):
        clear_all()
        st.rerun()

    # ============================
    # Sideways Screener
    # ============================
    st.markdown('<div id="section_dz"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Sideways Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Sideways Screener", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - MA5, MA10, MA20 Clustered (sideways detection)
        - Average 20-Day Transaction Value >= 5 Billion Rupiah
        
        **Sideways Detection (MA Cluster):**
        - MA5, MA10, MA20 berada dalam range yang sempit
        - Spread = (max MA - min MA) / min MA <= 5%
        - MA Cluster minimal 20 hari berturut-turut
        - Menandakan saham sedang konsolidasi/sideways
        
        **ATR Compression Conditions:**
        - ATR 5 / ATR 20 <= 1 (Compression Ratio)
        - ATR 5 menurun 3 hari berturut-turut
        - Menandakan volatilitas menurun = potensi breakout
        
        **Exit Strategy (Swing Trading):**
        - **Max Holding**: 5 trading days
        - **Trail Stop**: Close below MA20 (after 2 days)
        
        **Columns Explained:**
        - **Compression Ratio**: ATR 5 / ATR 20 (<= 1 = volatilitas rendah)
        - **Spread%**: Persentase spread antara MA (semakin kecil semakin bagus)
        - **Inflow Ratio**: Value hari ini / (Price MA 20 × Volume MA 20) (> 1x = nilai transaksi di atas rata-rata)
        - **Avg Val 20D (B)**: Rata-rata nilai transaksi 20 hari terakhir (dalam miliar rupiah)
        - **Demand**: Area demand (High - Low)
        - **Supply**: Area supply (High - Low)
        - **MA5/MA10/MA20**: Moving Average values
        - **Position**: Posisi MA (Bullish/Bearish/Neutral)
        - **Side Days**: Jumlah hari MA cluster bertahan
        """)

    # Date picker
    col_date8, col_btn8, col_info8 = st.columns([1, 1, 2])
    with col_date8:
        selected_date_dz = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_dz", format="DD/MM/YYYY")
    with col_btn8:
        if st.button("🚀 Run Sideways", key="btn_dz", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_dz)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_dz)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_dz):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_sideways_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                # Sort by Spread% ascending (tighter spread = better)
                if 'Spread%' in df_results.columns:
                    df_results['Spread_numeric'] = df_results['Spread%'].str.rstrip('%').astype(float)
                    df_results = df_results.sort_values(by=['Spread_numeric'], ascending=[True]).reset_index(drop=True)
                    df_results = df_results.drop(columns=['Spread_numeric'])
                st.session_state.dz_results = df_results
            else:
                st.session_state.dz_results = pd.DataFrame()
            st.rerun()

    with col_info8:
        st.info("🔎 Stocks with MA clustered indicating sideways movement")

    if st.session_state.dz_results is not None:
        if not st.session_state.dz_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.dz_results)} stock** found")
            display_results_table(st.session_state.dz_results, "dz")
            csv = st.session_state.dz_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="sideways_screener.csv", mime="text/csv", key="dl_dz")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest Sideways Screener
    # ============================
    st.markdown('<div id="section_dz_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Sideways Screener</p>', unsafe_allow_html=True)

    col_bt8_input, col_bt8_btn = st.columns([2, 1])
    with col_bt8_input:
        ticker_list_dz = get_ticker_list_dz()
        selected_ticker_dz = st.selectbox("Select Ticker :", options=ticker_list_dz, index=None, placeholder="Type or select a ticker...", key="ticker_dz_bt")
        selected_period_dz = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_dz_bt")

    with col_bt8_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest Sideways", key="btn_bt_dz", use_container_width=True):
            if selected_ticker_dz:
                with st.spinner(f"Running backtest for {selected_ticker_dz}..."):
                    df_trades, summary = run_backtest_dz(selected_ticker_dz, period=period_options[selected_period_dz])
                st.session_state.dz_bt_results = df_trades
                st.session_state.dz_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.dz_bt_results is not None and st.session_state.dz_bt_summary is not None:
        summary = st.session_state.dz_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        with col_s5:
            st.metric("Avg Days", f"{summary['avg_holding_days']:.1f}")
        display_backtest_table(st.session_state.dz_bt_results)

    st.markdown("---")
    # Oversold Screener
    # ============================
    st.markdown('<div id="section_os"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Oversold Screener (RSI & Stochastic)</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Oversold Criteria", expanded=False):
        st.markdown("""
        **What is Oversold?**
        
        Oversold adalah kondisi dimana harga sudah turun terlalu rendah dalam waktu singkat dan berpotensi untuk rebound/naik.
        
        **RSI Oversold Criteria:**
        - RSI < 30 = Oversold
        - RSI < 20 = Extremely Oversold
        
        **Stochastic Oversold Criteria:**
        - Stochastic %K < 20 = Oversold
        - Stochastic %K < 10 = Extremely Oversold
        
        **Signal Interpretation:**
        - **STRONG BUY**: RSI < 30 AND Stoch < 20
        - **BUY**: RSI < 30 OR Stoch < 20
        
        **Strategy:**
        - Entry ketika RSI atau Stochastic menunjukkan kondisi oversold
        - Exit ketika RSI naik di atas 70 (overbought)
        - Stop Loss 5% di bawah entry price
        - Max holding 5 hari
        
        **Columns:**
        - **RSI**: Nilai RSI saat ini
        - **RSI OS**: ☑ jika RSI < 30
        - **Stoch %K**: Nilai Stochastic %K
        - **Stoch %D**: Nilai Stochastic %D (signal line)
        - **Stoch OS**: ☑ jika Stoch %K < 20
        - **Signal**: STRONG BUY atau BUY
        """)

    # Run button
    col_date_os, col_btn_os, col_info_os = st.columns([1, 1, 2])
    with col_date_os:
        st.write("")  # No date picker needed
    with col_btn_os:
        if st.button("🚀 Run Oversold Screener", key="btn_os", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_os)

            with st.spinner("Scanning for oversold stocks..."):
                for idx, ticker_item in enumerate(tickers_os):
                    progress = (idx + 1) / total_tickers
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        output = run_oversold_screener(symbol=ticker_item)
                        if output:
                            results.append(output)
                    except Exception:
                        pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                # Sort by RSI ascending (most oversold first)
                if 'RSI' in df_results.columns:
                    df_results['RSI_numeric'] = df_results['RSI'].astype(float)
                    df_results = df_results.sort_values(by=['RSI_numeric'], ascending=[True]).reset_index(drop=True)
                    df_results = df_results.drop(columns=['RSI_numeric'])
                st.session_state.os_results = df_results
            else:
                st.session_state.os_results = pd.DataFrame()
            st.rerun()

    with col_info_os:
        st.info("🔎 Scan for stocks with RSI < 30 or Stochastic < 20")

    if st.session_state.os_results is not None:
        if not st.session_state.os_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.os_results)} stock** found in oversold condition")
            display_results_table(st.session_state.os_results, "os")
            csv = st.session_state.os_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="oversold_screener.csv", mime="text/csv", key="dl_os")
        else:
            st.warning("⚠️ No stocks meet the oversold criteria")

    # ============================
    # Backtest Oversold Screener
    # ============================
    st.markdown('<div id="section_os_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Oversold Screener</p>', unsafe_allow_html=True)

    col_bt_os_input, col_bt_os_btn = st.columns([2, 1])
    with col_bt_os_input:
        ticker_list_os_bt = get_ticker_list_os()
        selected_ticker_os = st.selectbox("Select Ticker :", options=ticker_list_os_bt, index=None, placeholder="Type or select a ticker...", key="ticker_os_bt")
        selected_period_os = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_os_bt")

    with col_bt_os_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest Oversold", key="btn_bt_os", use_container_width=True):
            if selected_ticker_os:
                with st.spinner(f"Running backtest for {selected_ticker_os}..."):
                    df_trades, summary = run_backtest_os(selected_ticker_os, period=period_options[selected_period_os])
                st.session_state.os_bt_results = df_trades
                st.session_state.os_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.os_bt_results is not None and st.session_state.os_bt_summary is not None:
        summary = st.session_state.os_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.os_bt_results)

    st.markdown("---")
    # ============================
    # Demand Zone Screener
    # ============================
    st.markdown('<div id="section_dmz"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Demand Zone Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Demand Zone Criteria", expanded=False):
        st.markdown("""
        **What is Demand Zone?**
        
        Demand Zone adalah area support dimana buying pressure biasanya muncul.
        Area ini diidentifikasi dari pivot low dengan zona berdasarkan ATR.
        
        **Criteria:**
        - Harga saat ini berada DALAM range demand zone (demand_low <= price <= demand_high)
        - Transaction Value >= 5 billion
        - Price >= 100
        
        **Demand Zone Calculation:**
        - Pivot Low terdeteksi (swing length = 10)
        - Zone Low = Pivot Low
        - Zone High = Pivot Low + (ATR × 0.25)
        
        **Strategy:**
        - Entry: Ketika harga memasuki demand zone
        - Target: Nearest supply zone
        - Stop Loss: Below demand zone low
        
        **Columns:**
        - **Date**: Tanggal data
        - **Ticker**: Kode emiten
        - **Price**: Harga penutupan terakhir
        - **Demand**: Area demand zone (tinggi - rendah)
        - **Supply**: Area supply zone terdekat (tinggi - rendah)
        - **Inflow Ratio**: Value hari ini / (MA20 × Vol MA20)
        - **Compression Ratio**: ATR 5 / ATR 20 (<= 1 menunjukkan volatilitas rendah)
        - **RRR**: Risk-Reward Ratio (jarak ke supply / jarak ke demand low)
        """)

    # Run button
    col_date_dmz, col_btn_dmz, col_info_dmz = st.columns([1, 1, 2])
    with col_date_dmz:
        st.write("")  # No date picker needed
    with col_btn_dmz:
        if st.button("🚀 Run Demand Zone Screener", key="btn_dmz", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_dmz)

            with st.spinner("Scanning for stocks in demand zone..."):
                for idx, ticker_item in enumerate(tickers_dmz):
                    progress = (idx + 1) / total_tickers
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        output = run_demand_zone_screener(symbol=ticker_item)
                        if output:
                            results.append(output)
                    except Exception:
                        pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                # Sort by RRR descending (higher RRR = better)
                if 'RRR' in df_results.columns:
                    df_results['RRR_numeric'] = df_results['RRR'].apply(lambda x: float(x.replace('x', '')) if x else 0)
                    df_results = df_results.sort_values(by=['RRR_numeric'], ascending=[False]).reset_index(drop=True)
                    df_results = df_results.drop(columns=['RRR_numeric'])
                st.session_state.dmz_results = df_results
            else:
                st.session_state.dmz_results = pd.DataFrame()
            st.rerun()

    with col_info_dmz:
        st.info("🔎 Scan for stocks currently in demand zone area")

    if st.session_state.dmz_results is not None:
        if not st.session_state.dmz_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.dmz_results)} stock** found in demand zone")
            display_results_table(st.session_state.dmz_results, "dmz")
            csv = st.session_state.dmz_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="demand_zone_screener.csv", mime="text/csv", key="dl_dmz")
        else:
            st.warning("⚠️ No stocks in demand zone found")

    # ============================
    # Demand/Supply Zone Lookup
    # ============================
    st.markdown('<div id="section_dmz_lookup"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">🔍 Cari Demand & Supply Zone Saham</p>', unsafe_allow_html=True)
    
    st.markdown("""
    **Cari area demand dan supply untuk saham tertentu.**
    Masukkan kode saham untuk melihat posisi harga saat ini relatif terhadap demand dan supply zone.
    """)
    
    col_lookup_input, col_lookup_btn = st.columns([2, 1])
    with col_lookup_input:
        ticker_list_dmz_lookup = [t.replace('.JK', '') for t in tickers_dmz]
        selected_ticker_lookup = st.selectbox("Pilih Ticker :", options=ticker_list_dmz_lookup, index=None, placeholder="Ketik atau pilih ticker...", key="ticker_dmz_lookup")
    
    with col_lookup_btn:
        st.write("")
        st.write("")
        if st.button("🔍 Cari Demand/Supply", key="btn_dmz_lookup", use_container_width=True):
            if selected_ticker_lookup:
                with st.spinner(f"Mencari demand/supply zone untuk {selected_ticker_lookup}..."):
                    result = get_stock_demand_supply(selected_ticker_lookup)
                st.session_state.dmz_lookup = result
                st.rerun()
            else:
                st.error("❌ Pilih ticker terlebih dahulu!")
    
    if st.session_state.dmz_lookup is not None:
        result = st.session_state.dmz_lookup
        
        if result:
            st.markdown('<div class="success-box">✅ Data ditemukan!</div>', unsafe_allow_html=True)
            
            # Format data untuk tabel
            inflow = result['Inflow Ratio']
            comp = result['Compression Ratio']
            rrr = result['RRR']
            
            table_data = {
                'Ticker': result['Ticker'],
                'Price': f"{result['Price']:,.0f}",
                '%C vs PC': f"{result['%C vs PC']:+.2f}%",
                'Demand': result['Demand Zone'] if result['Demand Zone'] else "-",
                'Supply': result['Supply Zone'] if result['Supply Zone'] else "-",
                'Inflow Ratio': f"{inflow:.2f}x" if inflow else "-",
                'Compression Ratio': f"{comp:.2f}" if comp else "-",
                'RRR': f"{rrr:.2f}x" if rrr else "-"
            }
            
            df_lookup = pd.DataFrame([table_data])
            display_results_table(df_lookup, "dmz_lookup")
                
        else:
            st.warning("⚠️ Tidak dapat mengambil data untuk ticker tersebut. Pastikan ticker valid.")
    
    st.markdown("---")
    # FVG Screener
    # ============================
    st.markdown('<div id="section_fvg"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 FVG Screener (Fair Value Gap)</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria FVG", expanded=False):
        st.markdown("""
        **What is Fair Value Gap (FVG)?**
        
        FVG adalah area gap yang terjadi antara High candle sebelumnya dan Low candle berikutnya.
        Area ini dianggap sebagai "fair value" dimana harga kemungkinan akan kembali (retrace).
        
        **Bullish FVG Criteria :**
        - High candle i-1 < Low candle i+1 (gap ke atas)
        - Menunjukkan momentum bullish kuat
        - Area antara High[i-1] dan Low[i+1] adalah FVG zone
        
        **Filters :**
        - Transaction Value >= 5 billion
        - Price >= 100
        
        **Strategy :**
        - Entry: Ketika FVG terdeteksi
        - Target: Price retrace ke FVG zone
        - Stop Loss: 5% below entry
        - Max Hold: 10 trading days
        
        **Columns :**
        - **Bull FVG (L)** : Batas bawah FVG (High candle sebelumnya)
        - **Bull FVG (H)** : Batas atas FVG (Low candle berikutnya)
        - **FVG Size%** : Ukuran FVG sebagai persentase dari harga
        - **Position** : Posisi harga relatif terhadap FVG (Above/In FVG/Below)
        - **Dist to FVG** : Jarak harga ke FVG zone
        - **Trend** : Trend 5 hari terakhir
        """)

    # Date picker
    col_date_fvg, col_btn_fvg, col_info_fvg = st.columns([1, 1, 2])
    with col_date_fvg:
        st.write("")  # FVG doesn't need date picker, it scans latest data
    with col_btn_fvg:
        if st.button("🚀 Run FVG Screener", key="btn_fvg", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_fvg)

            with st.spinner("Scanning for FVG patterns..."):
                for idx, ticker_item in enumerate(tickers_fvg):
                    progress = (idx + 1) / total_tickers
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        output = run_fvg_screener(symbol=ticker_item)
                        if output:
                            results.append(output)
                    except Exception:
                        pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                # Sort by FVG Size (larger = stronger momentum)
                if 'FVG Size%' in df_results.columns:
                    df_results['FVG_Size_numeric'] = df_results['FVG Size%'].str.rstrip('%').astype(float)
                    df_results = df_results.sort_values(by=['FVG_Size_numeric'], ascending=[False]).reset_index(drop=True)
                    df_results = df_results.drop(columns=['FVG_Size_numeric'])
                st.session_state.fvg_results = df_results
            else:
                st.session_state.fvg_results = pd.DataFrame()
            st.rerun()

    with col_info_fvg:
        st.info("🔎 Scan for stocks with Bullish Fair Value Gap pattern")

    if st.session_state.fvg_results is not None:
        if not st.session_state.fvg_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.fvg_results)} stock** found with Bullish FVG")
            display_results_table(st.session_state.fvg_results, "fvg")
            csv = st.session_state.fvg_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="fvg_screener.csv", mime="text/csv", key="dl_fvg")
        else:
            st.warning("⚠️ No stocks meet the FVG criteria")

    # ============================
    # Backtest FVG Screener
    # ============================
    st.markdown('<div id="section_fvg_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest FVG Screener</p>', unsafe_allow_html=True)

    col_bt_fvg_input, col_bt_fvg_btn = st.columns([2, 1])
    with col_bt_fvg_input:
        ticker_list_fvg_bt = get_ticker_list_fvg()
        selected_ticker_fvg = st.selectbox("Select Ticker :", options=ticker_list_fvg_bt, index=None, placeholder="Type or select a ticker...", key="ticker_fvg_bt")
        selected_period_fvg = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_fvg_bt")

    with col_bt_fvg_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest FVG", key="btn_bt_fvg", use_container_width=True):
            if selected_ticker_fvg:
                with st.spinner(f"Running backtest for {selected_ticker_fvg}..."):
                    df_trades, summary = run_backtest_fvg(selected_ticker_fvg, period=period_options[selected_period_fvg])
                st.session_state.fvg_bt_results = df_trades
                st.session_state.fvg_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.fvg_bt_results is not None and st.session_state.fvg_bt_summary is not None:
        summary = st.session_state.fvg_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        with col_s5:
            st.metric("FVG Hit Rate", f"{summary['fvg_hit_rate']:.1f}%")
        display_backtest_table(st.session_state.fvg_bt_results)

    st.markdown("---")
    # Decreasing Highs Screener
    # ============================
    st.markdown('<div id="section_dh"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Decreasing Highs Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Decreasing Highs", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - High Today < High Yesterday (decreasing)
        - High Yesterday < High Day Before Yesterday (decreasing)
        - High Day Before Yesterday < High Two Days Ago (decreasing)
        - High Two Days Ago < High Three Days Ago (decreasing)
        - Price >= 100
        - Transaction Value >= 5 Billion
        
        **Strategy Parameters :**
        - 4 consecutive days of decreasing highs
        - Target Profit (High): 1.36%
        - Target Profit (Close): 0.36%
        
        **Exit Strategy :**
        - Next day's High hits 1.36% target
        - Next day's Close hits 0.36% target
        - Otherwise exit at next day's close
        
        **Strategy Concept :**
        Mean reversion strategy looking for stocks in downtrend (4 days of decreasing highs)
        for potential reversal/bounce play.
        """)

    # Date picker
    col_date7, col_btn7, col_info7 = st.columns([1, 1, 2])
    with col_date7:
        selected_date_dh = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_dh", format="DD/MM/YYYY")
    with col_btn7:
        if st.button("🚀 Run Decreasing Highs", key="btn_dh", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_dh)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_dh)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_dh):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_decreasing_highs_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric'], ascending=[False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['WR_numeric'])
                st.session_state.dh_results = df_results
            else:
                st.session_state.dh_results = pd.DataFrame()
            st.rerun()

    with col_info7:
        st.info("🔎 Live screening for 4 consecutive days of decreasing highs (reversal play)")

    if st.session_state.dh_results is not None:
        if not st.session_state.dh_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.dh_results)} stock** found")
            display_results_table(st.session_state.dh_results, "dh")
            csv = st.session_state.dh_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="decreasing_highs_screener.csv", mime="text/csv", key="dl_dh")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest Decreasing Highs
    # ============================
    st.markdown('<div id="section_dh_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Decreasing Highs</p>', unsafe_allow_html=True)

    col_bt7_input, col_bt7_btn = st.columns([2, 1])
    with col_bt7_input:
        ticker_list_dh = get_ticker_list_dh()
        selected_ticker_dh = st.selectbox("Select Ticker :", options=ticker_list_dh, index=None, placeholder="Type or select a ticker...", key="ticker_dh_bt")
        selected_period_dh = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_dh_bt")

    with col_bt7_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest Decreasing Highs", key="btn_bt_dh", use_container_width=True):
            if selected_ticker_dh:
                with st.spinner(f"Running backtest for {selected_ticker_dh}..."):
                    df_trades, summary = run_backtest_dh(selected_ticker_dh, period=period_options[selected_period_dh])
                st.session_state.dh_bt_results = df_trades
                st.session_state.dh_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.dh_bt_results is not None and st.session_state.dh_bt_summary is not None:
        summary = st.session_state.dh_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.dh_bt_results)

    st.markdown("---")
    # Magic Screener V1.1
    # ============================
    st.markdown('<div id="section_v11"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Magic Screener V1.1</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria V1.1", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Vol > Prev Vol
        - Close > Prev Close
        - Close > MA5
        - Value > 5 billion
        - Prev Close < Prev MA5
        - Close > Open
        - Price >= 100
        """)

    # Date picker
    col_date1, col_btn1, col_info1 = st.columns([1, 1, 2])
    with col_date1:
        selected_date_v11 = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_v11", format="DD/MM/YYYY")
    with col_btn1:
        if st.button("🚀 Run V1.1", key="btn_v11", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_v11)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_v11)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_v11):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_magic_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['Price_numeric'] = df_results['Price'].str.replace(',', '').astype(float)
                df_results['Pct_C_vs_PC_numeric'] = df_results['%C vs PC'].str.rstrip('%').astype(float)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(
                    by=['WR_numeric', 'Pct_C_vs_PC_numeric', 'Price_numeric'],
                    ascending=[False, False, False]
                ).reset_index(drop=True)
                df_results = df_results.drop(columns=['Price_numeric', 'Pct_C_vs_PC_numeric', 'WR_numeric'])
                st.session_state.v11_results = df_results
            else:
                st.session_state.v11_results = pd.DataFrame()
            st.rerun()

    with col_info1:
        st.info("🔎 Live screening with reversal criteria from below MA5")

    if st.session_state.v11_results is not None:
        if not st.session_state.v11_results.empty:
            st.markdown('<div class="success-box">✅ Scan completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.v11_results)} stock** found")
            display_results_table(st.session_state.v11_results, "v11")
            csv = st.session_state.v11_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="magic_screener_v11.csv", mime="text/csv", key="dl_v11")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest Magic Screener V1.1
    # ============================
    st.markdown('<div id="section_v11_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Magic Screener V1.1</p>', unsafe_allow_html=True)

    col_bt1_input, col_bt1_btn = st.columns([2, 1])
    with col_bt1_input:
        ticker_list_v11 = get_ticker_list_v11()
        selected_ticker_v11 = st.selectbox("Select Ticker :", options=ticker_list_v11, index=None, placeholder="Type or select a ticker...", key="ticker_v11_bt")
        selected_period_v11 = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_v11_bt")

    with col_bt1_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest V1.1", key="btn_bt_v11", use_container_width=True):
            if selected_ticker_v11:
                with st.spinner(f"Running backtest for {selected_ticker_v11}..."):
                    df_trades, summary = run_backtest_for_ticker(selected_ticker_v11, period=period_options[selected_period_v11])
                st.session_state.v11_bt_results = df_trades
                st.session_state.v11_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.v11_bt_results is not None and st.session_state.v11_bt_summary is not None:
        summary = st.session_state.v11_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.v11_bt_results)

    st.markdown("---")
    # Magic Screener V1.3
    # ============================
    st.markdown('<div id="section_v13"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Magic Screener V1.3</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria V1.3", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Vol > Prev Vol
        - Close > Prev Close
        - Close > MA5
        - Value > 5 billion
        - Close > Open
        - **Yesterday : Close > Open and Close > MA5**
        - **2 Days Ago : Close > Open and Close > MA5**
        - Price >= 100
        """)

    # Date picker
    col_date2, col_btn2, col_info2 = st.columns([1, 1, 2])
    with col_date2:
        selected_date_v13 = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_v13", format="DD/MM/YYYY")
    with col_btn2:
        if st.button("🚀 Run V1.3", key="btn_v13", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_v13)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_v13)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_v13):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_magic_screener_v13(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['Price_numeric'] = df_results['Price'].str.replace(',', '').astype(float)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric', 'Price_numeric'], ascending=[False, False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['Price_numeric', 'WR_numeric'])
                st.session_state.v13_results = df_results
            else:
                st.session_state.v13_results = pd.DataFrame()
            st.rerun()

    with col_info2:
        st.info("🔎 Live screening with criteria of 3 consecutive green candles above MA5")

    if st.session_state.v13_results is not None:
        if not st.session_state.v13_results.empty:
            st.markdown('<div class="success-box">✅ Scan completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.v13_results)} stock** found")
            display_results_table(st.session_state.v13_results, "v13")
            csv = st.session_state.v13_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="magic_screener_v13.csv", mime="text/csv", key="dl_v13")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest Magic Screener V1.3
    # ============================
    st.markdown('<div id="section_v13_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Magic Screener V1.3</p>', unsafe_allow_html=True)

    col_bt2_input, col_bt2_btn = st.columns([2, 1])
    with col_bt2_input:
        ticker_list_v13 = get_ticker_list_v13()
        selected_ticker_v13 = st.selectbox("Select Ticker :", options=ticker_list_v13, index=None, placeholder="Type or select a ticker...", key="ticker_v13_bt")
        selected_period_v13 = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_v13_bt")

    with col_bt2_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest V1.3", key="btn_bt_v13", use_container_width=True):
            if selected_ticker_v13:
                with st.spinner(f"Running backtest for {selected_ticker_v13}..."):
                    df_trades, summary = run_backtest_for_ticker_v13(selected_ticker_v13, period=period_options[selected_period_v13])
                st.session_state.v13_bt_results = df_trades
                st.session_state.v13_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.v13_bt_results is not None and st.session_state.v13_bt_summary is not None:
        summary = st.session_state.v13_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.v13_bt_results)

    st.markdown("---")
    # BB Reversal
    # ============================
    st.markdown('<div id="section_bb"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 BB Reversal</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria BB Reversal", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Vol > Prev Vol
        - Close > Prev Close
        - Close > Open
        - Value > 1 billion
        - Prev Close < Prev Open
        - Close > Lower Band Bollinger
        - Prev Close < Prev Lower Band Bollinger
        - Price >= 100
        """)

    # Date picker
    col_date3, col_btn3, col_info3 = st.columns([1, 1, 2])
    with col_date3:
        selected_date_bb = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_bb", format="DD/MM/YYYY")
    with col_btn3:
        if st.button("🚀 Run BB Reversal", key="btn_bb", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_bb)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_bb)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_bb):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_bb_reversal_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['Price_numeric'] = df_results['Price'].str.replace(',', '').astype(float)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric', 'Price_numeric'], ascending=[False, False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['Price_numeric', 'WR_numeric'])
                st.session_state.bb_results = df_results
            else:
                st.session_state.bb_results = pd.DataFrame()
            st.rerun()

    with col_info3:
        st.info("🔎 Live screening for reversal from the Lower Bollinger Band")

    if st.session_state.bb_results is not None:
        if not st.session_state.bb_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.bb_results)} stock** found")
            display_results_table(st.session_state.bb_results, "bb")
            csv = st.session_state.bb_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="bb_reversal_screener.csv", mime="text/csv", key="dl_bb")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest BB Reversal
    # ============================
    st.markdown('<div id="section_bb_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest BB Reversal</p>', unsafe_allow_html=True)

    col_bt3_input, col_bt3_btn = st.columns([2, 1])
    with col_bt3_input:
        ticker_list_bb = get_ticker_list_bb()
        selected_ticker_bb = st.selectbox("Select Ticker :", options=ticker_list_bb, index=None, placeholder="Type or select a ticker...", key="ticker_bb_bt")
        selected_period_bb = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_bb_bt")

    with col_bt3_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest BB Reversal", key="btn_bt_bb", use_container_width=True):
            if selected_ticker_bb:
                with st.spinner(f"Running backtest for {selected_ticker_bb}..."):
                    df_trades, summary = run_backtest_bb_reversal_for_ticker(selected_ticker_bb, period=period_options[selected_period_bb])
                st.session_state.bb_bt_results = df_trades
                st.session_state.bb_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.bb_bt_results is not None and st.session_state.bb_bt_summary is not None:
        summary = st.session_state.bb_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.bb_bt_results)

    st.markdown("---")
    # IV Rank Screener
    # ============================
    st.markdown('<div id="section_iv"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 IV Rank Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria IV Rank", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - IV Rank crosses above 50 (from below)
        - Close > EMA(144)
        - Current day green candle (Close > Open)
        - Previous day red candle (Close < Open)
        - Price >= 100
        
        **Strategy Parameters :**
        - IV Rank Period: 365 days
        - Historical Volatility Period: 30 days
        - EMA Period: 144
        - IV Rank Threshold: 50
        - Target Profit (High): 1.36%
        - Target Profit (Close): 0.36%
        
        **Exit Strategy :**
        - Next day's High hits 1.36% target
        - Next day's Close hits 0.36% target
        - Otherwise exit at next day's close
        """)

    # Date picker
    col_date4, col_btn4, col_info4 = st.columns([1, 1, 2])
    with col_date4:
        selected_date_iv = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_iv", format="DD/MM/YYYY")
    with col_btn4:
        if st.button("🚀 Run IV Rank", key="btn_iv", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_iv)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_iv)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_iv):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_iv_rank_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric'], ascending=[False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['WR_numeric'])
                st.session_state.iv_results = df_results
            else:
                st.session_state.iv_results = pd.DataFrame()
            st.rerun()

    with col_info4:
        st.info("🔎 Live screening for IV Rank crossover with reversal pattern")

    if st.session_state.iv_results is not None:
        if not st.session_state.iv_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.iv_results)} stock** found")
            display_results_table(st.session_state.iv_results, "iv")
            csv = st.session_state.iv_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="iv_rank_screener.csv", mime="text/csv", key="dl_iv")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest IV Rank
    # ============================
    st.markdown('<div id="section_iv_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest IV Rank</p>', unsafe_allow_html=True)

    col_bt4_input, col_bt4_btn = st.columns([2, 1])
    with col_bt4_input:
        ticker_list_iv = get_ticker_list_iv()
        selected_ticker_iv = st.selectbox("Select Ticker :", options=ticker_list_iv, index=None, placeholder="Type or select a ticker...", key="ticker_iv_bt")
        selected_period_iv = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_iv_bt")

    with col_bt4_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest IV Rank", key="btn_bt_iv", use_container_width=True):
            if selected_ticker_iv:
                with st.spinner(f"Running backtest for {selected_ticker_iv}..."):
                    df_trades, summary = run_backtest_iv_rank(selected_ticker_iv, period=period_options[selected_period_iv])
                st.session_state.iv_bt_results = df_trades
                st.session_state.iv_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.iv_bt_results is not None and st.session_state.iv_bt_summary is not None:
        summary = st.session_state.iv_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.iv_bt_results)

    st.markdown("---")
    # Bullish Harami Screener
    # ============================
    st.markdown('<div id="section_bh"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Bullish Harami Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Bullish Harami", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Previous day: Long bearish candle (body >= 30% of range)
        - Current day: Small bullish candle (body < 15% of prev range)
        - Current body completely engulfed by previous body
        - Price >= 100
        - Transaction Value >= 1 Billion
        
        **Strategy Parameters :**
        - Previous Body Threshold: 30% of candle range
        - Current Body Threshold: < 15% of previous range
        - Target Profit (High): 1.36%
        - Target Profit (Close): 0.36%
        
        **Exit Strategy :**
        - Next day's High hits 1.36% target
        - Next day's Close hits 0.36% target
        - Otherwise exit at next day's close
        """)

    # Date picker
    col_date5, col_btn5, col_info5 = st.columns([1, 1, 2])
    with col_date5:
        selected_date_bh = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_bh", format="DD/MM/YYYY")
    with col_btn5:
        if st.button("🚀 Run Bullish Harami", key="btn_bh", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_bh)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_bh)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_bh):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_bullish_harami_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric'], ascending=[False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['WR_numeric'])
                st.session_state.bh_results = df_results
            else:
                st.session_state.bh_results = pd.DataFrame()
            st.rerun()

    with col_info5:
        st.info("🔎 Live screening for Bullish Harami candlestick pattern")

    if st.session_state.bh_results is not None:
        if not st.session_state.bh_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.bh_results)} stock** found")
            display_results_table(st.session_state.bh_results, "bh")
            csv = st.session_state.bh_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="bullish_harami_screener.csv", mime="text/csv", key="dl_bh")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest Bullish Harami
    # ============================
    st.markdown('<div id="section_bh_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest Bullish Harami</p>', unsafe_allow_html=True)

    col_bt5_input, col_bt5_btn = st.columns([2, 1])
    with col_bt5_input:
        ticker_list_bh = get_ticker_list_bh()
        selected_ticker_bh = st.selectbox("Select Ticker :", options=ticker_list_bh, index=None, placeholder="Type or select a ticker...", key="ticker_bh_bt")
        selected_period_bh = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_bh_bt")

    with col_bt5_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest Bullish Harami", key="btn_bt_bh", use_container_width=True):
            if selected_ticker_bh:
                with st.spinner(f"Running backtest for {selected_ticker_bh}..."):
                    df_trades, summary = run_backtest_bh(selected_ticker_bh, period=period_options[selected_period_bh])
                st.session_state.bh_bt_results = df_trades
                st.session_state.bh_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.bh_bt_results is not None and st.session_state.bh_bt_summary is not None:
        summary = st.session_state.bh_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.bh_bt_results)

    st.markdown("---")
    # 1 Day Reversal Screener
    # ============================
    st.markdown('<div id="section_dr"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 1 Day Reversal Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria 1 Day Reversal", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Volume Up: Current volume > Previous volume
        - Previous Red Candle: Previous close < Previous open
        - Current Green Candle: Current close > Current open
        - Price >= 100
        - Transaction Value >= 5 Billion
        
        **Strategy Parameters :**
        - Target Profit (High): 1.36%
        - Target Profit (Close): 0.36%
        
        **Exit Strategy :**
        - Next day's High hits 1.36% target
        - Next day's Close hits 0.36% target
        - Otherwise exit at next day's close
        """)

    # Date picker
    col_date6, col_btn6, col_info6 = st.columns([1, 1, 2])
    with col_date6:
        selected_date_dr = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_dr", format="DD/MM/YYYY")
    with col_btn6:
        if st.button("🚀 Run 1 Day Reversal", key="btn_dr", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_1dr)
            
            # Get all dates in range
            dates_to_scan = get_dates_in_range(selected_date_dr)
            total_dates = len(dates_to_scan)

            with st.spinner(f"Scanning {total_dates} date(s)..."):
                for date_idx, scan_date in enumerate(dates_to_scan):
                    for idx, ticker_item in enumerate(tickers_1dr):
                        progress = ((date_idx * total_tickers) + idx + 1) / (total_dates * total_tickers)
                        progress_bar.progress(progress)
                        status_text.text(f"Date {date_idx + 1}/{total_dates} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                        try:
                            output = run_1day_reversal_screener(None, ticker_item, target_date=scan_date)
                            if output:
                                results.append(output)
                        except Exception:
                            pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(by=['WR_numeric'], ascending=[False]).reset_index(drop=True)
                df_results = df_results.drop(columns=['WR_numeric'])
                st.session_state.dr_results = df_results
            else:
                st.session_state.dr_results = pd.DataFrame()
            st.rerun()

    with col_info6:
        st.info("🔎 Live screening for 1 Day Reversal pattern (Red to Green)")

    if st.session_state.dr_results is not None:
        if not st.session_state.dr_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.dr_results)} stock** found")
            display_results_table(st.session_state.dr_results, "dr")
            csv = st.session_state.dr_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="1day_reversal_screener.csv", mime="text/csv", key="dl_dr")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    # ============================
    # Backtest 1 Day Reversal
    # ============================
    st.markdown('<div id="section_dr_bt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Backtest 1 Day Reversal</p>', unsafe_allow_html=True)

    col_bt6_input, col_bt6_btn = st.columns([2, 1])
    with col_bt6_input:
        ticker_list_dr = get_ticker_list_1dr()
        selected_ticker_dr = st.selectbox("Select Ticker :", options=ticker_list_dr, index=None, placeholder="Type or select a ticker...", key="ticker_dr_bt")
        selected_period_dr = st.selectbox("Select Period :", options=list(period_options.keys()), index=3, key="period_dr_bt")

    with col_bt6_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Backtest 1 Day Reversal", key="btn_bt_dr", use_container_width=True):
            if selected_ticker_dr:
                with st.spinner(f"Running backtest for {selected_ticker_dr}..."):
                    df_trades, summary = run_backtest_1dr(selected_ticker_dr, period=period_options[selected_period_dr])
                st.session_state.dr_bt_results = df_trades
                st.session_state.dr_bt_summary = summary
                st.rerun()
            else:
                st.error("❌ Please select a ticker first!")

    if st.session_state.dr_bt_results is not None and st.session_state.dr_bt_summary is not None:
        summary = st.session_state.dr_bt_summary
        st.markdown(f'<div class="success-box">✅ Backtest completed for {summary["ticker"]}!</div>', unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Trades", summary['total_trades'])
        with col_s2:
            st.metric("Winning Trades", summary['winning_trades'])
        with col_s3:
            st.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        with col_s4:
            st.metric("Avg P/L", f"{summary['avg_profit_loss']:.2f}%")
        display_backtest_table(st.session_state.dr_bt_results)

    st.markdown("---")

    # ============================
    # Volume Trend Screener
    # ============================
    st.markdown('<div id="section_vt"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Volume Trend Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Kriteria Volume Trend Screener", expanded=False):
        st.markdown("""
        **Indikator yang Digunakan:**
        - **Volume Ratio** = Volume hari ini / Volume MA 20
        - **OBV (On-Balance Volume)** = Akumulasi volume berdasarkan arah harga
        - **CMF (Chaikin Money Flow)** = Tekanan beli/jual dalam 20 hari
        - **PVT (Price-Volume Trend)** = Volume di-weight berdasarkan perubahan harga
        - **Divergence** = Deteksi divergensi antara harga dan OBV
        
        **Sinyal:**
        - **STRONG ACCUMULATION**: Volume tinggi, OBV naik kuat, CMF positif kuat
        - **ACCUMULATION**: Ada tanda akumulasi institusi
        - **HIDDEN ACCUMULATION**: Harga sideways/turun tapi OBV naik
        - **NEUTRAL**: Tidak ada sinyal signifikan
        - **HIDDEN DISTRIBUTION**: Harga naik tapi OBV turun
        - **DISTRIBUTION**: Ada tanda distribusi institusi
        - **STRONG DISTRIBUTION**: Volume tinggi, OBV turun kuat, CMF negatif kuat
        
        **Interpretasi CMF:**
        - CMF > 0.25 : Akumulasi kuat
        - CMF 0.1 - 0.25 : Akumulasi moderat
        - CMF -0.1 - 0.1 : Netral
        - CMF -0.25 - -0.1 : Distribusi moderat
        - CMF < -0.25 : Distribusi kuat
        """)
    
    # Initialize session state
    if 'vt_results' not in st.session_state:
        st.session_state.vt_results = None
    
    col_vt_input, col_vt_btn = st.columns([2, 1])
    with col_vt_input:
        vt_scan_dates = st.date_input("Select Date(s) to Scan:", value=[datetime.now().date()], key="vt_dates")
    
    with col_vt_btn:
        st.write("")
        st.write("")
        if st.button("🔎 Run Volume Trend Screener", key="btn_vt", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_vt)
            
            for date_idx, scan_date in enumerate(vt_scan_dates):
                for idx, ticker_item in enumerate(tickers_vt):
                    progress = ((date_idx * total_tickers) + idx + 1) / (len(vt_scan_dates) * total_tickers)
                    progress_bar.progress(progress)
                    status_text.text(f"Date {date_idx + 1}/{len(vt_scan_dates)} | Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        output = run_volume_trend_screener(ticker_item, target_date=scan_date)
                        if output:
                            results.append(output)
                    except Exception:
                        pass
            
            progress_bar.empty()
            status_text.empty()
            
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
                st.session_state.vt_results = df_results
            else:
                st.session_state.vt_results = pd.DataFrame()
            st.rerun()
    
    st.info("🔎 Detect accumulation and distribution activity based on volume analysis")
    
    if st.session_state.vt_results is not None:
        if not st.session_state.vt_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.vt_results)} stock** found")
            display_results_table(st.session_state.vt_results, "vt")
            csv = st.session_state.vt_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="volume_trend_screener.csv", mime="text/csv", key="dl_vt")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    st.markdown("---")

    # ============================
    # Volume Profile Screener (Below VAL)
    # ============================
    st.markdown('<div id="section_vp"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">📈 Volume Profile Screener (Below VAL)</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Volume Profile", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Harga saat ini (Close) berada di bawah VAL (Value Area Low).
        - Lookback 20 bar terakhir untuk perhitungan Volume Profile.
        - Average 20-Day Transaction Value >= 5 Billion Rupiah.
        
        **Volume Profile Logic:**
        - Menghitung distribusi volume berdasarkan harga (Volume Profile).
        - Mencari POC (Point of Control), VAH (Value Area High), dan VAL (Value Area Low).
        - Jika harga turun dan berada di bawah VAL, mengindikasikan harga berada di area "discount" atau potensi oversold jangka pendek.
        
        **Columns:**
        - **POC**: Point of Control (harga dengan volume terbanyak).
        - **VAH**: Value Area High (batas atas area value 70%).
        - **VAL**: Value Area Low (batas bawah area value 70%).
        """)

    # Date picker & Run button
    col_date_vp, col_btn_vp, col_info_vp = st.columns([1, 1, 2])
    with col_date_vp:
        selected_date_vp = st.date_input("📅 Tanggal :", value=date.today(), key="date_vp", format="DD/MM/YYYY")
    with col_btn_vp:
        if st.button("🚀 Run VP Screener", key="btn_vp", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_vp)

            with st.spinner(f"Scanning {total_tickers} tickers..."):
                for idx, ticker_item in enumerate(tickers_vp):
                    progress = (idx + 1) / total_tickers
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        # Memanggil fungsi dari screener_vp.py
                        output = run_vp_screener(None, ticker_item, target_date=selected_date_vp)
                        if output:
                            results.append(output)
                    except Exception:
                        pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                st.session_state.vp_results = df_results
            else:
                st.session_state.vp_results = pd.DataFrame()
            st.rerun()

    with col_info_vp:
        st.info("🔎 Scan for stocks where current price is below Value Area Low (VAL)")

    if st.session_state.vp_results is not None:
        if not st.session_state.vp_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.vp_results)} stock** found")
            display_results_table(st.session_state.vp_results, "vp")
            csv = st.session_state.vp_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="volume_profile_screener.csv", mime="text/csv", key="dl_vp")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    st.markdown("---")


    # Footer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem;">
        <p>Auto Stock Screener by Rizky Aditya Tara | Data provided by Yahoo Finance</p>
        <p>⚠️ Disclaimer : This tool is for educational purposes only. Not financial advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()