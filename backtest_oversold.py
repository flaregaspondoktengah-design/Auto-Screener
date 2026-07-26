# Backtest Oversold Screener - RSI & Stochastic
# Backtest untuk strategi buy signal berdasarkan kondisi oversold

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_rsi(data, period=14):
    """Hitung RSI"""
    try:
        close = data['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        for i in range(period, len(gain)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    except:
        return None


def calculate_stochastic(data, k_period=10, k_smooth=5, d_period=5):
    """Hitung Stochastic Oscillator
    
    Args:
        k_period: %K Length (default 10)
        k_smooth: %K Smoothing (default 5)
        d_period: %D Smoothing (default 5)
    """
    try:
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Hitung raw %K
        lowest_low = low.rolling(window=k_period, min_periods=k_period).min()
        highest_high = high.rolling(window=k_period, min_periods=k_period).max()
        
        raw_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        
        # Apply %K Smoothing
        smooth_k = raw_k.rolling(window=k_smooth, min_periods=k_smooth).mean()
        
        # Hitung %D (moving average dari smoothed %K)
        smooth_d = smooth_k.rolling(window=d_period, min_periods=d_period).mean()
        
        return smooth_k, smooth_d
    except:
        return None, None


def get_ticker_list():
    """Mengembalikan list ticker untuk backtest"""
    from screener_oversold import tickers
    return [t.replace('.JK', '') for t in tickers]


def run_backtest_for_ticker(ticker_symbol, period="2y", 
                             rsi_threshold=30, stoch_threshold=20,
                             hold_days=5, stop_loss_pct=5):
    """
    Backtest strategi oversold (BUY signal)
    
    Entry: Ketika RSI < 30 ATAU Stochastic %K < 20 (oversold condition)
    Exit: 
        - Stop loss 5%
        - Max holding 5 hari
        - RSI naik di atas 70 (overbought)
    
    Returns:
        DataFrame hasil trades, Dictionary summary
    """
    symbol = ticker_symbol if '.JK' in ticker_symbol else f"{ticker_symbol}.JK"
    
    try:
        # Download data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, auto_adjust=False)
        
        if data.empty or len(data) < 50:
            return None, None
        
        # Hitung indikator
        data['RSI'] = calculate_rsi(data)
        data['Stoch_K'], data['Stoch_D'] = calculate_stochastic(data)
        
        # Inisialisasi
        trades = []
        position = None
        entry_date = None
        entry_price = None
        entry_rsi = None
        entry_stoch = None
        
        for i in range(30, len(data)):  # Mulai dari baris 30 untuk RSI stabil
            current_date = data.index[i]
            current_close = data['Close'].iloc[i]
            current_rsi = data['RSI'].iloc[i]
            current_stoch_k = data['Stoch_K'].iloc[i]
            prev_close = data['Close'].iloc[i-1]
            
            if pd.isna(current_rsi) or pd.isna(current_stoch_k):
                continue
            
            # Jika tidak ada posisi, cek entry signal (oversold = BUY)
            if position is None:
                rsi_oversold = current_rsi < rsi_threshold
                stoch_oversold = current_stoch_k < stoch_threshold
                
                if rsi_oversold or stoch_oversold:
                    # Entry LONG signal (BUY)
                    position = 'LONG'
                    entry_date = current_date
                    entry_price = current_close
                    entry_rsi = current_rsi
                    entry_stoch = current_stoch_k
            
            # Jika ada posisi, cek exit conditions
            elif position == 'LONG':
                holding_days = (current_date - entry_date).days
                
                # Calculate P/L (untuk long: profit jika harga naik)
                pct_change = ((current_close - entry_price) / entry_price) * 100
                
                # Exit conditions:
                # 1. Stop loss (harga turun > stop_loss_pct)
                # 2. Max holding days
                # 3. RSI naik di atas 70 (overbought)
                
                exit_reason = None
                
                if pct_change < -stop_loss_pct:  # Loss (harga turun)
                    exit_reason = 'Stop Loss'
                elif holding_days >= hold_days:
                    exit_reason = 'Max Hold'
                elif current_rsi > 70:
                    exit_reason = 'RSI Overbought'
                
                if exit_reason:
                    trades.append({
                        'Date': entry_date.strftime('%Y-%m-%d'),
                        'Ticker': ticker_symbol.replace('.JK', ''),
                        'Entry Price': f"{entry_price:,.0f}".replace(',', '.'),
                        'Exit Price': f"{current_close:,.0f}".replace(',', '.'),
                        'RSI Entry': f"{entry_rsi:.1f}",
                        'Stoch Entry': f"{entry_stoch:.1f}",
                        'RSI Exit': f"{current_rsi:.1f}",
                        'Hold Days': holding_days,
                        'P/L %': f"{pct_change:.2f}%",
                        'Exit Reason': exit_reason
                    })
                    
                    position = None
                    entry_date = None
                    entry_price = None
        
        # Calculate summary
        if trades:
            df_trades = pd.DataFrame(trades)
            
            # Parse P/L for calculations
            pl_values = [float(t['P/L %'].replace('%', '')) for t in trades]
            winning_trades = sum(1 for pl in pl_values if pl > 0)
            
            summary = {
                'ticker': ticker_symbol.replace('.JK', ''),
                'total_trades': len(trades),
                'winning_trades': winning_trades,
                'win_rate': (winning_trades / len(trades)) * 100 if trades else 0,
                'avg_profit_loss': np.mean(pl_values) if pl_values else 0,
                'max_profit': max(pl_values) if pl_values else 0,
                'max_loss': min(pl_values) if pl_values else 0,
                'avg_hold_days': np.mean([t['Hold Days'] for t in trades]) if trades else 0
            }
            
            return df_trades, summary
        
        return None, None
        
    except Exception as e:
        print(f"Error in backtest for {ticker_symbol}: {e}")
        return None, None


if __name__ == "__main__":
    # Test backtest
    print("Running Backtest Oversold Screener...")
    print("-" * 60)
    
    df, summary = run_backtest_for_ticker("BBCA.JK", period="2y")
    
    if df is not None:
        print("\nSummary:")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        print("\nTrades:")
        print(df.to_string(index=False))
    else:
        print("No trades found or error occurred")
