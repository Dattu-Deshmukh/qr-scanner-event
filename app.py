import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import cv2
import pandas as pd

# Load CSV with student data
student_df = pd.read_csv("students.csv")
valid_tokens = set(student_df["Roll Number"].astype(str))

# Streamlit UI
st.set_page_config(page_title="QR Entry", layout="centered")
st.markdown("## 🎟️ Event QR Scanner")
st.markdown("📸 Just scan the QR code. No upload, no buttons, just go.")

# Show result
result_placeholder = st.empty()

# QR Scanner Class
class QRProcessor(VideoProcessorBase):
    def __init__(self):
        self.last_token = None

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(image)

        if data and data != self.last_token:
            self.last_token = data
            if data in valid_tokens:
                result_placeholder.success(f"✅ Allowed: {data}")
            else:
                result_placeholder.error("❌ Not Allowed")

        return image

# Auto launch camera
webrtc_streamer(
    key="scan",
    video_processor_factory=QRProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)
