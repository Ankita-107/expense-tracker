import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="wide")

# --- FILE PATH FOR DATA ---
DATA_FILE = "expenses.csv"

# Function to load data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Create empty dataframe if file doesn't exist
        return pd.DataFrame(columns=["Date", "Category", "Amount (INR)", "Description"])

# Function to save data
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Load existing expenses
df = load_data()

# --- APP HEADER ---
st.title("💰 Personal Expense Tracker")
st.write("A simple dashboard to track and analyze your daily expenses.")
st.markdown("---")

# --- LAYOUT: LEFT SIDEBAR FOR INPUT, RIGHT FOR DASHBOARD ---
col1, col2 = st.columns([1, 2])

# --- 1. EXPENSE ENTRY FORM (LEFT COLUMN) ---
with col1:
    st.header("📍 Add New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.date.today())
        
        # Category placeholder structure
        category = st.selectbox(
            "Category", 
            ["Food & Drinks", "Travel/Commute", "Education/Books", "Entertainment", "Shopping", "Others"],
            index=None,
            placeholder="Choose a category..."
        )
        
        # Amount default value structure
        amount = st.number_input("Amount (INR)", min_value=0.0, value=0.0, step=10.0)
        description = st.text_input("Short Description (Optional)")
        
        submit_btn = st.form_submit_button("Add Expense")
        
        if submit_btn:
            # Check validation rules
            if category is None:
                st.error("Please select a category first!")
            elif amount <= 0.0:
                st.error("Please enter an amount greater than 0!")
            else:
                # Append new row logic
                new_row = {
                    "Date": str(date),
                    "Category": category,
                    "Amount (INR)": amount,
                    "Description": description
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("Expense added successfully!")
                st.rerun()

# --- 2. ANALYTICS & VISUALIZATION (RIGHT COLUMN) ---
with col2:
    st.header("📊 Expense Dashboard")
    
    if df.empty:
        st.info("No expenses recorded yet. Start by adding one in the left panel!")
    else:
        # Quick KPI Metrics
        total_expense = df["Amount (INR)"].sum()
        total_items = len(df)
        
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("Total Money Spent", f"₹ {total_expense:,.2f}")
        metric_col2.metric("Total Transactions", total_items)
        
        st.markdown("---")
        
        # Category-wise Breakdown Chart
        st.subheader("Category-wise Distribution")
        category_sum = df.groupby("Category")["Amount (INR)"].sum().reset_index()
        
        # Interactive Pie Chart using Plotly
        fig = px.pie(category_sum, values="Amount (INR)", names="Category", 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

# --- 3. RAW DATA VIEW (BOTTOM SECTION) ---
st.markdown("---")
st.header("📋 All Transactions")

if not df.empty:
    # Sort by date (newest first)
    df_sorted = df.iloc[::-1]
    st.dataframe(df_sorted, use_container_width=True)
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as Excel/CSV",
        data=csv,
        file_name='my_expenses.csv',
        mime='text/csv',
    )
else:
    st.write("No transaction history available.")
