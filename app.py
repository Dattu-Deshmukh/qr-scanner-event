import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd

# Page settings
st.set_page_config(page_title="🎓 Event QR Code Scanner", layout="centered")
st.title("🎓 Event QR Code Scanner")
st.write("📷 Upload a QR code image or manually enter token")

# Load student data
@st.cache_data
def load_data():
    return pd.read_csv("students.csv")

df = load_data()

# Upload QR image
uploaded_file = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

# QR Code Detector
if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        st.success(f"✅ Scanned Token: {data}")
        matched = df[df['Roll Number'].astype(str).str.strip() == data.strip()]
        if not matched.empty:
            student = matched.iloc[0]
            st.info(f"🎉 Name: {student['Name']} \n\n 🏷️ Dept.Branch: {student['Dept.Branch']}")
        else:
            st.error("⚠️ Token not found in students.csv")
    else:
        st.warning("❌ No QR code detected in image.")

# Manual entry fallback
token = st.text_input("Or enter scanned token (e.g., Roll Number):")
if st.button("Check Token"):
    matched = df[df['Roll Number'].astype(str).str.strip() == token.strip()]
    if not matched.empty:
        student = matched.iloc[0]
        st.success(f"🎉 Name: {student['Name']} \n\n 🏷️ Dept.Branch: {student['Dept.Branch']}")
    else:
        st.error("⚠️ Token not found in students.csv")
