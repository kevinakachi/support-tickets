import datetime
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page config
st.set_page_config(page_title="Sales Special Orders", page_icon="📦")

# Show app title and description.
st.title("📦 Sales Special Orders")
st.write(
    """
    Please submit your special order request using the form below. Ensure the details are as clear and specific as possible.
    You can create a new special order and edit existing orders.
    """
)

# Initialize an empty DataFrame if not already in session state.
if "df" not in st.session_state:
    columns = ["ID", "Salesperson", "Type", "Quantity and Product", "Requested Delivery Date", "Date Submitted", "SO#"]
    st.session_state.df = pd.DataFrame(columns=columns)

# Show a section to add a new special order.
st.header("Add a Special Order")

with st.form("add_order_form"):
    salesperson = st.selectbox("Salesperson", ["Ezio", "Kris", "Greg", "Barry", "Hillary", "Ross", "Diana", "Eren", "Mike", "Alex"])
    
    # Add the Type dropdown menu
    order_type = st.selectbox("Type", ["One Time", "Keep Inventory"])

    # Conditional input field for SO# if "One Time" is selected
    so_number = None
    if order_type == "One Time":
        so_number = st.text_input("Sales Order (SO#)")
        
    product = st.text_input("Quantity and Product Description")
    delivery = st.date_input("Requested Delivery Date")
    submitted = st.form_submit_button("Submit Order")

if submitted:
    recent_order_number = 1 if st.session_state.df.empty else int(max(st.session_state.df.ID).split("-")[1]) + 1
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"ORDER-{recent_order_number}",
                "Salesperson": salesperson,
                "Type": order_type,
                "Quantity and Product": product,
                "Requested Delivery Date": delivery,
                "Date Submitted": today,
                "SO#": so_number,
            }
        ]
    )

    # Show a success message and display the order details
    st.write("Order submitted! Here are the order details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    
    # Append the new entry to the session state DataFrame
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

    # Send an email notification to the buyer
    def send_email_notification(order_details):
        sender_email = "kevinakachi@gmail.com"
        receiver_email = "kevin.akachi@tikomangos.com"
        password = "your_app_password"

        subject = f"New Special Order: {order_details['ID']}"
        body = f"""
        A new special order has been submitted.

        Salesperson: {order_details['Salesperson']}
        Product: {order_details['Quantity and Product']}
        Requested Delivery Date: {order_details['Requested Delivery Date']}
        Date Submitted: {order_details['Date Submitted']}

        Please proceed with the order.
        """

        # Email setup
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            # Connect to the Gmail SMTP server using starttls
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            st.success("Email notification sent successfully!")
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")

    # Send email notification only after form submission
    send_email_notification(df_new.iloc[0])

# Show section to view and edit existing orders in a table.
st.header("Existing Special Orders")
if st.session_state.df.empty:
    st.write("No special orders have been submitted yet.")
else:
    st.write(f"Number of orders: `{len(st.session_state.df)}`")

    st.info(
        "You can edit the orders by double-clicking on a cell.",
        icon="✍️",
    )

    # Show the orders dataframe with `st.data_editor`.
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        disabled=["ID", "Date Submitted", "Salesperson", "Type", "Quantity and Product", "Requested Delivery Date", "SO#"],
    )

