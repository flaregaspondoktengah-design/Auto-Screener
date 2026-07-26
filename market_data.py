# BSJP : Market Data Module - Web Scraping for Foreign Flow & Top Broker
# Module ini berisi fungsi-fungsi untuk mengambil data pasar dari berbagai sumber

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# Headers untuk menghindari blocking
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


def get_foreign_flow_indopremier(ticker):
    """
    Mengambil data Net Foreign Flow dari Indopremier.
    
    Args:
        ticker (str): Kode ticker (contoh: ANTM, tanpa .JK)
    
    Returns:
        dict: {'net_foreign': float dalam Miliar, 'status': str}
    """
    try:
        # Indopremier stock page
        url = f"https://www.indopremier.com/saham/quote.php?symbol={ticker}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {'net_foreign': 0.0, 'status': 'error'}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Cari data foreign flow (struktur bisa berubah, perlu adaptasi)
        # Biasanya ada di tabel atau div tertentu
        foreign_data = soup.find_all(string=re.compile(r'Foreign|Net Buy|Net Sell'))
        
        net_foreign = 0.0
        
        # Parse nilai net foreign
        for text in foreign_data:
            parent = text.parent
            if parent:
                sibling = parent.find_next_sibling()
                if sibling:
                    value_text = sibling.get_text().strip()
                    # Parse nilai (contoh: "1.5B", "-2.3M", "500K")
                    match = re.search(r'([+-]?[\d,]+\.?\d*)\s*([BMK])?', value_text)
                    if match:
                        value = float(match.group(1).replace(',', ''))
                        unit = match.group(2) if match.group(2) else ''
                        
                        # Konversi ke Miliar
                        if unit == 'B':
                            net_foreign = value
                        elif unit == 'M':
                            net_foreign = value / 1000
                        elif unit == 'K':
                            net_foreign = value / 1000000
                        break
        
        return {
            'net_foreign': round(net_foreign, 2),
            'status': 'success'
        }
        
    except Exception as e:
        return {'net_foreign': 0.0, 'status': f'error: {str(e)}'}


def get_foreign_flow_idx(ticker):
    """
    Mengambil data Net Foreign Flow dari IDX Indonesia Stock Exchange.
    Alternative source untuk foreign flow.
    
    Args:
        ticker (str): Kode ticker (contoh: ANTM, tanpa .JK)
    
    Returns:
        dict: {'net_foreign': float dalam Miliar, 'status': str}
    """
    try:
        # IDX stock summary API (jika tersedia)
        url = f"https://www.idx.co.id/primary/Helper/GetSecuritySummary?ticker={ticker}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Parse data dari JSON response
            if data and 'foreign' in data:
                foreign = data['foreign']
                net_foreign = foreign.get('net', 0) / 1_000_000_000  # Konversi ke Miliar
                return {
                    'net_foreign': round(net_foreign, 2),
                    'status': 'success'
                }
        
        return {'net_foreign': 0.0, 'status': 'no data'}
        
    except Exception as e:
        return {'net_foreign': 0.0, 'status': f'error: {str(e)}'}


def get_top_broker_indopremier(ticker):
    """
    Mengambil data Top Broker Buy/Sell dari Indopremier.
    
    Args:
        ticker (str): Kode ticker (contoh: ANTM, tanpa .JK)
    
    Returns:
        dict: {'top_buy': str, 'top_sell': str, 'status': str}
    """
    try:
        url = f"https://www.indopremier.com/saham/quote.php?symbol={ticker}"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {'top_buy': '-', 'top_sell': '-', 'status': 'error'}
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        top_buy = '-'
        top_sell = '-'
        
        # Cari tabel broker summary
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # Cari header yang mengandung "Broker" atau "Top"
                    text = ' '.join([cell.get_text().lower() for cell in cells])
                    if 'buy' in text or 'beli' in text:
                        # Parse broker buy
                        broker_name = cells[0].get_text().strip()
                        volume = cells[-1].get_text().strip()
                        top_buy = f"{broker_name}: {volume}"
                    elif 'sell' in text or 'jual' in text:
                        # Parse broker sell
                        broker_name = cells[0].get_text().strip()
                        volume = cells[-1].get_text().strip()
                        top_sell = f"{broker_name}: {volume}"
        
        return {
            'top_buy': top_buy,
            'top_sell': top_sell,
            'status': 'success'
        }
        
    except Exception as e:
        return {'top_buy': '-', 'top_sell': '-', 'status': f'error: {str(e)}'}


def get_market_data(ticker):
    """
    Mengambil semua data pasar untuk ticker tertentu.
    Menggabungkan Net Foreign Flow dan Top Broker.
    
    Args:
        ticker (str): Kode ticker (contoh: ANTM, tanpa .JK)
    
    Returns:
        dict: {'net_foreign': str, 'top_buy': str, 'top_sell': str}
    """
    result = {
        'Net Foreign': '-',
        'Top Buy': '-',
        'Top Sell': '-'
    }
    
    try:
        # Ambil foreign flow
        foreign_data = get_foreign_flow_indopremier(ticker)
        if foreign_data['status'] == 'success':
            net_val = foreign_data['net_foreign']
            if net_val > 0:
                result['Net Foreign'] = f"+{net_val:.2f}B"
            elif net_val < 0:
                result['Net Foreign'] = f"{net_val:.2f}B"
            else:
                result['Net Foreign'] = "0.00B"
        
        # Ambil top broker
        broker_data = get_top_broker_indopremier(ticker)
        if broker_data['status'] == 'success':
            result['Top Buy'] = broker_data['top_buy']
            result['Top Sell'] = broker_data['top_sell']
        
        # Small delay untuk menghindari rate limiting
        time.sleep(0.5)
        
    except Exception:
        pass
    
    return result


def get_market_data_simple(ticker):
    """
    Versi sederhana untuk testing - mengembalikan placeholder data.
    Gunakan ini untuk testing tanpa web scraping.
    
    Args:
        ticker (str): Kode ticker
    
    Returns:
        dict: {'Net Foreign': str, 'Top Buy': str, 'Top Sell': str}
    """
    # Return placeholder untuk testing
    return {
        'Net Foreign': '-',
        'Top Buy': '-',
        'Top Sell': '-'
    }


# ==========================================
# SIMULATED DATA UNTUK DEMO/TESTING
# ==========================================

import random

def get_market_data_simulated(ticker):
    """
    Mengembalikan data simulasi untuk demo/testing.
    Data ini bukan data real, hanya untuk menunjukkan format.
    
    Args:
        ticker (str): Kode ticker
    
    Returns:
        dict: {'Net Foreign': str, 'Top Buy': str, 'Top Sell': str}
    """
    brokers = ['CGS-CIMB', 'Mandiri', 'BNI', 'BCA', 'UOB', 'Credit Suisse', 
               'JP Morgan', 'Morgan Stanley', 'Goldman Sachs', 'Deutsche Bank',
               'CLSA', 'Macquarie', 'Jefferies', 'HSBC', 'Citigroup']
    
    # Simulasi Net Foreign (-5B sampai +5B)
    net_foreign = round(random.uniform(-5, 5), 2)
    if net_foreign >= 0:
        net_foreign_str = f"+{net_foreign:.2f}B"
    else:
        net_foreign_str = f"{net_foreign:.2f}B"
    
    # Simulasi Top Broker
    buy_broker = random.choice(brokers)
    sell_broker = random.choice([b for b in brokers if b != buy_broker])
    buy_volume = random.randint(100, 10000)  # dalam K lot
    sell_volume = random.randint(100, 10000)
    
    return {
        'Net Foreign': net_foreign_str,
        'Top Buy': f"{buy_broker}: {buy_volume}K lot",
        'Top Sell': f"{sell_broker}: {sell_volume}K lot"
    }
