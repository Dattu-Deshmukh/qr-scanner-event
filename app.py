import streamlit as st
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import json

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
    # Map columns flexibly
    column_mapping = {
        "Roll Number": next((col for col in student_df.columns if "roll" in col.lower()), "Roll Number"),
        "Student Name": next((col for col in student_df.columns if "name" in col.lower()), "Student Name"),
        "Department": next((col for col in student_df.columns if "dept" in col.lower()), "Department")
    }
    if "Scanned" not in student_df.columns:
        student_df["Scanned"] = False
except FileNotFoundError:
    st.error("❌ Error: 'students.csv' not found. Please upload the student data file.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading CSV: {str(e)}. Please check the file format.")
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

# Function to extract roll number from QR data
def extract_roll_number(qr_data):
    try:
        # Attempt to parse JSON if the data is in JSON format
        data_dict = json.loads(qr_data)
        return data_dict.get("roll_no")
    except json.JSONDecodeError:
        # Return raw data if it's not JSON
        return qr_data

# Camera input
image = st.camera_input("Point your QR code at the camera and capture", key="camera_input")

if image is not None:
    # Decode the QR code
    qr_data = decode_qr(Image.open(image))
    if qr_data:
        # Extract roll number from QR data
        roll_number = extract_roll_number(qr_data)
        if roll_number:
            # Check if roll number exists and hasn't been scanned
            student = student_df[student_df[column_mapping["Roll Number"]] == roll_number]
            if not student.empty and not student["Scanned"].iloc[0]:
                # Display student details using mapped columns
                roll = student[column_mapping["Roll Number"]].iloc[0]
                name = student[column_mapping["Student Name"]].iloc[0]
                dept = student[column_mapping["Department"]].iloc[0]
                details_box.markdown(
                    '<div class="details-box" style="background-color: #424242; color: white;">'
                    f'✅ Welcome!\n\n**Roll Number**: {roll}\n**Name**: {name}\n**Department**: {dept}'
                    '</div>',
                    unsafe_allow_html=True
                )
                # Mark as scanned
                student_df.loc[student_df[column_mapping["Roll Number"]] == roll_number, "Scanned"] = True
                student_df.to_csv("students.csv", index=False)  # Save updated status
            elif not student.empty:
                details_box.markdown(
                    '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                    f'❌ Already Scanned: {roll_number}'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                details_box.markdown(
                    '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                    f'❌ Invalid QR Code: {roll_number}'
                    '</div>',
                    unsafe_allow_html=True
                )
        else:
            details_box.markdown(
                '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                f'❌ Invalid QR Code format: {qr_data}'
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

# Clear photo button
if image is not None:
    if st.button("❌ Clear photo"):
        st.session_state.camera_input = None
        details_box.empty()

# Instructions
st.markdown("---")
st.write("🎊 **How to Enter**: Point your QR code at the camera, capture the image, and check your details!")
