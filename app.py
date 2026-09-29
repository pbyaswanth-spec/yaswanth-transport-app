import streamlit as st
import random

st.set_page_config(page_title="Yaswanth Transport App", page_icon="🚌", layout="centered")

# Hardcoded test credentials
CREDENTIALS = {
    "passenger": "pass123",
    "yaswanth": "admin123"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "payment_status" not in st.session_state:
    st.session_state.payment_status = "NOT_STARTED"

# --- LOGIN SCREEN ---
if not st.session_state.authenticated:
    st.title("🚌 Transport App - Login")
    st.caption("Enter your username and password to proceed.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Log In")

        if submit_btn:
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

# --- TICKET & PAYMENT SCREEN ---
else:
    st.title("🎫 Ticket Reservation")
    st.write(f"Logged in as: **{st.session_state.username}**")

    with st.container(border=True):
        st.subheader("Selected Journey")
        st.write("🚍 **Route:** Hyderabad ➔ Bengaluru")
        st.write("💺 **Seat:** A1 (AC Sleeper)")
        st.write("💰 **Fare Amount:** ₹450")

    if st.session_state.payment_status == "CONFIRMED":
        st.balloons()
        st.success("🎉 Ticket is CONFIRMED!")
        st.markdown(f"**Ticket ID:** TKT-{random.randint(10000, 99999)}")
        if st.button("Book Another Ticket"):
            st.session_state.payment_status = "NOT_STARTED"
            st.rerun()
    else:
        st.warning("⚠️ Complete payment on PhonePe to confirm.")

        phonepe_upi_url = (
            "upi://pay?pa=merchantvpa@ybl"
            "&pn=YaswanthTransport"
            "&am=450.00"
            "&cu=INR"
            "&tn=BusTicketA1"
        )

        st.markdown(
            f"""
            <a href="{phonepe_upi_url}" target="_blank">
                <button style="
                    width: 100%;
                    background-color: #5f259f;
                    color: white;
                    padding: 14px;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-top: 10px;">
                    Pay ₹450 via PhonePe App
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

        st.caption("Testing simulation:")
        if st.button("Simulate Payment Success"):
            st.session_state.payment_status = "CONFIRMED"
            st.rerun()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
        
