import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page title & layout configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# 📂 File setup and schema initialization
CSV_FILE = "expenses.csv"
COLUMNS = ["Date", "Category", "Amount", "UserKey"]

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Schema ensure korchi jate column mismatch na hoy
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    else:
        return pd.DataFrame(columns=COLUMNS)

# Initial load
df = load_data()

# --- SIDEBAR: USER AUTH & INPUTS ---
st.sidebar.header("🔑 User Access")
# Password type mask input box
user_key = st.sidebar.text_input("Enter your Unique Secret Code:", type="password", help="Type your personal key to see and add your data.")

st.sidebar.markdown("---")
st.sidebar.header("💸 Add New Expense")

# Input fields
user_date_input = st.sidebar.date_input("Date")
category = st.sidebar.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Others"])
amount = st.sidebar.number_input("Amount (INR)", min_value=1.0, step=10.0)

if st.sidebar.button("Add Expense"):
    if user_key.strip() == "":
        st.sidebar.error("⚠️ Age ekta Unique Secret Code likho, tarpor expense save koro!")
    else:
        # Create single row entry dataframe
        new_data = {
            "Date": str(user_date_input),
            "Category": category,
            "Amount": amount,
            "UserKey": user_key.strip()
        }
        new_df = pd.DataFrame([new_data])
        
        # Write mode dynamic setup
        if not os.path.exists(CSV_FILE):
            new_df.to_csv(CSV_FILE, index=False)
        else:
            new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)
            
        st.sidebar.success("🎉 Expense perfectly saved!")
        st.rerun()

# --- MAIN DASHBOARD AREA ---
st.title("📊 Personal Expense Dashboard")

if user_key.strip() == "":
    st.info("👋 Welcome! Ba-dike (Sidebar) giye tomar **Unique Secret Code-ta type koro** jate tomar custom dashboard open hoy.")
else:
    # Filter dataset for specific user
    df_filtered = df[df["UserKey"] == user_key.strip()] if not df.empty else pd.DataFrame(columns=COLUMNS)
    
    # 1. Main visual block
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Transaction Details")
        if df_filtered.empty:
            st.info("Kono record khuje paowa jayni. Sidebar intermediate data form update kore first expense entry koro!")
        else:
            # Sort by date reverse
            df_display = df_filtered.copy()
            df_display = df_display.sort_values(by="Date", ascending=False)
            st.dataframe(df_display[["Date", "Category", "Amount"]], use_container_width=True)
            
            # Download options
            csv_data = df_display[["Date", "Category", "Amount"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download My History (CSV)",
                data=csv_data,
                file_name=f"{user_key}_expenses.csv",
                mime="text/csv"
            )
            
    with col2:
        st.subheader("📈 Visualization Analysis")
        if not df_filtered.empty:
            total_spent = df_filtered["Amount"].sum()
            st.metric(label="Total Money Spent", value=f"₹ {total_spent:,.2f}")
            
            # Pie Chart
            chart_data = df_filtered.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(chart_data, values="Amount", names="Category", hole=0.4, title="Category-wise Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Graph review korar jonno tracking entry blank ache.")
