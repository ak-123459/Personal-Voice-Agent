# 🤖 AI Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange.svg)](https://groq.com)

A real-time AI Voice Assistant powered by **Groq's Llama 3.3 70B** with voice streaming and text-to-speech capabilities. Talk to your AI assistant naturally using voice commands or text input!

![AI Voice Assistant Demo](https://via.placeholder.com/800x400/4A90E2/FFFFFF?text=AI+Voice+Assistant+Demo)

## 🚩 Important Note

🎤 This project works **only in Google Chrome** due to microphone permission limitations in other browsers.


## ✨ Features

- 🎤 **Real-time Voice Input** - Record and transcribe speech with automatic processing
- 🔊 **Text-to-Speech Output** - AI responses converted to natural speech
- 🧠 **Powered by Groq LLM** - Fast inference using Llama 3.3 70B model
- ⚡ **WebSocket Communication** - Real-time bidirectional communication
- 🎵 **Music Playback** - Search and play music via YouTube
- ⏰ **Smart Reminders** - Set and manage time-based reminders
- 📧 **Message Management** - Send and retrieve messages
- 🕐 **Time & Date Queries** - Get current time and date information
- 💬 **Natural Conversation** - Context-aware responses with conversation history

## 🎥 Demo

```
User: "Remind me to call mom in 10 minutes"
AI: "I've set a reminder for you at 2:45 PM to call mom."

User: "Play some relaxing music"
AI: "Opening YouTube to play relaxing music for you."

User: "What time is it?"
AI: "The current time is 2:35 PM."
```

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **Groq API Key** ([Get one free](https://console.groq.com))
- Modern web browser (Chrome/Edge recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/ak-123459/Personal-Voice-Agent.git
cd Personal-Voice-Agent
```

### 2. Set Up Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
``


### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **Important:** Never commit your `.env` file! It's already in `.gitignore`.

Get your Groq API key: [https://console.groq.com/keys](https://console.groq.com/keys)

## 🎮 Usage

### Run the main.py

```bash
python main.py
```

Expected output:
```
============================================================
AI Voice Assistant WebSocket Server
============================================================
Server starting on ws://localhost:8765
Make sure GROQ_API_KEY is set in environment variables
============================================================
```

### Open the Frontend

**Option 1: Direct File Open**
- Double-click `index.html`
- Or right-click → Open with → Your Browser

**Option 2: Local Server (Recommended)**
```bash
# Python
python -m http.server 8000

# Node.js
npx http-server

# Then open: http://localhost:8000
```

### Using the Assistant

#### Voice Commands
1. Click the **🎤 Microphone** button
2. Speak your command (auto-stops after 5 seconds)
3. Wait for transcription and AI response
4. Listen to the audio response

#### Text Commands
1. Type in the input box at the bottom
2. Press **Enter** or click **Send**
3. View AI response in chat

## 📚 API Reference

### Supported Commands

#### Reminders
```
"Remind me to call John in 15 minutes"
"Set a reminder for tomorrow's meeting"
"Show me my reminders"
"Delete reminder 1"
```

#### Messages
```
"Send a message to Sarah about the project"
"Send a note saying I'll be late"
"Show all my messages"
```

#### Music
```
"Play some jazz music"
"Play Bohemian Rhapsody by Queen"
"Play workout music"
```

#### Time & Date
```
"What time is it?"
"What's today's date?"
```

#### General Questions
```
"What is artificial intelligence?"
"Explain quantum computing"
"How do I make pasta?"
```

### WebSocket Message Format

**Client → Server:**
```json
{
  "type": "audio",
  "audio": "base64_encoded_audio_data"
}
```

```json
{
  "type": "text",
  "text": "Your message here"
}
```

**Server → Client:**
```json
{
  "type": "response",
  "data": {
    "status": "success",
    "message": "AI response text",
    "function_called": "function_name"
  }
}
```

```json
{
  "type": "audio_response",
  "audio": "base64_encoded_audio_data"
}
```

## ⚙️ Configuration

### Adjust Speech Recognition Sensitivity

Edit `main.py`:
```python
def __init__(self):
    self.recognizer = sr.Recognizer()
    self.recognizer.energy_threshold = 4000  # Lower = more sensitive
    self.recognizer.dynamic_energy_threshold = True
```

### Change Recording Duration

Edit `index.html`:
```javascript
setTimeout(() => {
    stopRecording();
}, 5000);  // 5000ms = 5 seconds
```

### Modify AI Model

Edit `main.py`:
```python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",  # Change model
    temperature=0.7,  # Adjust creativity (0.0-1.0)
    # ...
)
```

### Available Groq Models
- `llama-3.3-70b-versatile` (recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>❌ Error: <code>name 'tempfile' is not defined</code></b></summary>

**Solution:** Add import at top of `main.py`:
```python
import tempfile
```
</details>


<summary><b>🎤 Audio Not Recognized</b></summary>

**Solutions:**
- Grant microphone permissions in browser
- Check microphone in system settings
- Reduce background noise
- Speak closer to microphone
- Adjust `energy_threshold` (lower = more sensitive)
</details>

<details>
<summary><b>🔌 WebSocket Connection Failed</b></summary>

**Solutions:**
- Ensure main is running: `python main.py`
- Check port 8765 is available
- Disable firewall temporarily
- Check browser console (F12) for errors
</details>

<details>
<summary><b>🔇 No Audio Response</b></summary>

**Solutions:**
- Check browser console for errors
- Allow audio autoplay in browser settings
- Verify speakers/headphones connected
- Check system volume
</details>

### Debug Mode

Enable detailed logging in `main.py` by checking console output:

```
[DEBUG] Starting audio processing...
[DEBUG] Decoded 45632 bytes of audio
[DEBUG] Using temp file: C:\Temp\tmp8j5k2l.wav
[DEBUG] Attempting to load as WebM...
[DEBUG] Converting audio format...
[DEBUG] Starting speech recognition...
[DEBUG] Recognition successful: Hello world
```

## 🧪 Testing

### Test Individual Functions

```bash
# Test reminder
python -c "from main import set_reminder; print(set_reminder('Test', 5))"

# Test time
python -c "from main import get_current_time; print(get_current_time())"

# Test message
python -c "from main import send_message; print(send_message('Hello'))"
```

### Test WebSocket Connection

1. Start main: `python main.py`
2. Open browser console (F12)
3. Check for connection logs
4. Send test message

## 📊 Performance

- **Groq Free Tier Limits:**
  - 30 requests per minute
  - 14,400 tokens per minute
  
- **Audio Processing:**
  - Transcription: ~1-2 seconds
  - TTS Generation: ~0.5-1 second
  - Total latency: ~2-4 seconds

## 🔐 Security

⚠️ **Important Security Notes:**

- ✅ Never commit `.env` file
- ✅ Keep API keys private
- ✅ Use `.env.example` for documentation
- ✅ Rotate keys if exposed
- ⚠️ This is for local development only
- ⚠️ Add authentication for production use
- ⚠️ Use HTTPS in production

### Recommended `.gitignore`

```gitignore
# Environment
.env
.venv/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Audio files
*.wav
*.mp3
tts_output.wav

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## 🚀 Advanced Features

### Using Groq Whisper for Better Transcription

Replace Google Speech Recognition with Groq Whisper in `main.py`:

```python
def process_audio(self, base64_audio: str) -> str:
    tmp_filename = None
    try:
        audio_bytes = base64.b64decode(base64_audio)
        
        # Save as temporary file
        tmp_filename = tempfile.mktemp(suffix=".webm")
        with open(tmp_filename, "wb") as f:
            f.write(audio_bytes)
        
        # Use Groq Whisper
        with open(tmp_filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                response_format="text"
            )
        
        return transcription
    except Exception as e:
        return f"[ERROR] {e}"
    finally:
        if tmp_filename and os.path.exists(tmp_filename):
            os.remove(tmp_filename)
```

### Custom Functions

Add new functions to `tools` array and `function_map` in `main.py`:

```python
# Define tool
{
    "type": "function",
    "function": {
        "name": "your_function",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
}

# Implement function
def your_function(param1: str) -> Dict:
    # Your logic here
    return {
        "success": True,
        "message": "Result message",
        "data": {}
    }

# Add to mapping
function_map["your_function"] = your_function
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python
- Add docstrings to functions
- Test your changes thoroughly
- Update documentation as needed

## 📝 Changelog

### Version 1.0.0 (Current)
- ✨ Initial release
- 🎤 Voice input support
- 🔊 Text-to-speech output
- ⏰ Reminder system
- 🎵 Music playback
- 📧 Message management

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Custom wake word detection
- [ ] Integration with calendar apps
- [ ] Email sending functionality
- [ ] Weather information
- [ ] News summaries
- [ ] Mobile app version

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com) - For lightning-fast LLM inference
- [Google Speech Recognition](https://cloud.google.com/speech-to-text) - For speech-to-text API
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - For text-to-speech
- [pydub](https://github.com/jiaaro/pydub) - For audio processing
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) - For audio transcription
- Python & JavaScript communities

## 📞 Support

Need help? Here's how to get support:

- 📖 **Documentation:** Check this README
- 🐛 **Bug Reports:** [Open an issue](https://github.com/ak-123459/Personal-Voice-Agent/issues)
- 💡 **Feature Requests:** [Open an issue](https://github.com/ak-123459/Personal-Voice-Agent/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/ak-123459/Personal-Voice-Agent/discussions)

## 📧 Contact

**Your Name** - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/ak-123459/Personal-Voice-Agent](https://github.com/ak-123459/Personal-Voice-Agent)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [Your Name](https://github.com/ak-123459)

[⬆ Back to Top](#-ai-voice-assistant)

</div>
