from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Yashwanth Kumar Transport Agency",
    page_icon="🚌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styling for Transport Portal
st.markdown(
    """
<style>
    .agency-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 20px;
    }
    .agency-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .agency-header p { margin: 5px 0 0 0; font-size: 0.9rem; color: #e0e0e0; }
    
    .bus-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .seat-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "user_phone" not in st.session_state:
  st.session_state.user_phone = ""
if "bookings" not in st.session_state:
  st.session_state.bookings = []
if "step" not in st.session_state:
  st.session_state.step = "search"  # search, select_bus, checkout, success

# --- COMPREHENSIVE CITIES DATABASE (Tier 1, 2, 3) ---
CITIES = {
    "Tier 1": [
        "Kolkata",
        "Hyderabad",
        "Bengaluru",
        "Chennai",
        "Mumbai",
        "Delhi",
        "Pune",
        "Ahmedabad",
    ],
    "Tier 2": [
        "Vijayawada",
        "Visakhapatnam",
        "Coimbatore",
        "Jaipur",
        "Lucknow",
        "Patna",
        "Bhubaneswar",
        "Indore",
        "Nagpur",
    ],
    "Tier 3": [
        "Tirupati",
        "Warangal",
        "Nellore",
        "Rajahmundry",
        "Kakinada",
        "Guntur",
        "Kurnool",
        "Siliguri",
        "Durgapur",
        "Asansol",
        "Vellore",
        "Madurai",
        "Salem",
    ],
}

ALL_CITIES = sorted(
    CITIES["Tier 1"] + CITIES["Tier 2"] + CITIES["Tier 3"]
)

# --- HEADER ---
st.markdown(
    """
<div class="agency-header">
    <h1>🚌 YASHWANTH KUMAR Transport Agency</h1>
    <p>Connecting Tier 1, Tier 2 & Tier 3 Cities Across India Safely</p>
</div>
""",
    unsafe_allow_html=True,
)

# --- USER AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
  st.subheader("🔐 User Login / Sign Up")
  st.caption(
      "Enter your mobile number to access ticket booking & booking history."
  )

  with st.form("login_form"):
    phone = st.text_input(
        "Mobile Number", placeholder="10-digit mobile number"
    )
    name = st.text_input("Full Name", placeholder="Enter your name")
    submitted = st.form_submit_button("Proceed to Bookings")

    if submitted:
      if len(phone) == 10 and name.strip():
        st.session_state.logged_in = True
        st.session_state.user_phone = phone
        st.session_state.user_name = name
        st.rerun()
      else:
        st.error(
            "Please enter a valid 10-digit mobile number and your name."
        )
  st.stop()

# --- LOGGED IN USER NAV & PROFILE ---
col_u1, col_u2 = st.columns([3, 1])
col_u1.write(f"👤 Welcome, **{st.session_state.user_name}**")
if col_u2.button("Logout"):
  st.session_state.logged_in = False
  st.rerun()

st.markdown("---")

# --- STEP 1: ROUTE SEARCH ---
if st.session_state.step == "search":
  st.subheader("🔍 Search Bus Routes")

  from_city = st.selectbox("From (Departure City)", ALL_CITIES, index=0)
  to_city = st.selectbox(
      "To (Destination City)",
      ALL_CITIES,
      index=ALL_CITIES.index("Vijayawada")
      if "Vijayawada" in ALL_CITIES
      else 1,
  )
  travel_date = st.date_input(
      "Date of Journey", min_value=datetime.today().date()
  )

  if st.button("Find Buses", type="primary", use_container_width=True):
    if from_city == to_city:
      st.error("Departure and destination cities cannot be the same.")
    else:
      st.session_state.search_params = {
          "from": from_city,
          "to": to_city,
          "date": travel_date.strftime("%d %b %Y"),
      }
      st.session_state.step = "select_bus"
      st.rerun()

  # View past bookings section
  if st.session_state.bookings:
    st.markdown("---")
    st.subheader("🎫 Your Booked Tickets")
    for b in st.session_state.bookings:
      st.info(
          f"**{b['from']} ➔ {b['to']}** | Date: {b['date']} | Seats:"
          f" {', '.join(b['seats'])} | Bus: {b['bus_name']} | PNR:"
          f" {b['pnr']}"
      )

# --- STEP 2: SELECT BUS & SEATS ---
elif st.session_state.step == "select_bus":
  params = st.session_state.search_params
  if st.button("⬅ Back to Search"):
    st.session_state.step = "search"
    st.rerun()

  st.markdown(
      f"### Available Buses: {params['from']} ➔ {params['to']}"
  )
  st.caption(f"Journey Date: {params['date']}")

  # Mock available bus fleet
  buses = [
      {
          "id": 1,
          "name": "Yashwanth Luxury A/C Sleeper",
          "type": "2x1 A/C Sleeper",
          "dep": "21:00",
          "arr": "06:00",
          "fare": 1250,
          "seats_left": 14,
      },
      {
          "id": 2,
          "name": "Yashwanth Express Semi-Sleeper",
          "type": "2x2 Non-AC Seater",
          "dep": "22:30",
          "arr": "07:30",
          "fare": 650,
          "seats_left": 22,
      },
      {
          "id": 3,
          "name": "Royal Volvo Multi-Axle A/C",
          "type": "Volvo A/C Scania",
          "dep": "23:00",
          "arr": "05:30",
          "fare": 1600,
          "seats_left": 8,
      },
  ]

  selected_bus = None
  for bus in buses:
    st.markdown(
        f"""
        <div class="bus-card">
            <h4>{bus['name']}</h4>
            <p><b>Type:</b> {bus['type']} | <b>Timing:</b> {bus['dep']} ➔ {bus['arr']}</p>
            <p><b>Fare:</b> ₹{bus['fare']} &nbsp;&nbsp;|&nbsp;&nbsp; <span class="seat-badge">{bus['seats_left']} Seats Available</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(f"Book Seats on {bus['name']}", key=f"bus_{bus['id']}"):
      st.session_state.selected_bus = bus
      st.session_state.step = "checkout"
      st.rerun()

# --- STEP 3: PASSENGER DETAILS & CHECKOUT ---
elif st.session_state.step == "checkout":
  bus = st.session_state.selected_bus
  params = st.session_state.search_params

  if st.button("⬅ Back to Bus List"):
    st.session_state.step = "select_bus"
    st.rerun()

  st.subheader(f"Confirm Booking: {bus['name']}")

  with st.form("checkout_form"):
    st.write(
        f"**Route:** {params['from']} to {params['to']} on {params['date']}"
    )
    passengers = st.text_area(
        "Passenger Name(s)", placeholder="Enter names separated by comma"
    )
    selected_seats = st.multiselect(
        "Select Seat Numbers",
        [f"S{i}" for i in range(1, 25)],
        default=["S1"],
    )

    total_amount = len(selected_seats) * bus["fare"]
    st.markdown(f"### Total Payable Amount: **₹{total_amount}**")

    pay_submitted = st.form_submit_button(
        "Proceed to Secure Payment", type="primary"
    )

    if pay_submitted:
      if not passengers.strip() or not selected_seats:
        st.error("Please provide passenger names and select at least one seat.")
      else:
        pnr = f"YKA{datetime.now().strftime('%H%M%S')}"
        booking_record = {
            "pnr": pnr,
            "bus_name": bus["name"],
            "from": params["from"],
            "to": params["to"],
            "date": params["date"],
            "passengers": passengers,
            "seats": selected_seats,
            "amount": total_amount,
        }
        st.session_state.bookings.append(booking_record)
        st.session_state.last_booking = booking_record
        st.session_state.step = "success"
        st.rerun()

# --- STEP 4: SUCCESS TICKET RECEIPT ---
elif st.session_state.step == "success":
  b = st.session_state.last_booking
  st.success("🎉 Ticket Booked Successfully!")

  st.markdown(
      f"""
  <div style="background-color: #f8f9fa; padding: 20px; border-radius: 12px; border: 2px dashed #2a5298;">
      <h3>🎟 Yashwanth Kumar Transport E-Ticket</h3>
      <hr>
      <p><b>PNR Number:</b> {b['pnr']}</p>
      <p><b>Passenger(s):</b> {b['passengers']}</p>
      <p><b>Route:</b> {b['from']} ➔ {b['to']}</p>
      <p><b>Date:</b> {b['date']} | <b>Bus:</b> {b['bus_name']}</p>
      <p><b>Seats:</b> {', '.join(b['seats'])}</p>
      <p><b>Total Paid:</b> ₹{b['amount']} (Paid Online)</p>
  </div>
  """,
      unsafe_allow_html=True,
  )

  if st.button("Book Another Ticket", type="primary", use_container_width=True):
    st.session_state.step = "search"
    st.rerun()
