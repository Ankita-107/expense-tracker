import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# File storage and structure setup
CSV_FILE = "expenses.csv"
COLUMNS = ["Date", "Category", "Amount", "UserKey"]

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Ensure the required columns exist
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    else:
        return pd.DataFrame(columns=COLUMNS)

# Initial dataset load
df = load_data()

# --- SIDEBAR: USER AUTHENTICATION & INPUTS ---
st.sidebar.header("🔑 User Access")
user_key = st.sidebar.text_input(
    "Enter Unique Secret Code:", 
    type="password", 
    help="Type your custom key to unlock and filter your private data dashboard."
)

st.sidebar.markdown("---")
st.sidebar.header("💸 Add New Expense")

# Dynamic form fields
user_date_input = st.sidebar.date_input("Date")
category = st.sidebar.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Others"])
amount = st.sidebar.number_input("Amount (INR)", min_value=1.0, step=10.0)

if st.sidebar.button("Add Expense"):
    if user_key.strip() == "":
        st.sidebar.error("⚠️ Please enter a Secret Code first before saving any expense data!")
    else:
        # Create dictionary for the data row
        new_data = {
            "Date": str(user_date_input),
            "Category": category,
            "Amount": amount,
            "UserKey": user_key.strip()
        }
        new_df = pd.DataFrame([new_data])
        
        # Append data to shared dataset spreadsheet 
        if not os.path.exists(CSV_FILE):
            new_df.to_csv(CSV_FILE, index=False)
        else:
            new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)
            
        st.sidebar.success("🎉 Expense tracked successfully!")
        st.rerun()

# --- MAIN DASHBOARD INTERFACE ---
st.title("📊 Personal Expense Dashboard")

if user_key.strip() == "":
    st.info("👋 Welcome! Please enter your **Unique Secret Code** in the sidebar on the left panel to display your private dashboard.")
else:
    # Strict key matching row filtering layout layer
    df_filtered = df[df["UserKey"] == user_key.strip()] if not df.empty else pd.DataFrame(columns=COLUMNS)
    
    # Grid column workspace setup
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Transaction History")
        if df_filtered.empty:
            st.info("No records found yet for this code. Use the sidebar input form to log your first data entry!")
        else:
            # Sort data by latest transaction first
            df_display = df_filtered.copy()
            df_display = df_display.sort_values(by="Date", ascending=False)
            
            # Show standard raw parameters to user
            st.dataframe(df_display[["Date", "Category", "Amount"]], use_container_width=True)
            
            # Streamlit client explicit safe dataset download pipeline
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
            total_spent = df_filtered["Amount"].sum()
            st.metric(label="Total Money Spent", value=f"₹ {total_spent:,.2f}")
            
            # Responsive data visualization chart processing logic
            chart_data = df_filtered.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(chart_data, values="Amount", names="Category", hole=0.4, title="Category-wise Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Graphs will render here automatically once an entry is added to this secret key profile.")
