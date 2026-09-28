const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('.'));

const otpStore = {};
const bookingStore = {};

// 1. Send OTP Endpoint
app.post('/api/auth/send-otp', (req, res) => {
  const { phone } = req.body;

  if (!/^[6-9]\d{9}$/.test(phone)) {
    return res.status(400).json({ success: false, message: 'Invalid 10-digit mobile number' });
  }

  const otp = Math.floor(100000 + Math.random() * 900000).toString();
  otpStore[phone] = {
    otp,
    expiresAt: Date.now() + 5 * 60 * 1000
  };

  console.log(`\n================================`);
  console.log(`[SMS GATEWAY] OTP for +91${phone}: ${otp}`);
  console.log(`================================\n`);

  res.json({ success: true, message: 'OTP sent successfully' });
});

// 2. Verify OTP Endpoint
app.post('/api/auth/verify-otp', (req, res) => {
  const { phone, otp } = req.body;
  const record = otpStore[phone];

  if (!record || Date.now() > record.expiresAt) {
    return res.status(400).json({ success: false, message: 'OTP expired or not requested' });
  }

  if (record.otp !== otp) {
    return res.status(400).json({ success: false, message: 'Invalid OTP' });
  }

  delete otpStore[phone];
  res.json({ success: true, token: `auth_${phone}_${Date.now()}` });
});

// 3. Initiate Payment Endpoint
app.post('/api/tickets/create-payment', (req, res) => {
  const { phone, seatNumber, amountInRupees } = req.body;
  const orderId = `ORDER_${Date.now()}`;

  bookingStore[orderId] = {
    phone,
    seatNumber: seatNumber || 'Seat-1',
    amount: amountInRupees || 450,
    status: 'PENDING_PAYMENT'
  };

  // Redirect link: For testing, redirects to simulation gateway
  const redirectUrl = `/pay-screen?orderId=${orderId}`;
  res.json({ success: true, redirectUrl, orderId });
});

// 4. Payment Gateway Simulation Screen
app.get('/pay-screen', (req, res) => {
  const { orderId } = req.query;
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>PhonePe Payment</title>
      <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 90vh; margin: 0; background: #f2f2f2; }
        .box { background: white; padding: 24px; border-radius: 12px; text-align: center; max-width: 320px; width: 100%; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .btn { background: #5f259f; color: white; border: none; padding: 12px 20px; border-radius: 6px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 15px; }
      </style>
    </head>
    <body>
      <div class="box">
        <h2 style="color: #5f259f;">PhonePe Gateway</h2>
        <p>Order ID: <b>${orderId}</b></p>
        <p>Amount: <b>₹450</b></p>
        <form action="/api/payments/complete" method="POST">
          <input type="hidden" name="orderId" value="${orderId}" />
          <button class="btn" type="submit">Pay & Authorize</button>
        </form>
      </div>
    </body>
    </html>
  `);
});

// 5. Complete Payment & Confirm Ticket
app.post('/api/payments/complete', (req, res) => {
  const { orderId } = req.body;
  if (bookingStore[orderId]) {
    bookingStore[orderId].status = 'CONFIRMED';
  }
  res.redirect(`/status?orderId=${orderId}`);
});

// 6. Booking Confirmation Screen
app.get('/status', (req, res) => {
  const { orderId } = req.query;
  const booking = bookingStore[orderId];
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Ticket Status</title>
      <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 90vh; margin: 0; background: #f8fafc; }
        .card { background: white; padding: 24px; border-radius: 12px; text-align: center; max-width: 340px; width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: bold; background: #dcfce7; color: #15803d; }
      </style>
    </head>
    <body>
      <div class="card">
        <h3>Booking Summary</h3>
        <p>Order ID: <b>${orderId}</b></p>
        <p>Status: <span class="badge">${booking ? booking.status : 'NOT FOUND'}</span></p>
        <a href="/" style="display: inline-block; margin-top: 15px; color: #5f259f; text-decoration: none;">Book Another Ticket</a>
      </div>
    </body>
    </html>
  `);
});

const PORT = 3000;
app.listen(PORT, () => console.log(`App running at http://localhost:${PORT}`));
