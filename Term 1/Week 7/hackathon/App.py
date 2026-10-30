"""Waterbird Counter: detects and counts mallards, coots and Egyptian geese
in photos of Dutch city ponds and canals, using a Roboflow RF-DETR model.
SDG 15: Life on Land.
"""

import base64
import io
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------- Config ----------
HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID")  # e.g. my-first-project-ulrtu/2
API_URL = "https://serverless.roboflow.com"
MAX_SIDE = 1280  # resize large phone photos before sending

# class name in model -> (display name, box colour)
CLASSES = {
    "mallard": ("Mallard", "#2e7d32"),
    "coot": ("Coot", "#1565c0"),
    "egyptian_goose": ("Egyptian goose (exotic)", "#e65100"),
}


# ---------- Helpers ----------
def prepare_image(file) -> Image.Image:
    """Open upload, fix phone rotation, convert to RGB, shrink if huge."""
    img = Image.open(file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return img


def to_jpeg_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


@st.cache_data(show_spinner=False)
def predict(jpeg_bytes: bytes, confidence: float) -> list[dict]:
    """Send image to the Roboflow hosted model, return list of detections."""
    b64 = base64.b64encode(jpeg_bytes).decode("utf-8")
    response = requests.post(
        f"{API_URL}/{MODEL_ID}",
        params={"api_key": API_KEY, "confidence": int(confidence * 100)},
        data=b64,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("predictions", [])


def draw_boxes(img: Image.Image, preds: list[dict]) -> Image.Image:
    """Draw a coloured box + label for every detection."""
    out = img.copy()
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.load_default(size=max(14, out.width // 60))
    except TypeError:  # older Pillow
        font = ImageFont.load_default()
    line = max(2, out.width // 300)

    for p in preds:
        _, color = CLASSES.get(p["class"], (p["class"], "#c2185b"))
        # Roboflow gives the box centre (x, y) plus width/height
        x0 = p["x"] - p["width"] / 2
        y0 = p["y"] - p["height"] / 2
        x1 = p["x"] + p["width"] / 2
        y1 = p["y"] + p["height"] / 2
        draw.rectangle([x0, y0, x1, y1], outline=color, width=line)

        label = f'{p["class"]} {p["confidence"]:.0%}'
        left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
        tw, th = right - left, bottom - top
        ty = max(0, y0 - th - 6)
        draw.rectangle([x0, ty, x0 + tw + 6, ty + th + 6], fill=color)
        draw.text((x0 + 3, ty + 3 - top), label, fill="white", font=font)
    return out


# ---------- UI ----------
st.set_page_config(page_title="Waterbird Counter", page_icon="🦆", layout="wide")
st.title("🦆 Waterbird Counter")
st.write(
    "Upload a photo of a Dutch pond or canal. The model finds mallards, coots "
    "and Egyptian geese and counts them per species, to support volunteer "
    "waterbird counts (SDG 15: Life on Land)."
)

if not API_KEY or not MODEL_ID:
    st.error(
        "ROBOFLOW_API_KEY or ROBOFLOW_MODEL_ID is missing. Create a .env file "
        "next to app.py with both values (see .env.example), then restart."
    )
    st.stop()

if "log" not in st.session_state:
    st.session_state.log = []

with st.sidebar:
    st.header("Settings")
    location = st.text_input("Location", placeholder="e.g. Haagse Bos, main pond")
    confidence = st.slider(
        "Confidence threshold", 0.10, 0.90, 0.50, 0.05,
        help="Higher = fewer false detections, but more birds missed.",
    )
    st.divider()
    st.subheader("Limitations")
    st.caption(
        "Trained on ~350 images from a few ponds in Den Haag plus scraped photos. "
        "Only knows 3 species: any other bird may be counted as one of them. "
        "Coot is the least reliable class. Distant, overlapping or hidden birds "
        "can be missed. Always check counts by eye before reporting them."
    )

uploaded = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

if uploaded is None:
    st.info("Upload a photo to start counting.")
else:
    img = prepare_image(uploaded)

    with st.spinner("Counting birds..."):
        try:
            preds = predict(to_jpeg_bytes(img), confidence)
        except requests.RequestException as e:
            st.error(f"Could not reach the Roboflow model. Check your API key, model ID and internet. Details: {e}")
            st.stop()

    preds = [p for p in preds if p["confidence"] >= confidence]
    counts = {name: sum(p["class"] == name for p in preds) for name in CLASSES}

    col_img, col_counts = st.columns([3, 1])
    with col_img:
        st.image(draw_boxes(img, preds), caption=f"{len(preds)} birds detected")

    with col_counts:
        st.subheader("Counts")
        for key, (display, _) in CLASSES.items():
            st.metric(display, counts[key])
        st.metric("Total", sum(counts.values()))

        if counts["egyptian_goose"] > 0:
            st.warning("Egyptian goose is an exotic species in the Netherlands. Consider reporting it.")

        if st.button("Add to count log", type="primary"):
            st.session_state.log.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "location": location or "unknown",
                "photo": uploaded.name,
                **counts,
            })
            st.success("Added to log.")

if st.session_state.log:
    st.subheader("Count log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, hide_index=True)
    st.download_button(
        "Download log as CSV",
        df.to_csv(index=False),
        file_name="waterbird_counts.csv",
        mime="text/csv",
    )