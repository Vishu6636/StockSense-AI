import pandas as pd
import json
import io
import requests

def get_nifty500():
    try:
        # NSE URL for Nifty 500
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        df = pd.read_csv(io.StringIO(response.text))
        
        tickers = []
        for _, row in df.iterrows():
            tickers.append({
                "ticker": row["Symbol"] + ".NS",
                "name": row["Company Name"],
                "sector": row["Industry"],
                "exchange": "NSE"
            })
        return tickers
    except Exception as e:
        print("Error fetching NIFTY 500", e)
        return []

def get_sp500():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        df = pd.read_html(io.StringIO(response.text))[0]
        # Columns: Symbol, Security, GICS Sector
        tickers = []
        # taking top 300
        for _, row in df.head(300).iterrows():
            tickers.append({
                "ticker": row["Symbol"].replace(".", "-"),
                "name": row["Security"],
                "sector": row["GICS Sector"],
                "exchange": "US"
            })
        return tickers
    except Exception as e:
        print("Error fetching S&P 500", e)
        return []

if __name__ == "__main__":
    nifty = get_nifty500()
    print(f"Got {len(nifty)} India tickers")
    if nifty:
        with open("tickers_india.json", "w") as f:
            json.dump(nifty, f, indent=2)

    sp500 = get_sp500()
    print(f"Got {len(sp500)} US tickers")
    if sp500:
        with open("tickers_us.json", "w") as f:
            json.dump(sp500, f, indent=2)
    print("Done")
