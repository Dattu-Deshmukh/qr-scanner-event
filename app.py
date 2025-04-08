import streamlit as st
import cv2
import pandas as pd
import qrcode
import numpy as np
from PIL import Image

# Custom CSS for Google Lens-like styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #212121;
        color: white;
    }
    .title {
        font-size: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .instruction {
        font-size: 16px;
        text-align: center;
        font-family: 'cursive';
        color: #bbdefb;
    }
    .capture-box {
        text-align: center;
        margin-top: 20px;
    }
    .details-box {
        text-align: center;
        margin-top: 20px;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load student data
try:
    student_df = pd.read_csv("students.csv")
    student_df["Roll Number"] = student_df["Roll Number"].astype(str)
    if "Scanned" not in student_df.columns:
        student_df["Scanned"] = False
except FileNotFoundError:
    st.error("❌ Error: 'students.csv' not found. Please upload the student data file.")
    st.stop()

# UI Setup
st.markdown('<div class="title">🎉 2k25 Farewell Party Event</div>', unsafe_allow_html=True)
st.markdown('<div class="instruction">Capture with your camera</div>', unsafe_allow_html=True)

# Placeholder for student details
details_box = st.empty()

# Function to decode QR code from image
def decode_qr(image):
    # Convert PIL Image to OpenCV format
    img = np.array(image.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    return data if data else None

# Camera input
image = st.camera_input("Point your QR code at the camera and capture", key="camera_input")

if image is not None:
    # Decode the QR code
    qr_data = decode_qr(Image.open(image))
    if qr_data:
        # Check if roll number exists and hasn't been scanned
        student = student_df[student_df["Roll Number"] == qr_data]
        if not student.empty and not student["Scanned"].iloc[0]:
            # Display student details
            roll = student["Roll Number"].iloc[0]
            name = student["Student Name"].iloc[0]
            dept = student["Department"].iloc[0]
            details_box.markdown(
                '<div class="details-box" style="background-color: #424242; color: white;">'
                f'✅ Welcome!\n\n**Roll Number**: {roll}\n**Name**: {name}\n**Department**: {dept}'
                '</div>',
                unsafe_allow_html=True
            )
            # Mark as scanned
            student_df.loc[student_df["Roll Number"] == qr_data, "Scanned"] = True
            student_df.to_csv("students.csv", index=False)  # Save updated status
        elif not student.empty:
            details_box.markdown(
                '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                f'❌ Already Scanned: {qr_data}'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            details_box.markdown(
                '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                f'❌ Invalid QR Code: {qr_data}'
                '</div>',
                unsafe_allow_html=True
            )
    else:
        details_box.markdown(
            '<div class="details-box" style="background-color: #d32f2f; color: white;">'
            '❌ No QR code detected. Try again!'
            '</div>',
            unsafe_allow_html=True
        )

# Instructions
st.markdown("---")
st.write("🎊 **How to Enter**: Point your QR code at the camera, capture the image, and check your details!")
