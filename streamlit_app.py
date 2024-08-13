eimport datetime
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

# Initialize an empty DataFrame if not already in session state.
if "df" not in st.session_state:
    columns = ["ID", "Salesperson", "Quantity and Product", "Requested Delivery Date", "Date Submitted"]
    st.session_state.df = pd.DataFrame(columns=columns)

# Show a section to add a new special order.
st.header("Add a Special Order")

with st.form("add_order_form"):
    salesperson = st.selectbox("Salesperson", ["Ezio", "Kris", "Greg", "Barry", "Hillary", "Ross", "Diana", "Eren", "Mike", "Alex"])
    product = st.text_input("Quantity and Product Description")
    delivery = st.date_input("Requested Delivery Date")
    submitted = st.form_submit_button("Submit Order")

if submitted:
    recent_order_number = 1 if st.session_state.df.empty else int(max(st.session_state.df.ID).split("-")[1]) + 1
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"ORDER-{recent_order_number}",
                "Salesperson": salesperson,
                "Product": product,
                "Requested Delivery Date": delivery,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Order submitted! Here are the order details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    
    # Append the new entry to the session state DataFrame
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing orders in a table.
st.header("Existing Special Orders")
if st.session_state.df.empty:
    st.write("No special orders have been submitted yet.")
else:
    st.write(f"Number of orders: `{len(st.session_state.df)}`")

    st.info(
        "You can edit the orders by double-clicking on a cell. Note how the plots below "
        "update automatically! You can also sort the table by clicking on the column headers.",
        icon="✍️",
    )

    # Show the orders dataframe with `st.data_editor`.
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
        disabled=["ID", "Date Submitted", "Salesperson", "Product", "PO#", "ETA"],
    )

# Show some metrics and charts about the orders, only if there is data.
if not st.session_state.df.empty:
    st.header("Statistics")

    col1, col2, col3 = st.columns(3)
    num_open_orders = len(st.session_state.df[st.session_state.df.Status == "Open"])
    col1.metric(label="Number of open orders", value=num_open_orders)
    col2.metric(label="Pending Sales Confirmations", value=len(st.session_state.df[st.session_state.df["Sales Confirmation"] == "Pending"]))
    col3.metric(label="Orders Closed", value=len(st.session_state.df[st.session_state.df.Status == "Closed"]))

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

