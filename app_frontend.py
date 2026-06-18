import streamlit as st
import sqlite3
import os

# 設定網頁標題與小圖示
st.set_page_config(page_title="我的專屬選股儀表板", page_icon="📈", layout="wide")

st.title("📈 我的行動選股 App 測試儀表板")
st.subheader("用純 Python 打造的手機/網頁雙用選股介面")

# 📡 雲端優化核心：直接讀取與網頁躺在一起的 stock_brain.db
def get_db_data(mode="all"):
    # 自動尋找資料庫路徑
    db_path = "stock_brain.db"
    
    if not os.path.exists(db_path):
        return {"error": f"找不到資料庫檔案 {db_path}，請確保檔案有成功上傳到 GitHub！"}
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 抓取最新一天的日期
        cursor.execute("SELECT MAX(trade_date) FROM daily_prices")
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            return {"error": "資料庫內目前沒有任何股票數據！"}
            
        if mode == "all":
            # 模式 A：抓取全部股票
            cursor.execute("""
                SELECT stock_id as '股票代碼', stock_name as '股票名稱', 
                       close_price as '目前現價', ma5 as '5MA', ma60 as '季線(60MA)'
                FROM daily_prices WHERE trade_date = ?
            """, (latest_date,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            data_list = [dict(zip(columns, row)) for row in rows]
            return {"count": len(data_list), "data": data_list, "date": latest_date}
            
        elif mode == "warning":
            # 模式 B：抓取跌破季線的股票
            cursor.execute("""
                SELECT stock_id as '股票代碼', stock_name as '股票名稱', 
                       close_price as '目前現價', ma5 as '5MA', ma60 as '季線(60MA)'
                FROM daily_prices 
                WHERE trade_date = ? AND close_price < ma60
            """, (latest_date,))
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            data_list = [dict(zip(columns, row)) for row in rows]
            return {"warning_count": len(data_list), "data": data_list, "date": latest_date}
            
        conn.close()
    except Exception as e:
        return {"error": f"資料庫讀取失敗: {e}"}

# 🎛️ 前端介面：設計按鈕與功能切換
option = st.sidebar.selectbox(
    '🎯 請選擇功能模組',
    ('🌐 首頁歡迎狀態', '📋 查看大腦完整股池', '🚨 跌破季線警示選股')
)

if option == '🌐 首頁歡迎狀態':
    st.info("💡 說明：歡迎來到雲端運作狀態頁面。")
    st.success("🍏 系統提示：您的選股 App 已經完全擺脫電腦黑畫面，成功在雲端伺服器上線！")
    
elif option == '📋 查看大腦完整股池':
    st.success("💡 說明：目前存在雲端大腦資料庫裡的所有股票數據。")
    res_data = get_db_data(mode="all")
    
    if "error" in res_data:
        st.error(res_data["error"])
    else:
        st.write(f"📅 資料更新日期：{res_data['date']}")
        st.metric(label="📊 觀察個股總數", value=f"{res_data['count']} 檔")
        st.dataframe(res_data["data"], use_container_width=True)

elif option == '🚨 跌破季線警示選股':
    st.warning("💡 說明：App 選股引擎自動運算，單獨篩選出【目前現價 < 季線】的弱勢標的！")
    res_data = get_db_data(mode="warning")
    
    if "error" in res_data:
        st.error(res_data["error"])
    else:
        st.write(f"📅 資料更新日期：{res_data['date']}")
        st.metric(label="🔴 跌破季線警告股數", value=f"{res_data['warning_count']} 檔")
        
        if res_data['warning_count'] == 0:
            st.balloons()
            st.write("🟢 完美！目前沒有任何股票跌破季線，全數站在安全線上。")
        else:
            st.dataframe(res_data["data"], use_container_width=True)