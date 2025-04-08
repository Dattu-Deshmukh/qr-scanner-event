import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
import pandas as pd
import av
import time

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
st.markdown('<div class="instruction">Scan with your camera</div>', unsafe_allow_html=True)

# Button to start/stop scanning (mimics Google Lens activation)
if "scanner_active" not in st.session_state:
    st.session_state.scanner_active = False

if st.button("📷", key="camera_button", help="Tap to start scanning"):
    st.session_state.scanner_active = not st.session_state.scanner_active

# Placeholder for student details
details_box = st.empty()

# QR Scanner Class
class QRScanner(VideoProcessorBase):
    def __init__(self):
        self.last_data = None
        self.last_scan_time = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        current_time = time.time()
        # Process QR code only if new data is detected and 2 seconds have passed
        if data and data != self.last_data and (current_time - self.last_scan_time > 2):
            self.last_data = data
            self.last_scan_time = current_time

            # Check if roll number exists and hasn't been scanned
            student = student_df[student_df["Roll Number"] == data]
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
                student_df.loc[student_df["Roll Number"] == data, "Scanned"] = True
                student_df.to_csv("students.csv", index=False)  # Save updated status
            elif not student.empty:
                details_box.markdown(
                    '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                    f'❌ Already Scanned: {data}'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                details_box.markdown(
                    '<div class="details-box" style="background-color: #d32f2f; color: white;">'
                    f'❌ Invalid QR Code: {data}'
                    '</div>',
                    unsafe_allow_html=True
                )

        # Return the frame for display
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Start the webcam stream only when button is pressed
if st.session_state.scanner_active:
    webrtc_streamer(
        key="qr-scanner",
        video_processor_factory=QRScanner,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
        media_stream_constraints={"video": True, "audio": False},
    )

# Instructions
st.markdown("---")
st.write("🎊 **How to Enter**: Tap the camera button, then show your QR code. Valid codes display your details!")
