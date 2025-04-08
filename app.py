import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import pandas as pd
import qrcode
import numpy as np

# Load student data
student_df = pd.read_csv("students.csv")
valid_tokens = set(student_df["Roll Number"].astype(str))

# Display
st.title("🎓 College Event QR Scanner")
st.markdown("📷 Scan student QR code to verify entry")

# Result display box
result_box = st.empty()

# Custom Video Processor
class QRScanner(VideoProcessorBase):
    def __init__(self):
        self.last_scanned = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)
        
        if data and data != self.last_scanned:
            self.last_scanned = data
            if data in valid_tokens:
                result_box.success("✅ Allowed: Welcome to the event!")
            else:
                result_box.error("❌ Not Allowed: Invalid QR Code")

        return img

# Start WebRTC Camera Stream
webrtc_streamer(key="qr-scanner", video_processor_factory=QRScanner)
