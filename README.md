# 🎙 Real-Time English to Telugu Translator

## 🚀 Features
- Real-time speech-to-text
- English to Telugu translation
- Live audio playback
- WebSocket-based streaming

## 🛠 Tech Stack
- FastAPI
- WebSockets
- JavaScript
- HTML/CSS
- OpenAI / Whisper

## 📂 Project Structure

bash
real-time-english-telugu-translator/
│
├── app/
│   ├── backend.py              # FastAPI backend (WebSocket + API logic)
│   ├── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html              # Frontend UI
│
├── notebooks/
│   ├── English_to_Telugu_text.ipynb
│   ├── Test.ipynb
│
├── audio_samples/
│   ├── sample_input.wav
│   ├── sample_output.mp3
│
├── README.md
└── .gitignore

## ▶ How to Run

### 1. Backend
cd app
uvicorn backend:app --reload --port 8000

### 2. Frontend
Open frontend/index.html in browser

## 📸 Demo
(Add screenshots)

## 👨‍💻 Author
Your Name
