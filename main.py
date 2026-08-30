import os
import time
import re
import threading
import webbrowser
import speech_recognition as sr
from openai import OpenAI
import pyttsx3
import pygame
from flask import Flask, render_template, jsonify, request
import logging

# CUSTOM MODULES
import prompts
import memory
import automation
import youtube_helper

# ==========================================
#        SETTINGS
# ==========================================

GROQ_API_KEY = "YOUR_GROQ_API_KEY"
ROBOT_SPEED = 140

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app = Flask(__name__)

shared_data = {
    "status": "idle",
    "last_text": "",
    "mode": None,
    "running": True,
    "available_voices": [],
    "current_voice_id": None,
    "target_voice_id": None,
    "listening_lock": False
}

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# ==========================================
#        LOGIC
# ==========================================

def assistant_logic():
    engine = pyttsx3.init()
    engine.setProperty("rate", ROBOT_SPEED)

    voices = engine.getProperty("voices")
    voice_list = [{"id": v.id, "name": v.name.replace("Microsoft", "").strip()} for v in voices]
    shared_data["available_voices"] = voice_list

    default_id = voices[1].id if len(voices) > 1 else voices[0].id
    engine.setProperty("voice", default_id)
    shared_data["current_voice_id"] = default_id
    shared_data["target_voice_id"] = default_id

    def speak(text):
        shared_data["status"] = "speaking"
        shared_data["last_text"] = text
        print(f"Genius: {text}")

        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass

        shared_data["status"] = "listening"
        time.sleep(1)

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    # Wait for UI mode
    while shared_data["mode"] is None:
        if not shared_data["running"]:
            return
        time.sleep(0.4)

    active_prompt = prompts.get_prompt(shared_data["mode"])
    memory.init_memory(active_prompt)

    # Calibrate mic ONCE (important)
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

    speak("System Online. I am ready.")

    # ================= MAIN LOOP =================

    while shared_data["running"]:

        if shared_data["listening_lock"]:
            time.sleep(0.3)
            continue

        shared_data["listening_lock"] = True

        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source, phrase_time_limit=8)

            shared_data["status"] = "processing"

            try:
                text = recognizer.recognize_google(audio, language="en-IN")
            except sr.UnknownValueError:
                shared_data["listening_lock"] = False
                time.sleep(0.6)
                continue
            except sr.RequestError as e:
                print("Speech service error:", e)
                shared_data["listening_lock"] = False
                time.sleep(1)
                continue

            shared_data["last_text"] = text
            print(f"User: {text}")
            cmd = text.lower()

            shared_data["listening_lock"] = False
            time.sleep(0.5)

            if "stop" in cmd or "exit" in cmd:
                speak("Goodbye.")
                os._exit(0)

            # -------- CODING MODE --------
            if "build" in cmd or "code" in cmd or "create a website" in cmd:
                speak("I am building the premium project now.")
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": prompts.CODING_PROMPT},
                            {"role": "user", "content": text}
                        ],
                        temperature=0.1
                    )

                    code_content = completion.choices[0].message.content
                    match = re.search(r"(<!DOCTYPE html>[\s\S]*</html>)", code_content, re.I)
                    if match:
                        code_content = match.group(1)

                    result = automation.create_coding_project(code_content, "html")
                    speak(result)
                    continue
                except:
                    speak("I faced an error while creating the code.")
                    continue

            # -------- AUTOMATION --------
            app_res = automation.execute(text, None)
            if app_res:
                speak(app_res)
                continue

            # -------- CHAT --------
            memory.add_user_message(text)

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are Jarvis. Always reply in clear English only."}
                ] + memory.get_messages(),
                max_tokens=120
            )

            res = completion.choices[0].message.content
            memory.add_ai_message(res)
            speak(res)

        except Exception as e:
            print("Loop error:", e)
            shared_data["listening_lock"] = False
            time.sleep(1)

# ==========================================
#        ROUTES
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify(shared_data)

@app.route("/get_voices")
def get_voices():
    return jsonify(shared_data["available_voices"])

@app.route("/set_voice", methods=["POST"])
def set_voice():
    data = request.json
    shared_data["target_voice_id"] = data["voice_id"]
    return "OK"

@app.route("/start_mode/<mode>")
def start_mode(mode):
    shared_data["mode"] = mode
    return "OK"

@app.route("/shutdown")
def shutdown():
    shared_data["running"] = False
    threading.Thread(target=lambda: (time.sleep(1), os._exit(0))).start()
    return "Bye"

# ==========================================
#        START
# ==========================================

if __name__ == "__main__":
    t = threading.Thread(target=assistant_logic, daemon=True)
    t.start()
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000)
