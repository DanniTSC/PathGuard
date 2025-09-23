
import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.title("PathGuard — Minimal Dashboard")
st.write(f"API base: `{API_BASE}`")

col1, col2 = st.columns(2)
with col1:
    start = st.text_input("Start (lat,lon)", "50.12,8.67")
with col2:
    end = st.text_input("End (lat,lon)", "50.15,8.70")

if st.button("Compute Toy Route"):
    try:
        r = requests.get(f"{API_BASE}/route", params={"start": start, "end": end}, timeout=10)
        r.raise_for_status()
        data = r.json()
        st.subheader("Route Safety")
        st.metric("Safety score", data.get("safety_score", "-"))
        st.write("**Explanation**:", data.get("explanation", ""))
        st.write("**Segments:**")
        st.json(data.get("segments", []))
    except Exception as e:
        st.error(f"Failed to call API: {e}")
