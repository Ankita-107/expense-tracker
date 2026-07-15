import streamlit as st
import pandas as pd
import plotly.express as px

# Page layout visualization format configuration setup
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# 🎯 CLOUD BUFFER SYSTEM: Initialize system dynamic table directly in internal browser cloud session memory
if "expenses_db" not in st.session_state:
    st.session_state.expenses_db = pd.DataFrame(columns=["Date", "Category", "Amount", "UserKey"])

# --- SIDEBAR: USER AUTHENTICATION & INPUTS ---
st.sidebar.header("🔑 User Access")
user_key = st.sidebar.text_input(
    "Enter Unique Secret Code:", 
    type="password", 
    help="Type your custom key to unlock and filter your private data dashboard."
).strip()

st.sidebar.markdown("---")
st.sidebar.header("💸 Add New Expense")

# Dynamic form workspace field tracking initialization setup
user_date_input = st.sidebar.date_input("Date")

# Select Category default configuration parameters level select indicator
category = st.sidebar.selectbox(
    "Category", 
    ["Select Category", "Food", "Travel", "Shopping", "Bills", "Entertainment", "Others"]
)

# 0.00 default mapping control text configuration sequence
amount = st.sidebar.number_input("Amount (INR)", min_value=0.00, value=0.00, step=10.0, format="%.2f")

# 🎯 THE CRITICAL DATA SAVE SUBMISSION TRIGGER LAYER FIX:
if st.sidebar.button("Add Expense"):
    if user_key == "":
        st.sidebar.error("⚠️ Please enter a Secret Code first before saving any expense data!")
    elif category == "Select Category":
        st.sidebar.error("⚠️ Please select a valid Category!")
    elif amount <= 0:
        st.sidebar.error("⚠️ Amount must be greater than 0.00!")
    else:
        # Generate single row record mapping block dictionary format
        new_data = {
            "Date": str(user_date_input),
            "Category": category,
            "Amount": amount,
            "UserKey": user_key
        }
        new_df = pd.DataFrame([new_data])
        
        # Directly merge logic data template context target structure parsing update session framework storage block
        st.session_state.expenses_db = pd.concat([st.session_state.expenses_db, new_df], ignore_index=True)
            
        st.sidebar.success("🎉 Expense tracked successfully!")
        
        # Force execution frame standard state reload dynamic parameters display loop context update check
        st.rerun()

# --- MAIN DASHBOARD INTERFACE ---
st.title("📊 Personal Expense Dashboard")

if user_key == "":
    st.info("👋 Welcome! Please enter your **Unique Secret Code** in the sidebar on the left panel to display your private dashboard.")
else:
    # Read core memory structure matrix mapping array setup configuration reference layer
    df_fresh = st.session_state.expenses_db
    
    # Strict key matching data verification row filtering layer (Privacy Isolation Context)
    if not df_fresh.empty:
        df_filtered = df_fresh[df_fresh["UserKey"] == user_key]
    else:
        df_filtered = pd.DataFrame(columns=["Date", "Category", "Amount", "UserKey"])
    
    # Grid workspace column setup interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Transaction History")
        if df_filtered.empty:
            st.info(f"No records found yet for code '{user_key}'. Use the sidebar input form to log your first data entry!")
        else:
            # Sort data array structural loop reverse order logic
            df_display = df_filtered.copy()
            df_display = df_display.sort_values(by="Date", ascending=False)
            
            # Show standard parameters logic fields (UserKey column is hidden safely from view)
            st.dataframe(df_display[["Date", "Category", "Amount"]], use_container_width=True)
            
            # Streamlit dashboard explicit custom spreadsheet CSV download pipeline context parsing
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
            
            # Dynamic Pie Chart rendering algorithm block structure pipeline sequence check data model
            chart_data = df_filtered.groupby("Category")["Amount"].sum().reset_index()
            fig = px.pie(chart_data, values="Amount", names="Category", hole=0.4, title="Category-wise Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Graphs will render here automatically once an entry is added to this secret key profile.")
