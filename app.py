import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
import pandas as pd
import av
import time

# Load student data
try:
    student_df = pd.read_csv("students.csv")
    # Ensure Roll Number is string type and create a set of valid, unscanned roll numbers
    student_df["Roll Number"] = student_df["Roll Number"].astype(str)
    if "Scanned" not in student_df.columns:
        student_df["Scanned"] = False
    valid_tokens = set(student_df[student_df["Scanned"] == False]["Roll Number"])
except FileNotFoundError:
    st.error("❌ Error: 'students.csv' not found. Please provide the student data file.")
    st.stop()

# UI Setup
st.title("🎉 2k25 Farewell Party Event")
st.markdown("📷 Scan your QR code below to check entry!")

# Result Display and Scanned List
result_box = st.empty()
scanned_list = st.sidebar.empty()
st.sidebar.title("✅ Scanned Students")
update_scanned = st.sidebar.button("Refresh Scanned List")

# Initialize session state for tracking scanned roll numbers
if "scanned_rolls" not in st.session_state:
    st.session_state.scanned_rolls = []

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
        # Process QR code only if new data is detected and 2 seconds have passed since last scan
        if data and data != self.last_data and (current_time - self.last_scan_time > 2):
            self.last_data = data
            self.last_scan_time = current_time

            if data in valid_tokens:
                result_box.success(f"✅ Welcome! Roll Number: {data}")
                # Mark as scanned in dataframe and update valid_tokens
                student_df.loc[student_df["Roll Number"] == data, "Scanned"] = True
                valid_tokens.remove(data)
                st.session_state.scanned_rolls.append(data)
                student_df.to_csv("students.csv", index=False)  # Save updated status
            else:
                if data in student_df["Roll Number"].values:
                    result_box.error(f"❌ Already Scanned: Roll Number {data}")
                else:
                    result_box.error("❌ Invalid QR Code")

        # Convert back to VideoFrame for streamlit_webrtc
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Display scanned students in sidebar
if update_scanned or st.session_state.scanned_rolls:
    scanned_list.write(st.session_state.scanned_rolls)

# Start the webcam stream
webrtc_streamer(
    key="qr-scanner",
    video_processor_factory=QRScanner,
    rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
    media_stream_constraints={"video": True, "audio": False},
)

# Instructions
st.markdown("---")
st.write("**Instructions**: Point your QR code at the camera. One-time use only!")
