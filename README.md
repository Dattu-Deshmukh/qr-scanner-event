# 🎟️ QR Code-Based Entry System for College Events

A simple and secure QR code-based entry system built using **Streamlit**, designed to streamline student check-in during college events.

✅ **Live App**: https://qr-scanner-entrypass-fairwell-event.streamlit.app
_(Open this link on your mobile device to scan student QR codes)_

## 🔍 Features

- 🎫 Unique one-time QR codes generated for each student.
- 📧 QR codes sent directly to student domain emails.
- 📱 Mobile-friendly scanner for event coordinators.
- 🧾 CSV-based token verification (no external database).
- 🛡️ Verifies and blocks reused or invalid tokens.

## 🗂️ How It Works

1. Organizers prepare a CSV with student details (Name, Roll Number, Dept, Email).
2. QR codes with unique tokens are generated for each student.
3. Each student receives a QR code via email.
4. Event coordinators scan QR codes using the mobile Streamlit app.
5. The app validates the token and prevents reuse.

## 📁 Files Overview

```bash
qr-code-entry-system/
├── students.csv               # Input student data
├── qr_generator.py            # Generates QR codes
├── email_sender.py            # Sends QR codes to emails
├── app.py                     # Streamlit QR scanner (already deployed)
├── requirements.txt
└── README.md
