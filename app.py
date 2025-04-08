import streamlit as st
import pandas as pd
import json
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2

# Load student data
df = pd.read_csv("students.csv")

st.set_page_config(page_title="Event QR Code Scanner", layout="centered")
st.title("🎓 Event QR Code Scanner")
st.write("Scan your QR code to check if you're allowed into the event.")

# ===================== QR SCANNER LOGIC =====================

class QRScanner(VideoProcessorBase):
    def __init__(self):
        self.result = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if data:
            try:
                parsed = json.loads(data)
                roll = parsed.get("roll_no", "").strip()
                match = df[df["Roll Number"].astype(str).str.strip() == roll]

                if not match.empty:
                    self.result = f"✅ Welcome {match.iloc[0]['Name']}! 🎉 You are allowed to the event."
                else:
                    self.result = "❌ Not allowed. Roll number not found."
            except:
                self.result = "❌ Invalid QR format."

        return av.VideoFrame.from_ndarray(img, format="bgr24")


ctx = webrtc_streamer(
    key="qr-scanner",
    video_processor_factory=QRScanner,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if ctx.video_processor:
    result = ctx.video_processor.result
    if result:
        st.info(result)
