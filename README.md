## 🔣 WeCantTalk Bot — Kokoro TTS Discord Voice Bot

A Discord bot that joins your voice channel and speaks using Kokoro TTS via a local FastAPI server.

---

### ✅ Features
- `!speak [message]` — Speak using the default voice
- `!speakwith [voice] [message]` — Specify a voice to speak
- `!listvoices` — List all available voices
- `!stop` — Stop current playback
- `!raid [channel_id] [message]` — Speak in a specified voice channel
- Console support — Type messages directly into your terminal
- Smart mention replacement (`@user` → display name)

---

### ⚙️ Requirements

1. **Python 3.8+**
2. **A running Kokoro-FastAPI container**
   - We went with port 8880 so the code should match your settings, follow instructions here:  https://github.com/remsky/Kokoro-FastAPI
3. **FFmpeg installed and accessible in PATH**
4. A Discord Bot Token

---

### 📦 Installation

1. **Clone this repository or copy the `WeCantTalk.py` file**

2. **Set up a virtual environment** _(optional but recommended)_:  
   ```bash
   python -m venv venv
   venv\Scripts\activate   # on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install discord.py requests python-dotenv
   ```

4. **Create a `.env` file** in the same folder as `WeCantTalk.py`:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   KOKORO_API_URL=http://localhost:8880/v1/audio/speech
   VOICE_ID=am_adam
   MODEL_ID=kokoro
   ```

5. **Ensure FFmpeg is installed** and added to your system PATH:
   - [Download FFmpeg](https://ffmpeg.org/download.html)
   - Test with: `ffmpeg -version` in terminal

6. **Start your Kokoro-FastAPI Docker container**:
   ```bash
   docker run -d -p 8880:8000 remsky/kokoro-fastapi
   ```

---

### ▶️ Run the bot

```bash
python WeCantTalk.py
```

You’ll see a `Console>` prompt. You can type directly there or interact via Discord.

---

### 💬 Example Usage

- In Discord:
  - `!speak Hello friends`
  - `!speakwith af_heart Good evening`
  - `!listvoices`
  - `!raid 123456789012345678 Hello from WeCantTalk`
  - `!stop`

- In Terminal:
  - `Hello world`
  - `speakwith uk_london Cheers from the console`

---

### 🧠 Troubleshooting

- Bot joins voice but doesn’t speak? Ensure FFmpeg is correctly installed and audio is returned from the API.
- Getting `400 Bad Request`? Confirm your voice name is valid with `!listvoices`.
- No audio played? Make sure your Kokoro TTS container is running and reachable.

---
