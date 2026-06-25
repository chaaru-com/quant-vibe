import os
import sqlite3
import json
import sys

def fetch_nifty100_ohlcv(ticker, start_date=None, end_date=None):
    """
    Fetch strict factual historical records from the SQLite database.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "nifty100.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT Date, Open, High, Low, Close, Volume FROM nifty100_ohlcv WHERE Ticker = ?"
    params = [ticker]
    
    if start_date:
        query += " AND Date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND Date <= ?"
        params.append(end_date)
        
    query += " ORDER BY Date ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "Date": r[0].split(" ")[0] if " " in str(r[0]) else str(r[0]),
            "Open": float(r[1]),
            "High": float(r[2]),
            "Low": float(r[3]),
            "Close": float(r[4]),
            "Volume": float(r[5])
        })
    conn.close()
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "fetch":
            ticker = sys.argv[2] if len(sys.argv) > 2 else "NIFTY100"
            res = fetch_nifty100_ohlcv(ticker)
            print(json.dumps(res[:5], indent=2))
        else:
            print(json.dumps({"error": "Unknown command"}))
    else:
        for line in sys.stdin:
            try:
                req = json.loads(line.strip())
                method = req.get("method")
                params = req.get("params", {})
                
                if method == "fetch_nifty100_ohlcv":
                    ticker = params.get("ticker", "NIFTY100")
                    start = params.get("start_date")
                    end = params.get("end_date")
                    data = fetch_nifty100_ohlcv(ticker, start, end)
                    print(json.dumps({"result": data}))
                else:
                    print(json.dumps({"error": "Method not found"}))
            except Exception as e:
                print(json.dumps({"error": str(e)}))
            sys.stdout.flush()
