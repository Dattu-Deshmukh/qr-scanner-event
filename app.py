import streamlit as st
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import json

# Custom CSS for mobile-friendly styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #212121;
        color: white;
    }
    .title {
        font-size: 16px; /* Further reduced for mobile */
        text-align: center;
        margin: 5px 0;
    }
    .instruction {
        font-size: 12px; /* Optimized for mobile */
        text-align: center;
        font-family: 'cursive';
        color: #bbdefb;
    }
    .upload-box, .manual-box {
        text-align: center;
        margin: 5px 0;
    }
    .details-box {
        text-align: center;
        margin: 5px 0;
        padding: 5px;
        border-radius: 5px;
    }
    .login-box {
        text-align: center;
        margin: 5px 0;
    }
    .stButton>button {
        width: 100%;
        max-width: 200px;
        margin: 5px auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Coordinator credentials
VALID_CREDENTIALS = {
    "coord1": "FAIRWELL2K25",
    "coord2": "PARTY2025",
    "coord3": "EVENT2025",
    "coord4": "WELCOME2025",
    "coord5": "CELEBRATE2025"
}

# Login function
def check_credentials():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        if st.button("Login"):
            if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
                st.session_state.authenticated = True
                st.success(f"Login successful! Welcome, {username}!")
            else:
                st.error("❌ Invalid username or password. Please try again.")
                st.stop()
    return st.session_state.authenticated

# Load student data if credentials are correct
if check_credentials():
    try:
        student_df = pd.read_csv("students.csv")
        student_df["Roll Number"] = student_df["Roll Number"].astype(str)
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
    st.markdown('<div class="instruction">Upload or enter your QR code data</div>', unsafe_allow_html=True)

    # Placeholder for student details
    details_box = st.empty()

    # Function to decode QR code from image
    def decode_qr(image):
        img = np.array(image.convert('RGB'))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)
        return data if data else None

    # Function to extract roll number from QR data
    def extract_roll_number(qr_data):
        try:
            data_dict = json.loads(qr_data)
            return data_dict.get("roll_no")
        except json.JSONDecodeError:
            return qr_data

    # Upload image option
    uploaded_file = st.file_uploader("Tap to upload a QR code photo", type=["jpg", "jpeg", "png"], key="upload_input")

    # Manual entry option
    manual_input = st.text_input("Or enter roll number manually", key="manual_input")

    # Process input
    if uploaded_file is not None:
        qr_data = decode_qr(Image.open(uploaded_file))
        if qr_data:
            roll_number = extract_roll_number(qr_data)
            if roll_number:
                student = student_df[student_df[column_mapping["Roll Number"]] == roll_number]
                if not student.empty and not student["Scanned"].iloc[0]:
                    roll = student[column_mapping["Roll Number"]].iloc[0]
                    name = student[column_mapping["Student Name"]].iloc[0]
                    dept = student[column_mapping["Department"]].iloc[0]
                    details_box.markdown(
                        '<div class="details-box" style="background-color: #424242; color: white;">'
                        f'✅ Welcome!\n\n**Roll Number**: {roll}<br>**Name**: {name}<br>**Department**: {dept}'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    student_df.loc[student_df[column_mapping["Roll Number"]] == roll_number, "Scanned"] = True
                    student_df.to_csv("students.csv", index=False)
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
    elif manual_input:
        roll_number = manual_input.strip()
        student = student_df[student_df[column_mapping["Roll Number"]] == roll_number]
        if not student.empty and not student["Scanned"].iloc[0]:
            roll = student[column_mapping["Roll Number"]].iloc[0]
            name = student[column_mapping["Student Name"]].iloc[0]
            dept = student[column_mapping["Department"]].iloc[0]
            details_box.markdown(
                '<div class="details-box" style="background-color: #424242; color: white;">'
                f'✅ Welcome!\n\n**Roll Number**: {roll}<br>**Name**: {name}<br>**Department**: {dept}'
                '</div>',
                unsafe_allow_html=True
            )
            student_df.loc[student_df[column_mapping["Roll Number"]] == roll_number, "Scanned"] = True
            student_df.to_csv("students.csv", index=False)
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
                f'❌ Invalid Roll Number: {roll_number}'
                '</div>',
                unsafe_allow_html=True
            )

    # Clear button
    if uploaded_file is not None or manual_input:
        if st.button("❌ Clear"):
            st.session_state.upload_input = None
            st.session_state.manual_input = ""
            details_state.empty()

    # Instructions
    st.markdown("---")
    st.write("🎊 **How to Enter**: 1) Use your phone’s camera to take a photo of your QR code and upload it. 2) Or enter your roll number manually. Check your details!")
