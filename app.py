import streamlit as st
import pandas as pd

st.set_page_config(page_title="QR Code Scanner", layout="centered")

# Load student data
@st.cache_data
def load_data():
    return pd.read_csv("students.csv")

df = load_data()

st.title("🎓 Event QR Code Scanner")
st.write("Scan a QR code or enter token manually below")

token = st.text_input("Enter scanned token (e.g., Roll Number)")

if token:
    student = df[df["Roll Number"] == token]
    if not student.empty:
        st.success(f"✅ Verified: {student.iloc[0]['Name']} ({student.iloc[0]['Dept.Branch']})")
    else:
        st.error("❌ Invalid QR Code or Student not found.")
