import os
import sqlite3
from fastapi import FastAPI

# 初始化 FastAPI 網頁應用程式
app = FastAPI(title="我的專屬選股 App 後端 API")

DB_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "stock_brain.db")

@app.get("/")
def home():
    """App 首頁歡迎畫面"""
    return {
        "status": "online",
        "message": "歡迎來到您的選股 App 後端伺服器！",
        "endpoints": {
            "查看所有股票": "/stocks",
            "查看跌破季線警示股": "/warning-stocks"
        }
    }

@app.get("/stocks")
def get_all_stocks():
    """網址發送 /stocks 時，從大腦撈出所有股票"""
    if not os.path.exists(DB_PATH):
        return {"error": "找不到資料庫檔案"}
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id, stock_name, close_price, ma5, ma60 FROM daily_prices")
    rows = cursor.fetchall()
    conn.close()
    
    # 把撈出來的資料打包成標準的 JSON 格式（這就是手機 App 最喜歡讀的格式）
    result = []
    for r in rows:
        result.append({
            "stock_id": r[0],
            "stock_name": r[1],
            "close_price": r[2],
            "ma5": r[3],
            "ma60": r[4]
        })
    return {"count": len(result), "data": result}

@app.get("/warning-stocks")
def get_warning_stocks():
    """網址發送 /warning-stocks 時，自動篩選跌破季線的股票"""
    if not os.path.exists(DB_PATH):
        return {"error": "找不到資料庫檔案"}
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT stock_id, stock_name, close_price, ma60 FROM daily_prices WHERE close_price < ma60")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "stock_id": r[0],
            "stock_name": r[1],
            "close_price": r[2],
            "ma60": r[3],
            "alert": "🚨 股價已跌破季線！"
        })
    return {"warning_count": len(result), "data": result}

if __name__ == "__main__":
    import uvicorn
    # 啟動網頁伺服器，啟動在 port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)