import streamlit as st
import pandas as pd
import cv2
from pyzbar.pyzbar import decode
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

st.set_page_config(page_title="QR Code Scanner", layout="centered")

@st.cache_data
def load_data():
    return pd.read_csv("students.csv")

df = load_data()

st.title("🎓 Event QR Code Scanner")
st.write("📷 Scan your QR code below or enter token manually")

# Webcam QR scanner
class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.result = None

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        decoded_objs = decode(image)
        for obj in decoded_objs:
            self.result = obj.data.decode("utf-8")
            cv2.rectangle(image, (obj.rect.left, obj.rect.top),
                          (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                          (0, 255, 0), 2)
        return image

ctx = webrtc_streamer(key="qr-scanner", video_transformer_factory=QRScanner)

if ctx.video_transformer and ctx.video_transformer.result:
    token = ctx.video_transformer.result
    st.success(f"Scanned Token: {token}")

    student = df[df["Roll Number"] == token]
    if not student.empty:
        st.success(f"✅ Verified: {student.iloc[0]['Name']} ({student.iloc[0]['Dept.Branch']})")
    else:
        st.error("❌ Invalid QR Code or Student not found.")

# Manual entry fallback
st.markdown("---")
manual_token = st.text_input("Or manually enter token (Roll Number)")
if manual_token:
    student = df[df["Roll Number"] == manual_token]
    if not student.empty:
        st.success(f"✅ Verified: {student.iloc[0]['Name']} ({student.iloc[0]['Dept.Branch']})")
    else:
        st.error("❌ Invalid QR Code or Student not found.")
