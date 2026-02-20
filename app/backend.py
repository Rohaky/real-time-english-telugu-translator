from fastapi import FastAPI, WebSocket
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
import base64
import threading
import queue
from pydub import AudioSegment
import io
import uvicorn

app = FastAPI()
model = whisper.load_model("small")  # small for faster real-time

audio_queue = queue.Queue()
conversation_history = ""  # keep all English text for display

# -------------------------------
# Processing thread
# -------------------------------
def process_audio_queue(ws):
    global conversation_history
    while True:
        audio_bytes = audio_queue.get()
        if audio_bytes is None:  # Stop signal
            break

        # Convert any format to WAV
        audio_bytes_io = io.BytesIO(audio_bytes)
        try:
            audio = AudioSegment.from_file(audio_bytes_io)  # auto-detect format
        except Exception as e:
            print("Failed to read audio chunk:", e)
            continue

        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio.export(temp_wav.name, format="wav")

        # Transcribe chunk
        try:
            result = model.transcribe(temp_wav.name, language='en')
            english_text = result["text"].strip()
        except Exception as e:
            print("Whisper transcription failed:", e)
            os.remove(temp_wav.name)
            continue

        os.remove(temp_wav.name)

        if english_text:
            # Append to conversation history for display
            conversation_history += " " + english_text
            print("Conversation so far (English):", conversation_history)

            # Translate only the latest chunk for TTS
            try:
                telugu_text = GoogleTranslator(source='en', target='te').translate(english_text)
            except Exception as e:
                print("Translation failed:", e)
                telugu_text = ""

            print("Latest chunk (Telugu):", telugu_text)

            # Convert latest chunk to TTS
            temp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            try:
                tts = gTTS(telugu_text, lang='te')
                tts.save(temp_mp3.name)
            except Exception as e:
                print("TTS generation failed:", e)
                os.remove(temp_mp3.name)
                continue

            # Send base64 audio and texts back
            with open(temp_mp3.name, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
            os.remove(temp_mp3.name)

            try:
                ws.send_json({
                    "english": conversation_history,
                    "telugu": telugu_text,
                    "audio": audio_b64
                })
            except:
                break  # WebSocket closed

# -------------------------------
# WebSocket endpoint
# -------------------------------
@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    # Start background thread for processing
    thread = threading.Thread(target=process_audio_queue, args=(websocket,), daemon=True)
    thread.start()

    try:
        while True:
            data = await websocket.receive_text()
            audio_bytes = base64.b64decode(data)
            audio_queue.put(audio_bytes)  # add chunk to queue
    except Exception as e:
        print("WebSocket closed:", e)
    finally:
        audio_queue.put(None)  # stop background thread
        thread.join()

# Run backend
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
