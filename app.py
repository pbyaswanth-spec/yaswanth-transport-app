import streamlit as st
import random
import datetime
import io
import qrcode

st.set_page_config(page_title="Yaswanth Transport App", page_icon="🚌", layout="centered")

# --- INITIALIZE STATE ---
if "users_db" not in st.session_state:
    st.session_state.users_db = {"passenger": "pass123", "yaswanth": "admin123"}
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"

# Booking workflow state
if "step" not in st.session_state:
    st.session_state.step = "SEARCH"  # SEARCH -> BUS_LIST -> SEAT_SELECTION -> PASSENGER_DETAILS -> PAYMENT -> CONFIRMED
if "search_data" not in st.session_state:
    st.session_state.search_data = {}
if "selected_bus" not in st.session_state:
    st.session_state.selected_bus = None
if "selected_seat" not in st.session_state:
    st.session_state.selected_seat = None
if "passenger_info" not in st.session_state:
    st.session_state.passenger_info = {}
if "booking_id" not in st.session_state:
    st.session_state.booking_id = None

# Mock Bus Inventory
MOCK_BUSES = [
    {"id": "B101", "name": "Orange Travels (AC Sleeper 2+1)", "dept": "21:00", "arr": "06:30", "duration": "9h 30m", "fare": 650, "seats": ["L1", "L2", "L3", "L4", "U1", "U2", "U3", "U4"]},
    {"id": "B102", "name": "Kaveri Travels (Bharat Benz AC Semi-Sleeper)", "dept": "22:15", "arr": "07:00", "duration": "8h 45m", "fare": 550, "seats": ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]},
    {"id": "B103", "name": "VRL Multi-Axle Volvo (2+2)", "dept": "23:00", "arr": "08:00", "duration": "9h 00m", "fare": 750, "seats": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]},
]

CITIES = ["Hyderabad", "Bengaluru", "Chennai", "Vijayawada", "Visakhapatnam", "Tirupati", "Pune"]

# --- AUTHENTICATION (LOGIN & REGISTRATION) ---
if not st.session_state.authenticated:
    st.title("🚌 Yaswanth Transport App")
    tab_login, tab_register = st.tabs(["Log In", "Register New Account"])

    # 1. Login Tab
    with tab_login:
        st.subheader("Login to your account")
        with st.form("login_form"):
            l_user = st.text_input("Username / Mobile")
            l_pass = st.text_input("Password", type="password")
            btn_login = st.form_submit_button("Log In", use_container_width=True)

            if btn_login:
                if l_user in st.session_state.users_db and st.session_state.users_db[l_user] == l_pass:
                    st.session_state.authenticated = True
                    st.session_state.username = l_user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please register if you don't have an account.")

    # 2. Registration Tab
    with tab_register:
        st.subheader("Create a new account")
        with st.form("reg_form"):
            r_user = st.text_input("Choose Username / 10-Digit Mobile")
            r_pass = st.text_input("Set Password", type="password")
            r_pass_conf = st.text_input("Confirm Password", type="password")
            btn_reg = st.form_submit_button("Register", use_container_width=True)

            if btn_reg:
                if not r_user or not r_pass:
                    st.error("All fields are required.")
                elif r_pass != r_pass_conf:
                    st.error("Passwords do not match.")
                elif r_user in st.session_state.users_db:
                    st.error("User already exists. Please log in.")
                else:
                    st.session_state.users_db[r_user] = r_pass
                    st.session_state.authenticated = True
                    st.session_state.username = r_user
                    st.success("Account created successfully!")
                    st.rerun()

# --- MAIN BOOKING FLOW ---
else:
    # Top Bar
    c_user, c_logout = st.columns([3, 1])
    c_user.caption(f"👤 Logged in as: **{st.session_state.username}**")
    if c_logout.button("Log out"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    # STEP 1: ROUTE & DATE SEARCH
    if st.session_state.step == "SEARCH":
        st.subheader("🔍 Search Buses")
        c1, c2 = st.columns(2)
        with c1:
            origin = st.selectbox("From City", CITIES, index=0)
        with c2:
            dest_options = [c for c in CITIES if c != origin]
            dest = st.selectbox("To City", dest_options, index=0)

        travel_date = st.date_input("Travel Date", min_value=datetime.date.today(), value=datetime.date.today())

        if st.button("Search Available Buses", type="primary", use_container_width=True):
            st.session_state.search_data = {
                "from": origin,
                "to": dest,
                "date": str(travel_date)
            }
            st.session_state.step = "BUS_LIST"
            st.rerun()

    # STEP 2: BUS SELECTION
    elif st.session_state.step == "BUS_LIST":
        st.subheader(f"🚍 {st.session_state.search_data['from']} ➔ {st.session_state.search_data['to']}")
        st.caption(f"Travel Date: {st.session_state.search_data['date']}")

        if st.button("← Modify Search"):
            st.session_state.step = "SEARCH"
            st.rerun()

        st.write("---")
        for bus in MOCK_BUSES:
            with st.container(border=True):
                col_info, col_fare, col_act = st.columns([3, 1, 1])
                with col_info:
                    st.markdown(f"**{bus['name']}**")
                    st.caption(f"🕒 {bus['dept']} ➔ {bus['arr']} ({bus['duration']})")
                with col_fare:
                    st.markdown(f"### ₹{bus['fare']}")
                with col_act:
                    if st.button(f"Select", key=f"btn_{bus['id']}", use_container_width=True):
                        st.session_state.selected_bus = bus
                        st.session_state.step = "SEAT_SELECTION"
                        st.rerun()

    # STEP 3: SEAT SELECTION
    elif st.session_state.step == "SEAT_SELECTION":
        bus = st.session_state.selected_bus
        st.subheader("💺 Select Your Seat")
        st.caption(f"Bus: **{bus['name']}** | Route: **{st.session_state.search_data['from']} ➔ {st.session_state.search_data['to']}**")

        if st.button("← Back to Buses"):
            st.session_state.step = "BUS_LIST"
            st.rerun()

        st.write("Choose an available seat:")
        selected_seat = st.radio(
            "Seat Grid",
            options=bus["seats"],
            horizontal=True,
            help="Select one seat"
        )

        with st.container(border=True):
            st.write(f"Selected Seat: **{selected_seat}**")
            st.write(f"Fare: **₹{bus['fare']}**")

        if st.button("Proceed to Passenger Details →", type="primary", use_container_width=True):
            st.session_state.selected_seat = selected_seat
            st.session_state.step = "PASSENGER_DETAILS"
            st.rerun()

    # STEP 4: PASSENGER DETAILS
    elif st.session_state.step == "PASSENGER_DETAILS":
        st.subheader("📋 Enter Passenger Details")
        st.caption(f"Seat **{st.session_state.selected_seat}** | Fare: **₹{st.session_state.selected_bus['fare']}**")

        if st.button("← Back to Seat Selection"):
            st.session_state.step = "SEAT_SELECTION"
            st.rerun()

        with st.form("passenger_form"):
            p_name = st.text_input("Full Name", placeholder="e.g. Yaswanth Kumar")
            c_age, c_gender = st.columns(2)
            with c_age:
                p_age = st.number_input("Age", min_value=1, max_value=120, value=25)
            with c_gender:
                p_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            p_phone = st.text_input("Contact Mobile", value=st.session_state.username if st.session_state.username.isdigit() and len(st.session_state.username) == 10 else "", max_chars=10, placeholder="10-digit mobile number")

            btn_submit_pass = st.form_submit_button("Proceed to Payment →", use_container_width=True)

            if btn_submit_pass:
                if not p_name.strip():
                    st.error("Please enter passenger name.")
                elif not p_phone.isdigit() or len(p_phone) != 10:
                    st.error("Please enter a valid 10-digit contact mobile number.")
                else:
                    st.session_state.passenger_info = {
                        "name": p_name,
                        "age": p_age,
                        "gender": p_gender,
                        "phone": p_phone
                    }
                    st.session_state.step = "PAYMENT"
                    st.rerun()

    # STEP 5: PAYMENT REDIRECT (PhonePe UPI)
    elif st.session_state.step == "PAYMENT":
        bus = st.session_state.selected_bus
        p_info = st.session_state.passenger_info
        amount = bus["fare"]

        st.subheader("💳 Complete Payment")
        with st.container(border=True):
            st.markdown("#### Booking Overview")
            st.write(f"🚍 **Bus:** {bus['name']}")
            st.write(f"📍 **Route:** {st.session_state.search_data['from']} ➔ {st.session_state.search_data['to']} ({st.session_state.search_data['date']})")
            st.write(f"💺 **Seat:** {st.session_state.selected_seat}")
            st.write(f"👤 **Passenger:** {p_info['name']} ({p_info['gender']}, {p_info['age']} yrs)")
            st.markdown(f"### Total Fare: ₹{amount}")

        # UPI Intent Link formatting
        phonepe_upi_url = (
            f"upi://pay?pa=merchantvpa@ybl"
            f"&pn=YaswanthTransport"
            f"&am={amount}.00"
            f"&cu=INR"
            f"&tn=BusTicket-{st.session_state.selected_seat}"
        )

        st.warning("⚠️ Ticket reservation is held in PENDING state. Authorize payment on PhonePe to confirm.")

        # Intent Button (Direct switch into PhonePe on mobile)
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
                    margin-top: 10px;
                    margin-bottom: 12px;">
                    Pay ₹{amount} via PhonePe App
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

        # Fallback QR Code for Desktop users
        with st.expander("Show UPI QR Code (For Desktop / Scan & Pay)"):
            qr = qrcode.make(phonepe_upi_url)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            st.image(buf.getvalue(), caption="Scan using PhonePe or any UPI app", width=220)

        st.caption("Development testing bypass:")
        if st.button("Simulate Payment Success"):
            st.session_state.booking_id = f"YWT-{random.randint(100000, 999999)}"
            st.session_state.step = "CONFIRMED"
            st.rerun()

    # STEP 6: CONFIRMATION RECEIPT
    elif st.session_state.step == "CONFIRMED":
        st.balloons()
        st.success("🎉 Booking Confirmed! Payment received successfully.")
        
        with st.container(border=True):
            st.markdown(f"### Ticket ID: `{st.session_state.booking_id}`")
            st.write(f"🚍 **Bus:** {st.session_state.selected_bus['name']}")
            st.write(f"📍 **Route:** {st.session_state.search_data['from']} ➔ {st.session_state.search_data['to']}")
            st.write(f"📅 **Date:** {st.session_state.search_data['date']} at {st.session_state.selected_bus['dept']}")
            st.write(f"💺 **Seat:** {st.session_state.selected_seat}")
            st.write(f"👤 **Passenger:** {st.session_state.passenger_info['name']} ({st.session_state.passenger_info['gender']}, {st.session_state.passenger_info['age']})")
            st.write(f"📞 **Phone:** +91 {st.session_state.passenger_info['phone']}")
            st.write(f"💰 **Amount Paid:** ₹{st.session_state.selected_bus['fare']}")

        if st.button("Book Another Journey", type="primary", use_container_width=True):
            st.session_state.step = "SEARCH"
            st.session_state.selected_bus = None
            st.session_state.selected_seat = None
            st.session_state.passenger_info = {}
            st.session_state.booking_id = None
            st.rerun()
