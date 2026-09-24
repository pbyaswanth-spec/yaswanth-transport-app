import streamlit as st
import pandas as pd
from datetime import datetime
import math

st.set_page_config(
    page_title="Yashwanth Kumar Transport",
    page_icon="🚍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MODERN STYLING ---
st.markdown("""
<style>
    .agency-hero {
        background: linear-gradient(135deg, #0d2b45 0%, #203c56 100%);
        color: white;
        padding: 22px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 16px;
    }
    .bus-card {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    }
    .seat-box {
        display: inline-block;
        padding: 8px 12px;
        margin: 4px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.85rem;
        text-align: center;
    }
    .seat-avail { background-color: #e8f5e9; border: 1px solid #4caf50; color: #2e7d32; }
    .seat-booked { background-color: #eceff1; border: 1px solid #b0bec5; color: #90a4ae; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "bookings" not in st.session_state:
    st.session_state.bookings = []
if "step" not in st.session_state:
    st.session_state.step = "search"
if "chosen_seats" not in st.session_state:
    st.session_state.chosen_seats = []

# --- CURATED CITY DATABASE & APPROXIMATE DISTANCE ENGINE (KM) ---
CITY_COORDINATES = {
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Vijayawada": (16.5062, 80.6480),
    "Visakhapatnam": (17.6868, 83.2185),
    "Tirupati": (13.6288, 79.4192),
    "Kolkata": (22.5726, 88.3639),
    "Bhubaneswar": (20.2961, 85.8245),
    "Siliguri": (26.7271, 88.3953),
    "Pune": (18.5204, 73.8567),
    "Mumbai": (19.0760, 72.8777),
    "Warangal": (17.9689, 79.5941),
    "Nellore": (14.4426, 79.9865),
    "Rajahmundry": (17.0005, 81.8040)
}

ALL_CITIES = sorted(list(CITY_COORDINATES.keys()))

def get_approx_distance(c1, c2):
    # Haversine formula approximation for road routing estimate
    lat1, lon1 = CITY_COORDINATES[c1]
    lat2, lon2 = CITY_COORDINATES[c2]
    R = 6371 # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    road_factor = 1.25 # actual highway road distance is ~25% longer than straight line
    return max(150, int(R * c * road_factor))

# --- HEADER HERO ---
st.markdown("""
<div class="agency-hero">
    <h1 style="margin:0; font-size:1.6rem; color:#fff;">YASHWANTH KUMAR Transport Agency</h1>
    <p style="margin:4px 0 0 0; color:#d0dbe5; font-size:0.9rem;">Official Intercity Volvo & Sleeper Coach Fleet • Pan-India</p>
</div>
""", unsafe_allow_html=True)

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.subheader("Passenger Login")
    with st.form("auth_form"):
        phone = st.text_input("Mobile Number", placeholder="10-digit mobile number")
        name = st.text_input("Passenger Name", placeholder="Your full name")
        if st.form_submit_button("Enter Booking Portal", use_container_width=True):
            if len(phone) == 10 and name.strip():
                st.session_state.logged_in = True
                st.session_state.user_phone = phone
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Please enter a valid 10-digit phone number and full name.")
    st.stop()

# --- TOP NAVIGATION ---
c_usr, c_out = st.columns([3, 1])
c_usr.write(f"Logged in as **{st.session_state.user_name}** ({st.session_state.user_phone})")
if c_out.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.step = "search"
    st.rerun()

st.markdown("---")

# ==========================================
# STEP 1: ROUTE SEARCH
# ==========================================
if st.session_state.step == "search":
    st.subheader("Select Route & Travel Date")
    c1, c2 = st.columns(2)
    from_city = c1.selectbox("From City", ALL_CITIES, index=ALL_CITIES.index("Hyderabad"))
    to_city = c2.selectbox("To City", ALL_CITIES, index=ALL_CITIES.index("Vijayawada"))
    journey_date = st.date_input("Travel Date", min_value=datetime.today().date())

    if st.button("Search Buses", type="primary", use_container_width=True):
        if from_city == to_city:
            st.error("Origin and Destination cannot be the same city.")
        else:
            dist = get_approx_distance(from_city, to_city)
            st.session_state.route_info = {
                "from": from_city,
                "to": to_city,
                "date": journey_date.strftime("%d %b %Y"),
                "distance": dist
            }
            st.session_state.step = "buses"
            st.rerun()

    if st.session_state.bookings:
        st.markdown("---")
        st.subheader("Your Past Bookings")
        for b in st.session_state.bookings:
            st.info(f"**PNR: {b['pnr']}** | {b['from']} ➔ {b['to']} | Seats: {', '.join(b['seats'])} | Paid: ₹{b['fare']}")

# ==========================================
# STEP 2: AVAILABLE FLEET WITH REALISTIC MARKET RATES & IMAGES
# ==========================================
elif st.session_state.step == "buses":
    r = st.session_state.route_info
    if st.button("⬅ Change Route"):
        st.session_state.step = "search"
        st.rerun()

    st.markdown(f"### Available Coaches: {r['from']} ➔ {r['to']}")
    st.caption(f"Estimated Highway Distance: ~{r['distance']} km • Journey Date: {r['date']}")

    # Calculate real-market dynamic pricing based on distance & coach tier
    dist = r['distance']
    rate_semi = max(450, int(dist * 1.50))
    rate_sleeper = max(750, int(dist * 2.20))
    rate_volvo = max(1100, int(dist * 3.10))

    coaches = [
        {
            "id": "volvo_9600",
            "name": "Volvo 9600 Multi-Axle Luxury Sleeper (15m)",
            "type": "AC Sleeper 2x1 • Individual LCD • Restroom",
            "img": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80",
            "timing": "21:30 ➔ 05:30",
            "fare": rate_volvo,
            "seats_avail": 12,
            "rating": "⭐ 4.9/5"
        },
        {
            "id": "ac_sleeper",
            "name": "Bharat Benz A/C Executive Sleeper",
            "type": "AC Sleeper 2x1 • Charging Ports • Reading Lamp",
            "img": "https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=800&q=80",
            "timing": "22:15 ➔ 06:45",
            "fare": rate_sleeper,
            "seats_avail": 18,
            "rating": "⭐ 4.6/5"
        },
        {
            "id": "semi_sleeper",
            "name": "Yashwanth Express Semi-Sleeper",
            "type": "2x2 Air Suspension High-Deck Seater",
            "img": "https://images.unsplash.com/photo-1494515843206-f3117d3f51b7?auto=format&fit=crop&w=800&q=80",
            "timing": "23:00 ➔ 07:30",
            "fare": rate_semi,
            "seats_avail": 26,
            "rating": "⭐ 4.3/5"
        }
    ]

    for c in coaches:
        st.markdown(f"""
        <div class="bus-card">
            <h4 style="margin:0 0 6px 0;">{c['name']} <span style="font-size:0.85rem; color:#f39c12;">{c['rating']}</span></h4>
            <p style="color:#555; font-size:0.85rem; margin:0 0 8px 0;">{c['type']} | <b>Timing:</b> {c['timing']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_img, col_act = st.columns([1.5, 1])
        col_img.image(c["img"], use_container_width=True, caption=c['name'])
        
        with col_act:
            st.metric("Market Fare / Seat", f"₹{c['fare']:,}")
            st.write(f"🟢 **{c['seats_avail']} Seats Available**")
            if st.button(f"Select Seats", key=f"sel_{c['id']}", type="primary"):
                st.session_state.selected_coach = c
                st.session_state.step = "seats"
                st.rerun()
        st.markdown("---")

# ==========================================
# STEP 3: VISUAL 42-BERTH SEAT NUMBER SELECTION (7 ROWS x 6 BERTHS)
# ==========================================
elif st.session_state.step == "seats":
    coach = st.session_state.selected_coach
    r = st.session_state.route_info

    if st.button("⬅ Back to Coach Selection"):
        st.session_state.step = "buses"
        st.rerun()

    st.subheader(f"Select Berths: {coach['name']}")
    st.caption("Standard 42-Berth Layout • 7 Rows • Lower & Upper Decks")

    # Generate all 42 berth identifiers
    # Double berths: L{row}A, L{row}B (Lower), U{row}A, U{row}B (Upper)
    # Side berths:   SL{row} (Lower), SU{row} (Upper)
    all_42_berths = []
    for row in range(1, 8):
        # Double side
        all_42_berths.extend([f"L{row}A", f"L{row}B", f"U{row}A", f"U{row}B"])
        # Side/Single berths
        all_42_berths.extend([f"SL{row}", f"SU{row}"])

    # Sample occupied berths
    occupied_seats = ["L1A", "U2B", "SL3", "U4A", "L6B", "SU7"]

    st.markdown("### 🚌 Bus Deck Layout")

    # --- LOWER DECK (3 Berths per row x 7 rows = 21 Lower Berths) ---
    with st.expander("🔻 LOWER DECK (21 Berths)", expanded=True):
        st.write("**Double Side (Left) &emsp;&emsp;&emsp;&emsp; Aisle &emsp;&emsp;&emsp;&emsp; Single Side (Right)**")
        for row in range(1, 8):
            c1, c2, c_aisle, c3 = st.columns([1, 1, 0.4, 1])
            
            # Double Berth 1
            s1 = f"L{row}A"
            if s1 in occupied_seats:
                c1.markdown(f"<div class='seat-box seat-booked'>{s1}<br>Booked</div>", unsafe_allow_html=True)
            else:
                c1.markdown(f"<div class='seat-box seat-avail'>{s1}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)
            
            # Double Berth 2
            s2 = f"L{row}B"
            if s2 in occupied_seats:
                c2.markdown(f"<div class='seat-box seat-booked'>{s2}<br>Booked</div>", unsafe_allow_html=True)
            else:
                c2.markdown(f"<div class='seat-box seat-avail'>{s2}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)
            
            c_aisle.markdown("<div style='text-align:center; color:#bbb;'>|</div>", unsafe_allow_html=True)
            
            # Single Side Berth
            s_side = f"SL{row}"
            if s_side in occupied_seats:
                c3.markdown(f"<div class='seat-box seat-booked'>{s_side}<br>Booked</div>", unsafe_allow_html=True)
            else:
                c3.markdown(f"<div class='seat-box seat-avail'>{s_side}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)

    # --- UPPER DECK (3 Berths per row x 7 rows = 21 Upper Berths) ---
    with st.expander("🔺 UPPER DECK (21 Berths)", expanded=True):
        st.write("**Double Side (Left) &emsp;&emsp;&emsp;&emsp; Aisle &emsp;&emsp;&emsp;&emsp; Single Side (Right)**")
        for row in range(1, 8):
            u1, u2, u_aisle, u3 = st.columns([1, 1, 0.4, 1])
            
            # Double Berth 1 Upper
            s1 = f"U{row}A"
            if s1 in occupied_seats:
                u1.markdown(f"<div class='seat-box seat-booked'>{s1}<br>Booked</div>", unsafe_allow_html=True)
            else:
                u1.markdown(f"<div class='seat-box seat-avail'>{s1}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)
            
            # Double Berth 2 Upper
            s2 = f"U{row}B"
            if s2 in occupied_seats:
                u2.markdown(f"<div class='seat-box seat-booked'>{s2}<br>Booked</div>", unsafe_allow_html=True)
            else:
                u2.markdown(f"<div class='seat-box seat-avail'>{s2}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)
            
            u_aisle.markdown("<div style='text-align:center; color:#bbb;'>|</div>", unsafe_allow_html=True)
            
            # Single Side Berth Upper
            s_side = f"SU{row}"
            if s_side in occupied_seats:
                u3.markdown(f"<div class='seat-box seat-booked'>{s_side}<br>Booked</div>", unsafe_allow_html=True)
            else:
                u3.markdown(f"<div class='seat-box seat-avail'>{s_side}<br>₹{coach['fare']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Available seats to select
    selectable_berths = [b for b in all_42_berths if b not in occupied_seats]

    chosen_berths = st.multiselect(
        "Choose Your Berth(s):",
        options=selectable_berths,
        default=[selectable_berths[0]]
    )

    if chosen_berths:
        total_price = len(chosen_berths) * coach['fare']
        st.success(f"Selected: **{', '.join(chosen_berths)}** ({len(chosen_berths)} Berths) | Total: **₹{total_price:,}**")

        passenger_names = st.text_input("Passenger Name(s)", value=st.session_state.user_name)

        if st.button("Confirm & Pay Ticket", type="primary", use_container_width=True):
            pnr = f"YKT-{datetime.now().strftime('%d%H%M%S')}"
            booking = {
                "pnr": pnr,
                "coach": coach['name'],
                "from": r['from'],
                "to": r['to'],
                "date": r['date'],
                "seats": chosen_berths,
                "passengers": passenger_names,
                "fare": total_price
            }
            st.session_state.bookings.append(booking)
            st.session_state.last_ticket = booking
            st.session_state.step = "receipt"
            st.rerun()


# ==========================================
# STEP 4: CONFIRMED E-TICKET RECEIPT
# ==========================================
elif st.session_state.step == "receipt":
    t = st.session_state.last_ticket
    st.balloons()
    st.success("🎉 Ticket Confirmed Successfully!")

    st.markdown(f"""
    <div style="background-color:#ffffff; padding:22px; border-radius:14px; border:2px solid #0d2b45; box-shadow:0 6px 12px rgba(0,0,0,0.08);">
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #ddd; padding-bottom:10px;">
            <h3 style="margin:0; color:#0d2b45;">YASHWANTH KUMAR Transport Agency</h3>
            <span style="font-weight:bold; color:#2e7d32;">STATUS: CONFIRMED</span>
        </div>
        <p style="margin-top:12px;"><b>PNR:</b> <span style="font-family:monospace; font-size:1.1rem; color:#d32f2f;">{t['pnr']}</span></p>
        <p><b>Passenger(s):</b> {t['passengers']}</p>
        <p><b>Route:</b> {t['from']} ➔ {t['to']}</p>
        <p><b>Travel Date:</b> {t['date']}</p>
        <p><b>Bus Type:</b> {t['coach']}</p>
        <p><b>Seat Number(s):</b> <span style="background:#e8f5e9; padding:3px 8px; border-radius:4px; font-weight:bold; color:#1b5e20;">{', '.join(t['seats'])}</span></p>
        <hr>
        <h4 style="margin:0; text-align:right;">Total Paid: ₹{t['fare']:,} (Inc. GST)</h4>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Book Another Ticket", type="primary", use_container_width=True):
        st.session_state.step = "search"
        st.rerun()
