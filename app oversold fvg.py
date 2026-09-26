import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime
import subprocess
import sys

# Import screeners
from screener_v11 import run_full_screener, run_magic_screener, tickers as tickers_v11
from screener_v13 import run_magic_screener_v13, tickers as tickers_v13
from screener_bb_reversal import run_bb_reversal_screener, tickers as tickers_bb
from screener_iv_rank import run_iv_rank_screener, tickers as tickers_iv
from screener_bullish_harami import run_bullish_harami_screener, tickers as tickers_bh
from screener_1day_reversal import run_1day_reversal_screener, tickers as tickers_1dr
from screener_decreasing_highs import run_decreasing_highs_screener, tickers as tickers_dh
from screener_sideways import run_sideways_screener, tickers as tickers_sw
from screener_fvg import run_fvg_screener, tickers as tickers_fvg
from screener_oversold import run_oversold_screener, tickers as tickers_os

# Page config
st.set_page_config(
    page_title="IDX Stock Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .screener-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stDataFrame {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    screeners = ['v11', 'v13', 'bb', 'iv', 'bh', 'dr', 'dh', 'sw', 'fvg', 'os']
    for s in screeners:
        if f'{s}_results' not in st.session_state:
            st.session_state[f'{s}_results'] = None

init_session_state()

# Helper function for progress display
def run_screener_with_progress(screener_func, tickers_list, screener_type='single'):
    """
    Run screener with progress bar showing x/631 format
    """
    results = []
    total_tickers = len(tickers_list)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers_list):
        progress = (i + 1) / total_tickers
        progress_bar.progress(progress)
        status_text.text(f"Scanning: {ticker} ({i+1}/{total_tickers})")
        
        try:
            if screener_type == 'single':
                # For screeners that take single ticker
                result = screener_func([ticker])
                if result is not None and len(result) > 0:
                    results.append(result)
            else:
                # For screeners that take full list
                pass
        except Exception:
            pass
        
        time.sleep(0.03)
    
    progress_bar.empty()
    status_text.empty()
    
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()

# ==========================================
# MAIN PAGE - ALL SCREENERS IN ONE PAGE
# ==========================================

st.markdown('<p class="main-header">📊 IDX Stock Screener</p>', unsafe_allow_html=True)
st.markdown(f"**📅 Tanggal:** {datetime.now().strftime('%Y-%m-%d')} | **⏰ Waktu:** {datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# Quick Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Screeners", "10")
with col2:
    st.metric("Total Tickers", f"{len(tickers_v11)}")
with col3:
    st.metric("Market", "IDX")
with col4:
    active_screeners = sum(1 for s in ['v11', 'v13', 'bb', 'iv', 'bh', 'dr', 'dh', 'sw', 'fvg', 'os'] 
                          if st.session_state.get(f'{s}_results') is not None)
    st.metric("Active Results", active_screeners)

st.markdown("---")

# ==========================================
# SCREENER BUTTONS SECTION
# ==========================================

st.markdown("### 🚀 Jalankan Screener")
st.markdown("Klik tombol untuk menjalankan screener yang diinginkan:")

# Row 1
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    run_v11 = st.button("📈 V11 - Magic", key="btn_v11", use_container_width=True)
with col2:
    run_v13 = st.button("📊 V13 - Momentum", key="btn_v13", use_container_width=True)
with col3:
    run_bb = st.button("🔄 BB Reversal", key="btn_bb", use_container_width=True)
with col4:
    run_iv = st.button("📉 IV Rank", key="btn_iv", use_container_width=True)
with col5:
    run_bh = st.button("🐂 Bullish Harami", key="btn_bh", use_container_width=True)

# Row 2
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    run_dr = st.button("↩️ 1 Day Reversal", key="btn_dr", use_container_width=True)
with col2:
    run_dh = st.button("📉 Decreasing Highs", key="btn_dh", use_container_width=True)
with col3:
    run_sw = st.button("↔️ Sideways", key="btn_sw", use_container_width=True)
with col4:
    run_fvg = st.button("📊 FVG", key="btn_fvg", use_container_width=True)
with col5:
    run_os = st.button("🔴 Oversold", key="btn_os", use_container_width=True)

st.markdown("---")

# ==========================================
# SCREENER EXECUTION
# ==========================================

# V11 Screener
if run_v11:
    st.markdown("### 📈 Running V11 - Magic Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_full_screener()
            st.session_state.v11_results = result
            st.success(f"✅ V11 Selesai! Ditemukan {len(result.data) if hasattr(result, 'data') else 0} saham")
        except Exception as e:
            st.error(f"Error: {e}")

# V13 Screener
if run_v13:
    st.markdown("### 📊 Running V13 - Momentum Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(tickers_v13):
                progress = (i + 1) / len(tickers_v13)
                progress_bar.progress(progress)
                status_text.text(f"Scanning: {ticker} ({i+1}/{len(tickers_v13)})")
                
                try:
                    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
                    if not df.empty and len(df) >= 200:
                        result = run_magic_screener_v13(df, ticker)
                        if result:
                            results.append(result)
                except:
                    pass
                time.sleep(0.03)
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                st.session_state.v13_results = pd.DataFrame(results)
                st.success(f"✅ V13 Selesai! Ditemukan {len(results)} saham")
            else:
                st.session_state.v13_results = pd.DataFrame()
                st.warning("Tidak ada saham yang memenuhi kriteria V13")
        except Exception as e:
            st.error(f"Error: {e}")

# BB Reversal Screener
if run_bb:
    st.markdown("### 🔄 Running BB Reversal Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_bb_reversal_screener, tickers_bb)
            st.session_state.bb_results = result
            if len(result) > 0:
                st.success(f"✅ BB Reversal Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria BB Reversal")
        except Exception as e:
            st.error(f"Error: {e}")

# IV Rank Screener
if run_iv:
    st.markdown("### 📉 Running IV Rank Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_iv_rank_screener, tickers_iv)
            st.session_state.iv_results = result
            if len(result) > 0:
                st.success(f"✅ IV Rank Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria IV Rank")
        except Exception as e:
            st.error(f"Error: {e}")

# Bullish Harami Screener
if run_bh:
    st.markdown("### 🐂 Running Bullish Harami Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_bullish_harami_screener, tickers_bh)
            st.session_state.bh_results = result
            if len(result) > 0:
                st.success(f"✅ Bullish Harami Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria Bullish Harami")
        except Exception as e:
            st.error(f"Error: {e}")

# 1 Day Reversal Screener
if run_dr:
    st.markdown("### ↩️ Running 1 Day Reversal Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_1day_reversal_screener, tickers_1dr)
            st.session_state.dr_results = result
            if len(result) > 0:
                st.success(f"✅ 1 Day Reversal Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria 1 Day Reversal")
        except Exception as e:
            st.error(f"Error: {e}")

# Decreasing Highs Screener
if run_dh:
    st.markdown("### 📉 Running Decreasing Highs Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_decreasing_highs_screener, tickers_dh)
            st.session_state.dh_results = result
            if len(result) > 0:
                st.success(f"✅ Decreasing Highs Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria Decreasing Highs")
        except Exception as e:
            st.error(f"Error: {e}")

# Sideways Screener
if run_sw:
    st.markdown("### ↔️ Running Sideways Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_sideways_screener, tickers_sw)
            st.session_state.sw_results = result
            if len(result) > 0:
                st.success(f"✅ Sideways Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria Sideways")
        except Exception as e:
            st.error(f"Error: {e}")

# FVG Screener
if run_fvg:
    st.markdown("### 📊 Running FVG Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_fvg_screener, tickers_fvg)
            st.session_state.fvg_results = result
            if len(result) > 0:
                st.success(f"✅ FVG Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria FVG")
        except Exception as e:
            st.error(f"Error: {e}")

# Oversold Screener
if run_os:
    st.markdown("### 🔴 Running Oversold Screener...")
    with st.spinner("Scanning all tickers..."):
        try:
            result = run_screener_with_progress(run_oversold_screener, tickers_os)
            st.session_state.os_results = result
            if len(result) > 0:
                st.success(f"✅ Oversold Selesai! Ditemukan {len(result)} saham")
            else:
                st.warning("Tidak ada saham yang memenuhi kriteria Oversold")
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# RESULTS DISPLAY SECTION
# ==========================================

st.markdown("---")
st.markdown("### 📋 Hasil Screener")

# Create tabs for each screener
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📈 V11", "📊 V13", "🔄 BB Reversal", "📉 IV Rank", "🐂 Bullish Harami",
    "↩️ 1 Day Rev", "📉 Dec Highs", "↔️ Sideways", "📊 FVG", "🔴 Oversold"
])

def display_screener_results(results, tab, name):
    """Display results in a tab"""
    with tab:
        if results is not None and len(results) > 0:
            # Get DataFrame
            if hasattr(results, 'data'):
                df = results.data
            else:
                df = results
            
            st.success(f"✅ Ditemukan {len(df)} saham")
            
            # Display the dataframe
            st.dataframe(results, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {name} (CSV)",
                data=csv,
                file_name=f"{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
                key=f"dl_{name}"
            )
        else:
            st.info(f"Belum ada hasil. Klik tombol {name} di atas untuk menjalankan screener.")

# Display results in each tab
display_screener_results(st.session_state.v11_results, tab1, "V11")
display_screener_results(st.session_state.v13_results, tab2, "V13")
display_screener_results(st.session_state.bb_results, tab3, "BB_Reversal")
display_screener_results(st.session_state.iv_results, tab4, "IV_Rank")
display_screener_results(st.session_state.bh_results, tab5, "Bullish_Harami")
display_screener_results(st.session_state.dr_results, tab6, "1Day_Reversal")
display_screener_results(st.session_state.dh_results, tab7, "Decreasing_Highs")
display_screener_results(st.session_state.sw_results, tab8, "Sideways")
display_screener_results(st.session_state.fvg_results, tab9, "FVG")
display_screener_results(st.session_state.os_results, tab10, "Oversold")

# ==========================================
# BACKTEST SECTION
# ==========================================

st.markdown("---")
st.markdown("### 🧪 Backtest")

st.markdown("Pilih backtest yang ingin dijalankan:")

col1, col2 = st.columns(2)
with col1:
    run_bt_fvg = st.button("📊 Run FVG Backtest", key="btn_bt_fvg", use_container_width=True)
with col2:
    run_bt_os = st.button("🔴 Run Oversold Backtest", key="btn_bt_os", use_container_width=True)

# FVG Backtest
if run_bt_fvg:
    st.markdown("#### 📊 FVG Backtest Results")
    with st.spinner("Running FVG Backtest..."):
        try:
            result = subprocess.run(
                [sys.executable, "backtest_fvg.py"],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                st.success("✅ FVG Backtest Selesai!")
                st.code(result.stdout)
            else:
                st.error(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            st.error("Backtest timeout. Proses terlalu lama.")
        except Exception as e:
            st.error(f"Error: {e}")

# Oversold Backtest
if run_bt_os:
    st.markdown("#### 🔴 Oversold Backtest Results")
    st.markdown("""
    **Strategi Oversold Backtest:**
    - Entry: RSI < 30 atau Stochastic %K < 20
    - Exit: Stop Loss 5%, Max Hold 10 hari, RSI > 70
    - Position: LONG (Buy)
    """)
    with st.spinner("Running Oversold Backtest..."):
        try:
            result = subprocess.run(
                [sys.executable, "backtest_oversold.py"],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode == 0:
                st.success("✅ Oversold Backtest Selesai!")
                st.code(result.stdout)
            else:
                st.error(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            st.error("Backtest timeout. Proses terlalu lama.")
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# SUMMARY TABLE
# ==========================================

st.markdown("---")
st.markdown("### 📊 Ringkasan Hasil Screener")

summary_data = []
screener_names = [
    ('v11', 'V11 - Magic Screener'),
    ('v13', 'V13 - Momentum'),
    ('bb', 'BB Reversal'),
    ('iv', 'IV Rank'),
    ('bh', 'Bullish Harami'),
    ('dr', '1 Day Reversal'),
    ('dh', 'Decreasing Highs'),
    ('sw', 'Sideways'),
    ('fvg', 'FVG'),
    ('os', 'Oversold')
]

for key, name in screener_names:
    results = st.session_state.get(f'{key}_results')
    if results is not None:
        if hasattr(results, 'data'):
            count = len(results.data)
        else:
            count = len(results)
        status = "✅" if count > 0 else "⚠️"
    else:
        count = 0
        status = "⬜"
    
    summary_data.append({
        "Screener": name,
        "Status": status,
        "Jumlah Saham": count
    })

st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>📊 IDX Stock Screener | Developed for Indonesian Stock Market Analysis</p>
    <p>Data provided by Yahoo Finance</p>
</div>
""", unsafe_allow_html=True)