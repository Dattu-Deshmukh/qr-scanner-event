import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import pandas as pd

# Load student data
student_df = pd.read_csv("students.csv")
valid_tokens = set(student_df["Roll Number"].astype(str))

# UI
st.title("🎓 College Event QR Scanner")
st.markdown("📷 Point your camera at the QR Code to check entry")

# Result Display
result_box = st.empty()

class QRScanner(VideoProcessorBase):
    def __init__(self):
        self.last_data = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if data and data != self.last_data:
            self.last_data = data
            if data in valid_tokens:
                result_box.success(f"✅ Allowed: Welcome!")
            else:
                result_box.error("❌ Not Allowed: Invalid QR Code")
        
        return img

webrtc_streamer(key="qr-scanner", video_processor_factory=QRScanner)
