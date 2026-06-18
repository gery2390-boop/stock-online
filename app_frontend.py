import streamlit as st
import sqlite3
import pandas as pd
import os

# 設定網頁標題與小圖示
st.set_page_config(page_title="富邦籌碼大腦儀表板", page_icon="📈", layout="wide")

st.title("📈 我的行動選股 App 測試儀表板 (富邦籌碼全面升級版)")
st.subheader("用純 Python 打造的手機/網頁雙用選股介面")

# 📡 核心：從 SQLite 讀取資料
def get_latest_date(db_path="stock_brain.db"):
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(trade_date) FROM daily_prices")
        latest_date = cursor.fetchone()[0]
        conn.close()
        return latest_date
    except:
        return None

db_file = "stock_brain.db"
latest_trade_date = get_latest_date(db_file)

# 🎛️ 左側導覽列選單
option = st.sidebar.selectbox(
    '🎯 請選擇功能模組',
    ('🌐 首頁歡迎狀態', '📋 查看大腦完整股池', '🚨 跌破季線警示選股', '🔥 法人土洋雙進爆發股', '🏆 今日法人買超排行榜')
)

if option == '🌐 首頁歡迎狀態':
    st.info("💡 說明：歡迎來到雲端運作狀態頁面。")
    st.success("🍏 系統提示：您的選股 App 運作完美，且已預留「富邦證券籌碼資料庫欄位」！")
    if latest_trade_date:
        st.metric(label="📅 目前大腦資料庫最新觀測日期", value=latest_trade_date)
    else:
        st.error("⚠️ 警告：目前專案目錄下找不到 stock_brain.db，請確認資料庫檔案是否已成功上傳至 GitHub。")
    
elif option == '📋 查看大腦完整股池':
    st.success("💡 說明：目前存在雲端大腦資料庫裡的所有股票數據。")
    if not latest_trade_date:
        st.error("找不到資料庫或無數據！")
    else:
        conn = sqlite3.connect(db_file)
        query = "SELECT stock_id as '股票代碼', stock_name as '股票名稱', close_price as '目前現價', ma5 as '5MA', ma60 as '季線(60MA)' FROM daily_prices WHERE trade_date = ?"
        df = pd.read_sql_query(query, conn, params=(latest_trade_date,))
        conn.close()
        st.metric(label="📊 觀察個股總數", value=f"{len(df)} 檔")
        st.dataframe(df, use_container_width=True)

elif option == '🚨 跌破季線警示選股':
    st.warning("💡 說明：App 選股引擎自動運算，單獨篩選出【目前現價 < 季線】的弱勢標的！")
    if not latest_trade_date:
        st.error("找不到資料庫或無數據！")
    else:
        conn = sqlite3.connect(db_file)
        query = "SELECT stock_id as '股票代碼', stock_name as '股票名稱', close_price as '目前現價', ma5 as '5MA', ma60 as '季線(60MA)' FROM daily_prices WHERE trade_date = ? AND close_price < ma60"
        df = pd.read_sql_query(query, conn, params=(latest_trade_date,))
        conn.close()
        st.metric(label="🔴 跌破季線警告股數", value=f"{len(df)} 檔")
        st.dataframe(df, use_container_width=True)

elif option == '🔥 法人土洋雙進爆發股':
    st.header("🔥 土洋雙進 + 強勢多頭排列選股")
    st.info("💡 策略邏輯：篩選出【外資買超(張) > 0】且【投信買超(張) > 0】且【現價 > 5MA】的籌碼與技術面雙強個股！")
    
    if not latest_trade_date:
        st.error("找不到資料庫或無數據！")
    else:
        try:
            conn = sqlite3.connect(db_file)
            # 利用 SQL 語法在資料庫直接完成籌碼大數據過濾
            query = """
                SELECT stock_id as '股票代碼', stock_name as '股票名稱', 
                       close_price as '目前現價', ma5 as '5MA',
                       foreign_buy_net as '外資買超(張)', investment_trust_buy_net as '投信買超(張)'
                FROM daily_prices 
                WHERE trade_date = ? 
                  AND foreign_buy_net > 0 
                  AND investment_trust_buy_net > 0 
                  AND close_price > ma5
                ORDER BY investment_trust_buy_net DESC
            """
            df_strategy = pd.read_sql_query(query, conn, params=(latest_trade_date,))
            conn.close()
            
            if df_strategy.empty:
                st.info("ℹ️ 提示：目前資料庫中暫無法人籌碼數據，或今日無符合「土洋雙進」的股票。（等本機富邦腳本跑完寫入後，這裡就會自動浮現列表囉！）")
            else:
                st.metric(label="📈 精選籌碼爆發股數", value=f"{len(df_strategy)} 檔")
                st.dataframe(df_strategy, use_container_width=True)
        except Exception as e:
            st.error(f"資料庫讀取失敗，可能是籌碼欄位尚未建立：{e}")

elif option == '🏆 今日法人買超排行榜':
    st.header("🏆 今日全市場三大法人合計買超 Top 10")
    st.info("💡 策略邏輯：不看技術面，單純依據三大法人今日合計買超張數進行由高到低排序，抓出市場主力資金焦點。")
    
    if not latest_trade_date:
        st.error("找不到資料庫或無數據！")
    else:
        try:
            conn = sqlite3.connect(db_file)
            query = """
                SELECT stock_id as '股票代碼', stock_name as '股票名稱', 
                       close_price as '目前現價',
                       foreign_buy_net as '外資買超(張)', 
                       investment_trust_buy_net as '投信買超(張)',
                       institutional_total_buy_net as '三大法人合計買超(張)'
                FROM daily_prices 
                WHERE trade_date = ? AND institutional_total_buy_net > 0
                ORDER BY institutional_total_buy_net DESC
                LIMIT 10
            """
            df_top10 = pd.read_sql_query(query, conn, params=(latest_trade_date,))
            conn.close()
            
            if df_top10.empty:
                st.info("ℹ️ 提示：目前資料庫中暫無合計買超排序數據。（等富邦 API 籌碼對接完成後自動展現）")
            else:
                st.dataframe(df_top10, use_container_width=True)
        except Exception as e:
            st.error(f"資料庫讀取失敗：{e}")
