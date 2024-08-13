import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Set page config
st.set_page_config(page_title="Sales Special Orders", page_icon="📦")

# Show app title and description.
st.title("📦 Sales Special Orders")
st.write(
    """
    Please submit your special order request using the form below. Ensure the details are as clear and specific as possible.
    You can create a new special order, edit existing orders, and view statistics.
    """
)

# Create a random Pandas dataframe with existing orders.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Generate the dataframe with 100 rows/orders.
    data = {
        "ID": [f"ORDER-{i}" for i in range(1100, 1000, -1)],
        "Salesperson": np.random.choice(["Kris", "Greg", "Barry", "Hilary", "Mike", "Alex", "Diana", "Ross", "Eren"], size=100),
        "Product": np.random.choice(["Yellow Beans", "Green Beans", "Red Beans"], size=100),
        "Quantity": np.random.randint(1, 10, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "PO#": np.random.randint(10000, 20000, size=100),
        "ETA": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Sales Confirmation": np.random.choice(["Pending", "Confirmed"], size=100),
        "SO#": [None] * 100,
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state
    st.session_state.df = df

# Show a section to add a new special order.
st.header("Add a Special Order")

with st.form("add_order_form"):
    salesperson = st.selectbox("Salesperson", ["John Doe", "Jane Smith", "Mike Lee"])
    product = st.text_input("Product")
    quantity = st.number_input("Quantity", min_value=1)
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    po_number = st.text_input("Purchase Order (PO#)")
    eta = st.date_input("ETA")
    submitted = st.form_submit_button("Submit Order")

if submitted:
    recent_order_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"ORDER-{recent_order_number+1}",
                "Salesperson": salesperson,
                "Product": product,
                "Quantity": quantity,
                "Status": "Open",
                "Priority": priority,
                "PO#": po_number,
                "ETA": eta,
                "Date Submitted": today,
                "Sales Confirmation": "Pending",
                "SO#": None,
            }
        ]
    )

    st.write("Order submitted! Here are the order details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing orders in a table.
st.header("Existing Special Orders")
st.write(f"Number of orders: `{len(st.session_state.df)}`")

st.info(
    "You can edit the orders by double-clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the orders dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Order status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
        "Sales Confirmation": st.column_config.SelectboxColumn(
            "Sales Confirmation",
            help="Sales confirmation status",
            options=["Pending", "Confirmed"],
            required=True,
        ),
    },
    disabled=["ID", "Date Submitted", "Salesperson", "Product", "Quantity", "PO#", "ETA"],
)

# Show some metrics and charts about the orders.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_orders = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open orders", value=num_open_orders)
col2.metric(label="Pending Sales Confirmations", value=len(st.session_state.df[st.session_state.df["Sales Confirmation"] == "Pending"]))
col3.metric(label="Orders Closed", value=len(st.session_state.df[st.session_state.df.Status == "Closed"]))

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Order status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current order priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")

