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
                "Quantity and Product": product,
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

    # Send an email notification to the buyer
def send_email_notification(order_details):
    sender_email = "kevin@bondiproduce.com"
    receiver_email = "kevinakachi@gmail.com"
    password = "K3vin@7799"

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
        # Connect to the Office 365 SMTP server using starttls
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        st.success("Email notification sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")

# Example usage with the order details
order_details = {
    "ID": "ORDER-123",
    "Salesperson": "Ezio",
    "Quantity and Product": "5 cases of apples",
    "Requested Delivery Date": "2024-08-13",
    "Date Submitted": "2024-08-13"
}

# Send email notification
send_email_notification(order_details)
