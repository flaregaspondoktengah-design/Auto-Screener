# Backtest FVG Screener
# Backtest module for Fair Value Gap strategy
# 
# Strategy:
# - Entry: When Bullish FVG detected
# - Exit Options:
#   1. Price retraces to FVG zone (take profit at FVG low)
#   2. Max holding period: 10 trading days
#   3. Stop loss: -5% below entry

import yfinance as yf
import pandas as pd
import numpy as np
import warnings
from datetime import date, timedelta

# Suppress FutureWarning from yfinance
warnings.simplefilter(action='ignore', category=FutureWarning)


def apply_fraksi_harga(price):
    """Determines the tick size and applies rounding based on Indonesian stock exchange rules."""
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


def calculate_fvg(df):
    """
    Mengidentifikasi dan menghitung Fair Value Gap (FVG) bullish dan bearish.
    """
    df_copy = df.copy()

    if 'High' not in df_copy.columns or 'Low' not in df_copy.columns:
        raise ValueError("DataFrame harus memiliki kolom 'High' dan 'Low'.")

    df_copy['Bullish_FVG'] = np.nan
    df_copy['Bearish_FVG'] = np.nan

    for i in range(1, len(df_copy) - 1):
        high_prev = df_copy['High'].iloc[i-1]
        low_prev = df_copy['Low'].iloc[i-1]
        high_next = df_copy['High'].iloc[i+1]
        low_next = df_copy['Low'].iloc[i+1]

        if high_prev < low_next:
            fvg_bullish_value = low_next - high_prev
            df_copy.loc[df_copy.index[i], 'Bullish_FVG'] = fvg_bullish_value

        if low_prev > high_next:
            fvg_bearish_value = low_prev - high_next
            df_copy.loc[df_copy.index[i], 'Bearish_FVG'] = fvg_bearish_value

    return df_copy


def get_ticker_list():
    """Return list of available tickers for backtest."""
    from screener_fvg import tickers
    return [t.replace('.JK', '') for t in tickers]


def run_backtest_for_ticker(ticker, period="5y"):
    """
    Run backtest for a single ticker with FVG strategy.
    
    Strategy Rules:
    1. Entry: When Bullish FVG is detected (High[i-1] < Low[i+1])
    2. Entry price: Close of the candle where FVG is identified
    3. Exit conditions:
       - Take Profit: Price retraces to FVG zone (Low of FVG)
       - Stop Loss: -5% below entry
       - Max holding: 10 trading days
    
    Args:
        ticker: Stock ticker symbol (without .JK suffix)
        period: Period to backtest (e.g., "1y", "5y")
    
    Returns:
        tuple: (DataFrame of trades, dict of summary statistics)
    """
    symbol = f"{ticker}.JK"
    
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False, auto_adjust=True)
    except Exception as e:
        return None, {'error': str(e)}
    
    if df.empty:
        return None, {'error': 'No data available'}
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Standardize column names
    new_columns = []
    for col in df.columns:
        if col.lower() == 'adj close':
            new_columns.append('Close')
        else:
            new_columns.append(col.capitalize())
    df.columns = new_columns
    df = df.loc[:, ~df.columns.duplicated(keep='last')]
    
    if len(df) < 50:
        return None, {'error': 'Insufficient data'}
    
    # Calculate FVG
    try:
        df = calculate_fvg(df)
    except Exception as e:
        return None, {'error': str(e)}
    
    # Reset index to make Date a column
    df = df.reset_index()
    df.rename(columns={'index': 'Date', 'Datetime': 'Date'}, inplace=True)
    
    # Find all Bullish FVG signals
    trades = []
    
    for i in range(2, len(df) - 11):  # Need at least 11 candles for 10-day hold
        # Check for Bullish FVG at this candle (middle candle)
        if pd.notna(df['Bullish_FVG'].iloc[i]):
            # FVG zone
            fvg_high = float(df['Low'].iloc[i+1])  # Low of candle after middle
            fvg_low = float(df['High'].iloc[i-1])  # High of candle before middle
            
            # Entry at close of middle candle
            entry_date = df['Date'].iloc[i]
            entry_price = float(df['Close'].iloc[i])
            
            # Check filters
            volume = float(df['Volume'].iloc[i])
            transaction_value = (entry_price * volume) / 1_000_000_000
            
            if entry_price < 100 or transaction_value < 5:
                continue
            
            # Exit conditions
            stop_loss_pct = 0.05
            stop_loss_price = entry_price * (1 - stop_loss_pct)
            take_profit_price = fvg_low  # Target is FVG low (retracement)
            
            exit_price = None
            exit_date = None
            exit_reason = None
            holding_days = 0
            max_hold_days = 10
            
            # Check next 10 candles for exit
            for j in range(i + 1, min(i + 11, len(df))):
                holding_days = j - i
                low = float(df['Low'].iloc[j])
                high = float(df['High'].iloc[j])
                close = float(df['Close'].iloc[j])
                
                # Check if price hit take profit (retraced to FVG zone)
                if low <= fvg_high and low >= fvg_low:
                    # Price is in FVG zone
                    exit_price = fvg_high  # Exit at FVG high
                    exit_date = df['Date'].iloc[j]
                    exit_reason = "FVG Hit"
                    break
                
                # Check stop loss
                if low <= stop_loss_price:
                    exit_price = stop_loss_price
                    exit_date = df['Date'].iloc[j]
                    exit_reason = "Stop Loss"
                    break
                
                # Check max holding period
                if holding_days >= max_hold_days:
                    exit_price = close
                    exit_date = df['Date'].iloc[j]
                    exit_reason = "Max Days"
                    break
            
            if exit_price is None:
                # If we reach here, use the last available price
                exit_price = float(df['Close'].iloc[min(i + 10, len(df) - 1)])
                exit_date = df['Date'].iloc[min(i + 10, len(df) - 1)]
                exit_reason = "End Period"
                holding_days = min(10, len(df) - 1 - i)
            
            # Calculate profit/loss
            profit_loss_pct = ((exit_price - entry_price) / entry_price) * 100
            
            # Determine win/loss
            is_win = profit_loss_pct > 0
            
            trade = {
                'Entry Date': entry_date.strftime('%Y-%m-%d') if hasattr(entry_date, 'strftime') else str(entry_date)[:10],
                'Entry Price': f'{apply_fraksi_harga(entry_price):,.0f}',
                'FVG Low': f'{apply_fraksi_harga(fvg_low):,.0f}',
                'FVG High': f'{apply_fraksi_harga(fvg_high):,.0f}',
                'Exit Date': exit_date.strftime('%Y-%m-%d') if hasattr(exit_date, 'strftime') else str(exit_date)[:10],
                'Exit Price': f'{apply_fraksi_harga(exit_price):,.0f}',
                'Hold Days': str(holding_days),
                'Exit Reason': exit_reason,
                'P/L %': f'{profit_loss_pct:+.2f}%',
                'Result': '☑' if is_win else ''
            }
            trades.append(trade)
    
    # Calculate summary statistics
    if trades:
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['Result'] == '☑')
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Calculate average P/L
        pnl_values = [float(t['P/L %'].replace('%', '').replace('+', '')) for t in trades]
        avg_profit_loss = np.mean(pnl_values) if pnl_values else 0
        
        # Calculate average holding days
        holding_days = [int(t['Hold Days']) for t in trades]
        avg_holding_days = np.mean(holding_days) if holding_days else 0
        
        # Count exit reasons
        fvg_hit_count = sum(1 for t in trades if t['Exit Reason'] == 'FVG Hit')
        stop_loss_count = sum(1 for t in trades if t['Exit Reason'] == 'Stop Loss')
        max_days_count = sum(1 for t in trades if t['Exit Reason'] == 'Max Days')
        
        summary = {
            'ticker': ticker,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'avg_profit_loss': avg_profit_loss,
            'avg_holding_days': avg_holding_days,
            'fvg_hit_rate': (fvg_hit_count / total_trades) * 100 if total_trades > 0 else 0,
            'stop_loss_rate': (stop_loss_count / total_trades) * 100 if total_trades > 0 else 0,
            'max_days_rate': (max_days_count / total_trades) * 100 if total_trades > 0 else 0
        }
    else:
        summary = {
            'ticker': ticker,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'avg_profit_loss': 0,
            'avg_holding_days': 0,
            'fvg_hit_rate': 0,
            'stop_loss_rate': 0,
            'max_days_rate': 0
        }
    
    df_trades = pd.DataFrame(trades) if trades else pd.DataFrame()
    
    return df_trades, summary


if __name__ == "__main__":
    # Test backtest
    ticker = "BBCA"
    print(f"Running backtest for {ticker}...")
    
    df_trades, summary = run_backtest_for_ticker(ticker, period="2y")
    
    if df_trades is not None and not df_trades.empty:
        print("\nSummary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print("\nTrades:")
        print(df_trades.to_string(index=False))
    else:
        print(f"No trades found for {ticker}")