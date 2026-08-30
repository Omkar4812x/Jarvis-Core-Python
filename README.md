# 🤖 Jarvis Core Python Engine

> **High-performance Python virtual assistant core integrating speech recognition, LLM intelligence, persistent memory, YouTube automation, and desktop controls.**

---

## ✨ Features

- 🎙️ **Voice Command & Audio Manager** (`voice_manager.py`)
  - Real-time microphone listening, ambient noise suppression, and gTTS / pyttsx3 audio playback.
- 🧠 **LLM Brain & Memory Systems** (`llm.py`, `memory.py`, `memory_brain.py`)
  - Connects to LLM endpoints with persistent conversation history and user memory retention.
- ⚙️ **System Automation & Media Control** (`automation.py`, `youtube_helper.py`)
  - Automates desktop app opening, system settings, web searching, and YouTube video playback.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Speech**: `SpeechRecognition`, `gTTS`, `pygame`, `pyttsx3`
- **Automation**: `pyautogui`, `psutil`, `yt-dlp`
- **AI Gateway**: OpenAI Python SDK, `python-dotenv`

---

## 🚀 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Omkar4812x/Jarvis-Core-Python.git
   cd Jarvis-Core-Python
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run Jarvis Core Engine**:
   ```bash
   python main.py
   ```

---

## 📄 License

Distributed under the MIT License.
