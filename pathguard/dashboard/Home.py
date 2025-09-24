
import os
import requests
import streamlit as st
from typing import Tuple, Optional
import folium
from streamlit.components.v1 import html

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
USE_HF = os.getenv("USE_HF", "false").lower() == "true"

st.set_page_config(page_title="PathGuard — Route Safety", page_icon="🛡️", layout="wide")
st.title("🛡️ PathGuard — Route Safety & Accessibility (MVP)")

with st.sidebar:
    st.header("⚙️ Settings")
    api_base = st.text_input("API base", API_BASE)
    st.caption("Tip: run the API with `uvicorn --app-dir pathguard app.api:app --reload`")
    colA, colB = st.columns([1, 1])
    with colA:
        use_hf_ui = st.toggle("Use HF summarizer", value=USE_HF)
    with colB:
        if st.button("Check API health", use_container_width=True):
            try:
                r = requests.get(f"{api_base}/health", timeout=5)
                r.raise_for_status()
                st.success(f"API OK: {r.json()}")
            except Exception as e:
                st.error(f"API not reachable: {e}")
    st.divider()
    st.caption("Note: HF toggle is read by the API server via `USE_HF` env var.")

col1, col2 = st.columns(2)
with col1:
    start = st.text_input("Start (lat,lon)", "50.12,8.67")
with col2:
    end = st.text_input("End (lat,lon)", "50.15,8.70")


def parse_latlon(text: str) -> Optional[Tuple[float, float]]:
    try:
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != 2:
            return None
        lat = float(parts[0])
        lon = float(parts[1])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return lat, lon
    except Exception:
        return None


def render_map(start_ll: Tuple[float, float], end_ll: Tuple[float, float]):
    lat_mid = (start_ll[0] + end_ll[0]) / 2
    lon_mid = (start_ll[1] + end_ll[1]) / 2
    m = folium.Map(location=[lat_mid, lon_mid], zoom_start=14, tiles="cartodbpositron")
    folium.Marker(start_ll, tooltip="Start", icon=folium.Icon(color="green", icon="play")).add_to(m)
    folium.Marker(end_ll, tooltip="End", icon=folium.Icon(color="red", icon="stop")).add_to(m)
    folium.PolyLine([start_ll, end_ll], color="#1e88e5", weight=5, opacity=0.8).add_to(m)
    html_str = m.get_root().render()
    html(html_str, height=420)


st.divider()

left, right = st.columns([1, 1])

with left:
    if st.button("🚀 Compute Route", type="primary"):
        start_ll = parse_latlon(start)
        end_ll = parse_latlon(end)
        if not start_ll or not end_ll:
            st.error("Please provide valid coordinates like '50.12,8.67'.")
        else:
            try:
                r = requests.get(f"{api_base}/route", params={"start": start, "end": end}, timeout=15)
                r.raise_for_status()
                data = r.json()
                score = data.get("safety_score", None)
                explanation = data.get("explanation", "")
                segments = data.get("segments", [])

                # Pretty score badge
                if isinstance(score, (int, float)):
                    color = "#2e7d32" if score >= 0.8 else ("#f9a825" if score >= 0.6 else "#c62828")
                    st.markdown(
                        f"<div style='display:inline-block;padding:8px 12px;border-radius:8px;background:{color};color:white;font-weight:600;'>Safety score: {score}</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.metric("Safety score", "-")

                st.subheader("Explanation")
                st.write(explanation)

                st.subheader("Segments")
                if segments:
                    # Format reasons as comma-separated chips-like string
                    seg_rows = []
                    for s in segments:
                        seg_rows.append({
                            "id": s.get("id"),
                            "name": s.get("name"),
                            "safety": s.get("safety"),
                            "reasons": ", ".join(s.get("reasons", [])),
                        })
                    st.dataframe(seg_rows, use_container_width=True)
                else:
                    st.info("No segments returned.")

            except Exception as e:
                st.error(f"Failed to call API: {e}")

with right:
    start_ll = parse_latlon(start)
    end_ll = parse_latlon(end)
    if start_ll and end_ll:
        render_map(start_ll, end_ll)
    else:
        st.info("Enter valid start/end to preview route on the map.")
