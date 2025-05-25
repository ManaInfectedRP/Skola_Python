import sys
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageChops
import time
import tempfile
from moviepy.editor import ImageSequenceClip

# --- Filterfunktioner utan cv2 ---
def apply_filter(frame, filter_name):
    img = Image.fromarray(frame[:, :, ::-1])  # BGR->RGB

    if filter_name == "Gråskala":
        img = ImageOps.grayscale(img).convert("RGB")
    elif filter_name == "Sepia":
        sepia_img = np.array(img)
        tr = [0.393, 0.769, 0.189]
        tg = [0.349, 0.686, 0.168]
        tb = [0.272, 0.534, 0.131]
        r = sepia_img[:, :, 0]
        g = sepia_img[:, :, 1]
        b = sepia_img[:, :, 2]
        sr = (r * tr[0] + g * tr[1] + b * tr[2])
        sg = (r * tg[0] + g * tg[1] + b * tg[2])
        sb = (r * tb[0] + g * tb[1] + b * tb[2])
        sepia_img[:, :, 0] = np.clip(sr, 0, 255)
        sepia_img[:, :, 1] = np.clip(sg, 0, 255)
        sepia_img[:, :, 2] = np.clip(sb, 0, 255)
        img = Image.fromarray(sepia_img.astype(np.uint8))
    elif filter_name == "Invert":
        img = ImageOps.invert(img)
    elif filter_name == "Blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=5))
    elif filter_name == "Canny Edge":
        img_gray = ImageOps.grayscale(img)
        img = img_gray.filter(ImageFilter.FIND_EDGES).convert("RGB")
    elif filter_name == "Cartoonifier":
        img = img.filter(ImageFilter.MedianFilter(size=5))
        img = ImageOps.posterize(img, bits=3)
        edges = img.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda x: 255 if x > 50 else 0)
        edges_rgb = edges.convert("RGB")
        img = ImageChops.subtract(img, edges_rgb)
    return np.array(img)[:, :, ::-1]  # RGB->BGR

# --- VideoProcessor ---
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.filter_name = "Ingen"
        self.recording = False
        self.frames = []
        self.start_time = None
        self.last_frame = None  # för bildspara

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        filtered_img = apply_filter(img, self.filter_name)
        self.last_frame = filtered_img.copy()

        if self.recording:
            if self.start_time is None:
                self.start_time = time.time()
            elapsed = time.time() - self.start_time
            if elapsed <= 20:
                self.frames.append(filtered_img.copy())
            else:
                self.recording = False
                self.start_time = None
                self.save_video()
                self.frames = []

        return av.VideoFrame.from_ndarray(filtered_img, format="bgr24")

    def save_video(self):
        if not self.frames:
            return
        # moviepy kräver RGB
        rgb_frames = [frame[:, :, ::-1] for frame in self.frames]  # BGR->RGB
        clip = ImageSequenceClip(rgb_frames, fps=20)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        clip.write_videofile(tmp_file.name, codec="libx264", audio=False, verbose=False, logger=None)
        st.success(f"🎥 Video sparad: {tmp_file.name}")
        st.video(tmp_file.name)

    def save_image(self):
        if self.last_frame is None:
            st.warning("Ingen bild att spara ännu.")
            return
        img = Image.fromarray(self.last_frame[:, :, ::-1])  # BGR->RGB
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(tmp_file.name)
        st.success(f"📸 Bild sparad: {tmp_file.name}")
        st.image(img)

# --- Streamlit UI ---
st.title("📷 Live Kamera med Filter och Inspelning (utan cv2)")

filter_option = st.selectbox(
    "Välj filter",
    ["Ingen", "Gråskala", "Sepia", "Invert", "Blur", "Canny Edge", "Cartoonifier"],
)

ctx = webrtc_streamer(key="live", video_processor_factory=VideoProcessor)

if ctx.video_processor:
    ctx.video_processor.filter_name = filter_option

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎥 Spela in 20 sek"):
            ctx.video_processor.recording = True
            ctx.video_processor.frames = []
            ctx.video_processor.start_time = None
            st.info("🎬 Inspelning startad (max 20s)...")

    with col2:
        if st.button("📸 Ta bild"):
            ctx.video_processor.save_image()
