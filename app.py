import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2
import pandas as pd
import av
import time

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
st.title("🎉 2k25 Farewell Party Event")
st.markdown("📷 Point your QR code at the camera to verify entry")

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
                details_box.success(f"✅ Valid Entry\n\n**Roll Number**: {roll}\n**Name**: {name}\n**Department**: {dept}")
                # Mark as scanned
                student_df.loc[student_df["Roll Number"] == data, "Scanned"] = True
                student_df.to_csv("students.csv", index=False)  # Save updated status
            elif not student.empty:
                details_box.error(f"❌ Already Scanned: {data}")
            else:
                details_box.error(f"❌ Invalid QR Code: {data}")

        # Return the frame for display
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Start the webcam stream
webrtc_streamer(
    key="qr-scanner",
    video_processor_factory=QRScanner,
    rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
    media_stream_constraints={"video": True, "audio": False},
)

# Instructions
st.markdown("---")
st.write("**Instructions**: Show your QR code to the camera. Valid codes display your details!")
