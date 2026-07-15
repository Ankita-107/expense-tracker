import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# 2. Database File Configuration
CSV_FILE = "expenses.csv"
COLUMNS = ["Date", "Category", "Amount", "UserKey"]

# 3. Load Data Helper Function
def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Ensure proper schema column structures
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    else:
        # File na thakle program background system-e automatic create korbe
        return pd.DataFrame(columns=COLUMNS)

# Initial global data load
df = load_data()

# --- SIDEBAR: USER AUTH & INPUT DATA ---
st.sidebar.header("🔑 User Access")
user_key = st.sidebar.text_input(
    "Enter Unique Secret Code:", 
    type="password", 
    help="Enter your unique private key to see and manage your private data."
).strip()

st.sidebar.markdown("---")
st.sidebar.header("💸 Add New Expense")

# Date selector
user_date_input = st.sidebar.date_input("Date")

# Category dropdown (Default is "Select Category")
category = st.sidebar.selectbox(
    "Category", 
    ["Select Category", "Food", "Travel", "Shopping", "Bills", "Entertainment", "Others"]
)

# Amount input box (Default is 0.00)
amount = st.sidebar.number_input("Amount (INR)", min_value=0.00, value=0.00, step=10.0, format="%.2f")

# --- SAVE DATA SYSTEM ON BUTTON CLICK ---
if st.sidebar.button("Add Expense"):
    if user_key == "":
        st.sidebar.error("⚠️ Please enter a Secret Code first before saving any expense data!")
    elif category == "Select Category":
        st.sidebar.error("⚠️ Please select a valid Category!")
    elif amount <= 0:
        st.sidebar.error("⚠️ Amount must be greater than 0.00!")
    else:
        # Preparing the new data block
        new_data = {
            "Date": str(user_date_input),
            "Category": category,
            "Amount": amount,
            "UserKey": user_key
        }
        new_df = pd.DataFrame([new_data])
        
        try:
            # Check if file exists to append or write fresh
            if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
                new_df.to_csv(CSV_FILE, index=False)
            else:
                new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)
                
            st.sidebar.success("🎉 Expense saved successfully!")
            st.rerun() # Immediate visual reload
        except Exception as e:
            st.sidebar.error(f"❌ Storage Error: {str(e)}")

# --- MAIN DASHBOARD WINDOW ---
st.title("📊 Personal Expense Dashboard")

if user_key == "":
    st.info("👋 Welcome! Please enter your **Unique Secret Code** in the sidebar on the left panel to display your private dashboard.")
else:
    # Always read the latest state from CSV to show old data
    df_fresh = load_data()
    
    # Strictly filter records belonging ONLY to the logged-in UserKey
    if not df_fresh.empty:
        df_filtered = df_fresh[df_fresh["UserKey"] == user_key]
    else:
        df_filtered = pd.DataFrame(columns=COLUMNS)
    
    # Two-Column Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Transaction History")
        if df_filtered.empty:
            st.info(f"No records found yet for code '{user_key}'. Use the sidebar input form to log your first data entry!")
        else:
            # Sort with newest date first
            df_display = df_filtered.copy()
            df_display = df_display.sort_values(by="Date", ascending=False)
            
            # Show historical logs (Hiding the UserKey from display)
            st.dataframe(df_display[["Date", "Category", "Amount"]], use_container_width=True)
            
            # Download CSV functionality
            csv_data = df_display[["Date", "Category", "Amount"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download My History (CSV)",
                data=csv_data,
                file_name=f"{user_key}_expenses.csv",
                mime="text/csv"
            )
            
    with col2:
        st.subheader("📈 Financial Breakdown")
        if not df_filtered.empty:
            # Cumulative spent metric calculation
            total_spent = df_filtered["Amount"].sum()
            st.metric(label="Total Money Spent", value=f"₹ {total_spent:,.2f}")
            
            # Interactive Plotly Pie Chart
            chart_data = df_filtered.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(chart_data, values="Amount", names="Category", hole=0.4, title="Category-wise Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Graphs will render here automatically once an entry is added to this secret key profile.")
