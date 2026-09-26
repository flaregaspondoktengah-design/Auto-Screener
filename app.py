# BSJP : Stock Screener Streamlit Application
# Aplikasi untuk screening saham Indonesia dengan berbagai jenis screener

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
from screener_bullish_div import run_bullish_divergence_screener, tickers as tickers_bd
from screener_sideways import run_sideways_screener, tickers as tickers_dz

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
    .streamlit-expanderHeader {
        color: #757575 !important;
    }
    div[data-testid="stExpander"] summary p {
        color: #757575 !important;
    }
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
        border: 1px solid rgba(128, 128, 128, 0.3);
        white-space: nowrap;
        color: inherit; 
    }
    .custom-table tr:nth-child(even) {
        background-color: rgba(128, 128, 128, 0.15);
    }
    .custom-table tr:hover {
        background-color: rgba(30, 136, 229, 0.2);
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
if 'bd_results' not in st.session_state:
    st.session_state.bd_results = None

if 'v11_results' not in st.session_state:
    st.session_state.v11_results = None
if 'v11_bt_results' not in st.session_state:
    st.session_state.v11_bt_results = None
if 'v11_bt_summary' not in st.session_state:
    st.session_state.v11_bt_summary = None

if 'v13_results' not in st.session_state:
    st.session_state.v13_results = None
if 'v13_bt_results' not in st.session_state:
    st.session_state.v13_bt_results = None
if 'v13_bt_summary' not in st.session_state:
    st.session_state.v13_bt_summary = None

if 'bb_results' not in st.session_state:
    st.session_state.bb_results = None
if 'bb_bt_results' not in st.session_state:
    st.session_state.bb_bt_results = None
if 'bb_bt_summary' not in st.session_state:
    st.session_state.bb_bt_summary = None

if 'dz_results' not in st.session_state:
    st.session_state.dz_results = None

# --- Helper Functions ---
def clear_all():
    st.session_state.bd_results = None
    st.session_state.v11_results = None
    st.session_state.v11_bt_results = None
    st.session_state.v11_bt_summary = None
    st.session_state.v13_results = None
    st.session_state.v13_bt_results = None
    st.session_state.v13_bt_summary = None
    st.session_state.bb_results = None
    st.session_state.bb_bt_results = None
    st.session_state.bb_bt_summary = None
    st.session_state.dz_results = None

def get_dates_in_range(date_input):
    if isinstance(date_input, tuple):
        if len(date_input) == 0:
            return [date.today()]
        elif len(date_input) == 1:
            single_date = date_input[0]
            if single_date is None:
                return [date.today()]
            return [single_date]
        else:
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
        if date_input is None:
            return [date.today()]
        return [date_input]

def format_signal(signal):
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
    try:
        value = float(str(value_str).replace('%', '').replace('x', '').strip())
        if value >= 80: return 'cell-green'
        elif value >= 60: return 'cell-yellow'
        elif value >= 50: return 'cell-orange'
        else: return 'cell-red'
    except: return ''

def get_color_class_for_ratio(value_str):
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value > 2: return 'cell-green'
        elif value >= 1.5: return 'cell-yellow'
        elif value >= 1: return 'cell-orange'
        else: return 'cell-red'
    except: return ''

def get_color_class_for_rrr(value_str):
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value >= 2: return 'cell-green'
        elif value > 1.5: return 'cell-yellow'
        elif value >= 1: return 'cell-orange'
        else: return 'cell-red'
    except: return ''

def get_color_class_for_compression_ratio(value_str):
    try:
        value = float(str(value_str).replace('x', '').replace('X', '').strip())
        if value <= 0.8: return 'cell-green'
        elif value <= 1.0: return 'cell-yellow'
        elif value <= 1.2: return 'cell-orange'
        else: return 'cell-red'
    except: return ''

def get_color_class_for_spread(value_str):
    try:
        value = float(str(value_str).replace('%', '').replace('x', '').strip())
        if value <= 1: return 'cell-green'
        elif value <= 2: return 'cell-yellow'
        elif value <= 3: return 'cell-orange'
        else: return 'cell-red'
    except: return ''

def get_color_class_for_pct_change(value_str):
    try:
        value = float(str(value_str).replace('%', '').replace('+', '').strip())
        if value > 0: return 'cell-green'
        elif value < 0: return 'cell-red'
        else: return ''
    except: return ''

def get_color_class_for_position(value_str):
    value_str = str(value_str).strip()
    if value_str == 'Bullish': return 'cell-green'
    elif value_str == 'Bearish': return 'cell-red'
    elif value_str == 'Neutral': return 'cell-yellow'
    return ''

def get_color_class_for_vt_signal(value_str):
    value_str = str(value_str).strip()
    if value_str in ['STRONG ACCUMULATION', 'ACCUMULATION']: return 'cell-green'
    elif value_str in ['HIDDEN ACCUMULATION', 'HIDDEN DISTRIBUTION']: return 'cell-yellow'
    elif value_str in ['DISTRIBUTION', 'STRONG DISTRIBUTION']: return 'cell-red'
    return ''

def format_colored_cell(value, css_class):
    if css_class:
        return f'<span class="{css_class}">{value}</span>'
    return str(value)

def display_results_table(df, key_prefix=""):
    if df is None or df.empty: return
    
    pct_columns = ['WR', 'Correlation']
    position_column = 'Position'
    ratio_columns = ['Inflow Ratio', 'Vol Ratio', 'Daily Vol Ratio']
    avg_val_column = 'Avg Val 20D (B)'
    rrr_column = 'RRR'
    compression_ratio_column = 'Compression Ratio'
    spread_column = 'Spread%'
    pct_change_column = '1D Return'
    obv_trend_column = 'OBV Trend'
    pvt_trend_column = 'PVT Trend'
    obv_div_column = 'OBV Div'
    macd_div_column = 'MACD Div'
    cmf_column = 'CMF'
    
    html = '<table class="custom-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            
            if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) or col in ('RSI OS', 'Stoch OS'):
                if value == '☑':
                    html += f'<td><span class="check-yes">☑</span></td>'
                else:
                    html += f'<td></td>'
            elif col == 'Signal':
                signal_val = str(value).strip()
                if signal_val in ['STRONG ACCUMULATION', 'ACCUMULATION', 'HIDDEN ACCUMULATION', 
                                   'NEUTRAL', 'HIDDEN DISTRIBUTION', 'DISTRIBUTION', 'STRONG DISTRIBUTION']:
                    css_class = get_color_class_for_vt_signal(value)
                    html += f'<td>{format_colored_cell(value, css_class)}</td>'
                else:
                    html += f'<td>{format_signal(value)}</td>'
            elif col == position_column:
                value_str = str(value).strip()
                if value_str.endswith('%'):
                    css_class = get_color_class_for_percentage(value)
                else:
                    css_class = get_color_class_for_position(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == obv_trend_column:
                if value == 'Up':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Down':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            elif col == pvt_trend_column:
                if value == 'Up':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Down':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            elif col == obv_div_column:
                if value == 'Bullish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Bearish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            elif col == macd_div_column:
                if value == 'Bullish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                elif value == 'Bearish Divergence':
                    html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                else:
                    html += f'<td>{value}</td>'
            elif col == cmf_column:
                try:
                    cmf_val = float(str(value).replace('x', '').strip())
                    if cmf_val > 0.25: html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif cmf_val > 0.1: html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif cmf_val > 0: html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    elif cmf_val < -0.25: html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                    elif cmf_val < -0.1: html += f'<td>{format_colored_cell(value, "cell-red")}</td>'
                    elif cmf_val < 0: html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    else: html += f'<td>{value}</td>'
                except: html += f'<td>{value}</td>'
            elif col in pct_columns:
                css_class = get_color_class_for_percentage(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == rrr_column:
                css_class = get_color_class_for_rrr(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == compression_ratio_column:
                css_class = get_color_class_for_compression_ratio(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == spread_column:
                css_class = get_color_class_for_spread(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == pct_change_column:
                css_class = get_color_class_for_pct_change(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col in ratio_columns:
                css_class = get_color_class_for_ratio(value)
                html += f'<td>{format_colored_cell(value, css_class)}</td>'
            elif col == avg_val_column:
                try:
                    val = float(str(value).replace('x', '').strip())
                    if val >= 10: html += f'<td>{format_colored_cell(value, "cell-green")}</td>'
                    elif val >= 5: html += f'<td>{format_colored_cell(value, "cell-yellow")}</td>'
                    else: html += f'<td>{value}</td>'
                except: html += f'<td>{value}</td>'
            else:
                html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

def display_backtest_table(df):
    if df is None or df.empty: return
    
    html = '<table class="custom-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if value == '☑':
                    html += f'<td><span class="check-yes">☑</span></td>'
                else:
                    html += f'<td></td>'
            else:
                html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

period_options = {"1 Year": "1y", "2 Years": "2y", "3 Years": "3y", "5 Years": "5y", "10 Years": "10y"}

# --- Main Application ---
def main():
    st.markdown('<p class="main-header">💰 Auto Stock Screener</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar Legend & Clear All
    st.sidebar.markdown("**📋 Keterangan Kolom :**")
    with st.sidebar.expander("Lihat Keterangan", expanded=False):
        st.markdown("""
        **Tickers** : Kode emiten
        
        **Price** : Harga penutupan terakhir
        
        **1D Return** : Persentase perubahan harga dari harga kemarin
        
        **WR** : Win Rate
        
        **Trades** : Jumlah transaksi historis dengan setup sesuai kriteria
        
        **Position** : Posisi close dalam range harian
        
        **Correlation** : Rata-rata WR dari kondisi yang terpenuhi
        
        **Inflow Ratio** : Value hari ini / (MA20 * Vol MA20)
        
        **Daily Vol Ratio** : Volume 15 menit terakhir / rata-rata volume 15 menit harian
        
        **Vol Ratio** : Volume hari ini / Volume MA 20
        
        **Buy Price** : Harga entry (High hari ini + 1 tick)
        
        **SL Price** : Harga Stop Loss (Low hari ini - 1 tick)
        
        **Low Today / Low Yesterday** : Perbandingan harga terendah untuk melihat lower low.
        """)

    st.sidebar.markdown("---")

    if st.sidebar.button("🗑️ Clear All Results", use_container_width=True):
        clear_all()
        st.rerun()

    # ============================
    # Magic Screener V1.1
    # ============================
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

    col_date1, col_btn1, col_info1 = st.columns([1, 1, 2])
    with col_date1:
        selected_date_v11 = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_v11", format="DD/MM/YYYY")
    with col_btn1:
        if st.button("🚀 Run V1.1", key="btn_v11", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_v11)
            
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
                column_order = ['Date', 'Tickers', 'Price', 'Trades', 'WR', '1D Return', 'Position', 'Correlation', 'Inflow Ratio', 'Daily Vol Ratio', 'Vol Ratio']
                df_results = df_results[[col for col in column_order if col in df_results.columns]]
                
                df_results['Price_numeric'] = df_results['Price'].str.replace(',', '').astype(float)
                df_results['1D_Return_numeric'] = df_results['1D Return'].str.rstrip('%').astype(float)
                df_results['WR_numeric'] = df_results['WR'].str.rstrip('%').astype(float)
                df_results = df_results.sort_values(
                    by=['WR_numeric', '1D_Return_numeric', 'Price_numeric'],
                    ascending=[False, False, False]
                ).reset_index(drop=True)
                df_results = df_results.drop(columns=['Price_numeric', '1D_Return_numeric', 'WR_numeric'])
                
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
    
    # ============================
    # Magic Screener V1.3
    # ============================
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

    col_date2, col_btn2, col_info2 = st.columns([1, 1, 2])
    with col_date2:
        selected_date_v13 = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_v13", format="DD/MM/YYYY")
    with col_btn2:
        if st.button("🚀 Run V1.3", key="btn_v13", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_v13)
            
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
    
    # ============================
    # BB Reversal
    # ============================
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

    col_date3, col_btn3, col_info3 = st.columns([1, 1, 2])
    with col_date3:
        selected_date_bb = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_bb", format="DD/MM/YYYY")
    with col_btn3:
        if st.button("🚀 Run BB Reversal", key="btn_bb", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_bb)
            
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

    # ============================
    # Bullish Divergence Screener
    # ============================
    st.markdown('<p class="sub-header">📈 Bullish Divergence Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Bullish Divergence", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - Low hari ini < Low kemarin (Membuat lower low / sisa downtrend).
        - Close hari ini berada di setengah atas bar (Upper half = menolak harga turun).
        - Awesome Oscillator (AO) < 0 (Momentum indikator masih bearish).
        
        **Exit Strategy :**
        - **Buy Price**: High hari ini + 1 tick.
        - **Stop Loss**: Low hari ini - 1 tick.
        
        **Columns:**
        - **Low Today / Low Yesterday**: Perbandingan harga terendah untuk melihat lower low.
        - **AO**: Awesome Oscillator (SMA 5 - SMA 34 dari Median Price).
        - **Buy Price**: Harga entry (High hari ini + 1 tick).
        - **SL Price**: Harga Stop Loss (Low hari ini - 1 tick).
        """)

    col_date_bd, col_btn_bd, col_info_bd = st.columns([1, 1, 2])
    with col_date_bd:
        selected_date_bd = st.date_input("📅 Tanggal :", value=date.today(), key="date_bd", format="DD/MM/YYYY")
    with col_btn_bd:
        if st.button("🚀 Run Bullish Divergence", key="btn_bd", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_bd)

            with st.spinner(f"Scanning {total_tickers} tickers..."):
                for idx, ticker_item in enumerate(tickers_bd):
                    progress = (idx + 1) / total_tickers
                    progress_bar.progress(progress)
                    status_text.text(f"Processing {idx + 1}/{total_tickers}: {ticker_item.replace('.JK', '')}")
                    try:
                        output = run_bullish_divergence_screener(None, ticker_item, target_date=selected_date_bd)
                        if output:
                            results.append(output)
                    except Exception:
                        pass

            progress_bar.empty()
            status_text.empty()

            if results:
                df_results = pd.DataFrame(results)
                st.session_state.bd_results = df_results
            else:
                st.session_state.bd_results = pd.DataFrame()
            st.rerun()

    with col_info_bd:
        st.info("🔎 Scan for stocks showing bullish divergence (lower low but close in upper half)")

    if st.session_state.bd_results is not None:
        if not st.session_state.bd_results.empty:
            st.markdown('<div class="success-box">✅ Scan Completed!</div>', unsafe_allow_html=True)
            st.write(f"📊 **{len(st.session_state.bd_results)} stock** found")
            display_results_table(st.session_state.bd_results, "bd")
            csv = st.session_state.bd_results.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", data=csv, file_name="bullish_divergence_screener.csv", mime="text/csv", key="dl_bd")
        else:
            st.warning("⚠️ No stocks meet the criteria")

    st.markdown("---")

    # ============================
    # Sideways Screener
    # ============================
    st.markdown('<p class="sub-header">📈 Sideways Screener</p>', unsafe_allow_html=True)
    
    with st.expander("📋 Buy Criteria Sideways Screener", expanded=False):
        st.markdown("""
        **Main Criteria :**
        - MA5, MA10, MA20 Clustered (sideways detection)
        - Average 20-Day Transaction Value >= 5 Billion Rupiah
        """)

    col_date8, col_btn8, col_info8 = st.columns([1, 1, 2])
    with col_date8:
        selected_date_dz = st.date_input("📅 Tanggal :", value=(date.today(), date.today()), key="date_dz", format="DD/MM/YYYY")
    with col_btn8:
        if st.button("🚀 Run Sideways", key="btn_dz", use_container_width=True):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_tickers = len(tickers_dz)
            
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