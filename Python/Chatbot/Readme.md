# 📷 Kamera-app i Streamlit med filter, bild & video

Detta projekt är en webbaserad kameraapplikation byggd med [Streamlit](https://streamlit.io) och [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc). Appen erbjuder:

- ✅ Livekamera direkt i webbläsaren
- 🎨 Realtidsfilter (gråskala, sepia, cartoonifier, m.fl.)
- 📸 Ta snapshot som `.png`
- 🎥 Spela in video i 20 sekunder

## 🛠 Installation

Om du vill köra det lokalt:

```bash
git clone https://github.com/ditt-användarnamn/kamera-app-streamlit.git
cd kamera-app-streamlit
pip install -r requirements.txt
streamlit run Camera_app.py
