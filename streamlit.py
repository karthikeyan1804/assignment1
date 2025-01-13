import sqlite3
import pandas as pd
import random
from faker import Faker
import streamlit as st

# Initialize Faker instance
fake = Faker()

# Generate simulated data
def generate_expense_data(month, year, num_records=100):
    data = []
    categories = ["Food", "Transportation", "Bills", "Groceries", "Subscriptions", "Entertainment", "Personal Spending"]
    payment_modes = ["Cash", "Online"]

    for _ in range(num_records):
        data.append({
            "Date": fake.date_between(start_date=f"{year}-{month}-01", end_date=f"{year}-{month}-28"),
            "Category": random.choice(categories),
            "Payment_Mode": random.choice(payment_modes),
            "Description": fake.sentence(nb_words=5),
            "Amount_Paid": round(random.uniform(5, 500), 2),
            "Cashback": round(random.uniform(0, 20), 2)
        })

    return pd.DataFrame(data)

# Create database connection
conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()

# Create a table schema
def create_table(month):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS expenses_{month} (
            Date TEXT,
            Category TEXT,
            Payment_Mode TEXT,
            Description TEXT,
            Amount_Paid REAL,
            Cashback REAL
        )
    """)

# Insert data into table
def insert_data(df, month):
    df.to_sql(f"expenses_{month}", conn, if_exists="replace", index=False)

# Generate and populate tables for 12 months
def generate_and_populate_tables(year):
    for month in range(1, 13):
        create_table(month)
        data = generate_expense_data(month, year)
        insert_data(data, month)

# Run data generation for the current year
generate_and_populate_tables(2023)

# Query database to extract insights
def run_query(query):
    return pd.read_sql_query(query, conn)

# Streamlit App
st.title("Personal Expense Tracker")

# Query Selection
def get_query_insight():
    return {
        "Monthly Expense Breakdown": "SELECT strftime('%m', Date) as Month, SUM(Amount_Paid) as Total_Expenses FROM expenses_1 GROUP BY Month",
        "Top Categories by Spending": "SELECT Category, SUM(Amount_Paid) as Total_Amount FROM expenses_1 GROUP BY Category ORDER BY Total_Amount DESC LIMIT 5",
        "Average Cashback Per Category": "SELECT Category, AVG(Cashback) as Avg_Cashback FROM expenses_1 GROUP BY Category"
    }

queries = get_query_insight()
selected_query = st.selectbox("Choose a Query to Run:", options=queries.keys())

# Run and Display Results
if selected_query:
    query = queries[selected_query]
    result = run_query(query)
    st.write(result)

# Visualization
if st.checkbox("Show Visualizations"):
    if selected_query == "Monthly Expense Breakdown":
        result = run_query(queries[selected_query])
        st.bar_chart(result.set_index("Month")['Total_Expenses'])

    elif selected_query == "Top Categories by Spending":
        result = run_query(queries[selected_query])
        st.bar_chart(result.set_index("Category")['Total_Amount'])

st.write("---")
st.write("**Streamlit app developed for visualizing expense patterns and SQL query insights**")

# Close database connection
conn.close()



