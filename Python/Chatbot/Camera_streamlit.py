import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import cv2
import numpy as np
import time

def apply_filter(frame, filter_name):
    if filter_name == "Gråskala":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif filter_name == "Sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        frame = cv2.transform(frame, kernel)
        frame = np.clip(frame, 0, 255).astype(np.uint8)
    elif filter_name == "Invert":
        frame = cv2.bitwise_not(frame)
    elif filter_name == "Blur":
        frame = cv2.GaussianBlur(frame, (15, 15), 0)
    elif filter_name == "Canny Edge":
        edges = cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 100, 200)
        frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif filter_name == "Cartoonifier":
        color = cv2.bilateralFilter(frame, 9, 250, 250)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(blur, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(color, edges_colored)
    return frame

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.filter_name = "Ingen"
        self.recording = False
        self.frames = []
        self.start_time = None
        self.latest_frame = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = apply_filter(img, self.filter_name)
        self.latest_frame = img.copy()

        if self.recording:
            if self.start_time is None:
                self.start_time = time.time()
            elapsed = time.time() - self.start_time
            if elapsed <= 20:
                self.frames.append(img.copy())
            else:
                self.recording = False
                self.start_time = None
                self.save_video()
                self.frames = []

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def save_video(self):
        if not self.frames:
            return
        height, width, _ = self.frames[0].shape
        out = cv2.VideoWriter(f"video_{int(time.time())}.avi",
                              cv2.VideoWriter_fourcc(*'XVID'), 20.0, (width, height))
        for f in self.frames:
            out.write(f)
        out.release()
        st.success("🎥 Video sparad!")

    def save_image(self):
        if self.latest_frame is not None:
            filename = f"snapshot_{int(time.time())}.png"
            cv2.imwrite(filename, self.latest_frame)
            st.success(f"📸 Bild sparad som {filename}")
        else:
            st.warning("Ingen bild tillgänglig än.")

# === Streamlit UI ===
st.title("📷 Live Kamera med Filter, Foto & 20s Videoinspelning")

filter_option = st.selectbox("Välj filter", ["Ingen", "Gråskala", "Sepia", "Invert", "Blur", "Canny Edge", "Cartoonifier"])

ctx = webrtc_streamer(key="live", video_processor_factory=VideoProcessor)

if ctx.video_processor:
    ctx.video_processor.filter_name = filter_option

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎥 Spela in 20 sek"):
            ctx.video_processor.recording = True
            ctx.video_processor.frames = []
            ctx.video_processor.start_time = None
            st.info("🎬 Inspelning startad (max 20s) ...")

    with col2:
        if st.button("📸 Ta bild"):
            ctx.video_processor.save_image()
