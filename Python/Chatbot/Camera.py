import cv2
import time
import threading
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam App")
        self.root.geometry("700x700")

        self.video_label = Label(self.root)
        self.video_label.pack(pady=10)

        # Resolution Dropdown
        self.resolution_var = StringVar(value="640x480")
        OptionMenu(self.root, self.resolution_var, "320x240", "640x480", "1280x720").pack()

        # Filter Dropdown
        self.filter_var = StringVar(value="Ingen")
        OptionMenu(self.root, self.filter_var,
           "Ingen", "Gråskala", "Sepia", "Invert", "Blur", "Canny Edge", "Cartoonifier").pack()

        self.btn_start = Button(self.root, text="Starta Kamera", command=self.start_camera)
        self.btn_start.pack(pady=5)

        self.btn_stop = Button(self.root, text="Stoppa Kamera", command=self.stop_camera, state=DISABLED)
        self.btn_stop.pack(pady=5)

        self.btn_snapshot = Button(self.root, text="Ta Bild (PNG)", command=self.take_snapshot, state=DISABLED)
        self.btn_snapshot.pack(pady=5)

        self.btn_record = Button(self.root, text="Spela in 20s Video", command=self.record_video, state=DISABLED)
        self.btn_record.pack(pady=5)

        self.cap = None
        self.running = False
        self.frame = None
        self.width, self.height = 640, 480

    def start_camera(self):
        resolution = self.resolution_var.get()
        self.width, self.height = map(int, resolution.split("x"))

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.running = True
        self.update_frame()

        self.btn_start.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.btn_snapshot.config(state=NORMAL)
        self.btn_record.config(state=NORMAL)

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image='')
        self.btn_start.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self.btn_snapshot.config(state=DISABLED)
        self.btn_record.config(state=DISABLED)

    def apply_filter(self, frame):
        filter_name = self.filter_var.get()

        if filter_name == "Gråskala":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        elif filter_name == "Sepia":
            sepia_kernel = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            frame = cv2.transform(frame, sepia_kernel)
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        elif filter_name == "Invert":
            frame = cv2.bitwise_not(frame)

        elif filter_name == "Blur":
            frame = cv2.GaussianBlur(frame, (15, 15), 0)

        elif filter_name == "Canny Edge":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif filter_name == "Cartoonifier":
            # Steg 1: Bilateral filter för att jämna ut färger
            color = cv2.bilateralFilter(frame, 9, 250, 250)
            # Steg 2: Edge detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.medianBlur(gray, 7)
            edges = cv2.adaptiveThreshold(blur, 255,
                                        cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, 9, 9)
            # Steg 3: Kombinera färger och kanter
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            frame = cv2.bitwise_and(color, edges_colored)

        return frame


    def update_frame(self):
        if self.running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                frame = self.apply_filter(frame)
                self.frame = frame
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        self.root.after(30, self.update_frame)

    def take_snapshot(self):
        if self.frame is not None:
            filtered = self.apply_filter(self.frame.copy())  # Använd aktuell filterinställning
            filename = f"snapshot_{int(time.time())}.png"
            cv2.imwrite(filename, filtered)
            print(f"Bild sparad som {filename}")


    def record_video(self):
        if self.cap and self.running:
            filename = f"video_{int(time.time())}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filename, fourcc, 20.0, (self.width, self.height))
            print(f"Spelar in video till {filename} i 20 sekunder...")

            start_time = time.time()

            def record():
                while time.time() - start_time < 20 and self.running:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    frame = cv2.resize(frame, (self.width, self.height))
                    frame = self.apply_filter(frame)
                    out.write(frame)
                    time.sleep(0.05)
                out.release()
                print("Inspelning klar.")

            threading.Thread(target=record).start()

if __name__ == "__main__":
    root = Tk()
    app = WebcamApp(root)
    root.mainloop()
