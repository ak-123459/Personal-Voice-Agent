🤖 AI Voice Assistant
A real-time AI Voice Assistant powered by Groq LLM with voice streaming and TTS capabilities. Supports voice input, text input, and audio responses through a WebSocket server.

✨ Features
Real-time voice recording via microphone
Speech-to-text transcription using Google Speech Recognition
Text-to-speech (TTS) responses using pyttsx3
AI-powered conversation using Groq's Llama 3.3 70B
Function call support for commands:
⏰ Set and manage reminders
📧 Send messages
🎵 Play music via YouTube
🕐 Get current time and date
❓ Answer general questions
Interactive chat UI with status indicators
Real-time WebSocket communication between frontend and backend
🛠️ Technologies Used
Frontend:

HTML5
CSS3
Vanilla JavaScript
WebSocket API
MediaRecorder API
Backend:

Python 3.10+
asyncio for async operations
websockets for real-time communication
Groq API for AI processing
speech_recognition for STT
pyttsx3 for TTS
pydub for audio processing
External Tools:

FFmpeg (required for audio format conversion)
📁 Project Structure
.
├── index.html          # Frontend interface
├── server.py           # Python WebSocket server
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── README.md          # Documentation
└── .venv/             # Python virtual environment
📋 Prerequisites
Python 3.10 or higher
Web browser (Chrome/Edge recommended for best audio support)
Groq API Key (Get one here)
FFmpeg installed and added to system PATH
🚀 Setup Instructions
1. Clone the Repository
bash
git clone <repository-url>
cd <project-folder>
2. Setup Python Virtual Environment
bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
3. Install Python Dependencies
bash
pip install -r requirements.txt
requirements.txt contents:

txt
websockets==12.0
SpeechRecognition==3.10.0
pydub==0.25.1
pyttsx3==2.90
groq==0.4.1
python-dotenv==1.0.0
4. Install FFmpeg
FFmpeg is required for audio format conversion.

Windows:

bash
# Using Chocolatey
choco install ffmpeg

# Or download manually from:
# https://ffmpeg.org/download.html
# Extract and add bin folder to system PATH
Linux:

bash
sudo apt update
sudo apt install ffmpeg
macOS:

bash
brew install ffmpeg
Verify installation:

bash
ffmpeg -version
5. Configure Environment Variables
Create a .env file in the project root:

env
GROQ_API_KEY=your_groq_api_key_here
Get your Groq API key from: https://console.groq.com/keys

6. Run the WebSocket Server
bash
python server.py
You should see:

============================================================
AI Voice Assistant WebSocket Server
============================================================
Server starting on ws://localhost:8765
Make sure GROQ_API_KEY is set in environment variables
============================================================
🌐 Frontend Setup
Option 1: Open Directly in Browser
bash
# Simply open index.html in your browser
# Double-click the file or right-click → Open with → Browser
Option 2: Use Local Server (Recommended)
bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Then open: http://localhost:8000
🎯 How to Use
Voice Input
bash
1. Click the 🎤 Microphone button
2. Speak your command (recording stops automatically after 5 seconds)
3. Wait for transcription to appear
4. AI will respond with text and audio
Text Input
bash
1. Type your message in the input box at the bottom
2. Press Enter or click Send
3. AI will respond with text and audio
Supported Commands
Reminders
bash
"Remind me to call mom in 10 minutes"
"Set a reminder for tomorrow's meeting"
"Show me my reminders"
"Delete reminder number 1"
Messages
bash
"Send a message to John about the meeting"
"Send a note saying I'll be late"
"Show me all messages"
Music
bash
"Play some jazz music"
"Play Bohemian Rhapsody"
"Play relaxing music"
Time & Date
bash
"What time is it?"
"What's today's date?"
General Questions
bash
"What is machine learning?"
"Tell me about Python programming"
"How does a combustion engine work?"
🔧 Configuration Options
Adjust Speech Recognition Sensitivity
In server.py, modify the AIVoiceAssistant class:

python
def __init__(self):
    self.recognizer = sr.Recognizer()
    self.recognizer.energy_threshold = 4000  # Adjust this value
    self.recognizer.dynamic_energy_threshold = True
Change Recording Duration
In index.html, find the startRecording() function:

javascript
setTimeout(() => {
    stopRecording();
}, 5000);  // Change 5000 to desired milliseconds
Modify AI Model
In server.py, change the model in process_command():

python
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",  # Change model here
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=0.7  # Adjust creativity (0.0 - 1.0)
)
🐛 Troubleshooting
Issue: name 'tempfile' is not defined
bash
Solution: Ensure import tempfile is at the top of server.py
Issue: Couldn't find ffmpeg or avconv
bash
Solution:
1. Install FFmpeg (see installation instructions above)
2. Verify it's in your system PATH: ffmpeg -version
3. Restart your terminal/command prompt
Issue: [WinError 2] The system cannot find the file specified
bash
Solution: This usually means FFmpeg is not in PATH
1. Add FFmpeg bin folder to system environment variables
2. Restart terminal
3. Test: ffmpeg -version
Issue: Audio not recognized
bash
Solutions:
- Ensure microphone permissions are granted in browser
- Check microphone is working in system settings
- Try speaking closer to microphone
- Reduce background noise
- Adjust energy_threshold in code (default: 4000)
Issue: WebSocket connection failed
bash
Solutions:
- Ensure server is running: python server.py
- Check if port 8765 is available
- Verify firewall isn't blocking connections
- Check browser console for detailed error messages
Issue: No audio response playing
bash
Solutions:
- Check browser console for errors
- Ensure audio playback is not blocked by browser
- Verify speaker/headphones are connected
- Check browser audio settings
Issue: AI not calling functions
bash
Solutions:
- Verify your command is clear and specific
- Check server logs for error messages
- Ensure Groq API key is valid
- Try rephrasing your command
📊 API Rate Limits
Groq Free Tier:

bash
- 30 requests per minute
- 14,400 tokens per minute
If you exceed limits, you'll see rate limit errors in the console.

🔒 Security Notes
⚠️ Important Security Considerations:

bash
1. Never commit .env file - Add to .gitignore
2. API Key Protection - Keep your Groq API key private
3. Local Development - This setup is for local development only
4. Production Deployment - Add authentication and HTTPS for production
Recommended .gitignore:

gitignore
.env
.venv/
__pycache__/
*.pyc
*.wav
tts_output.wav
🚀 Advanced Features
Using Groq Whisper for Transcription
For better transcription accuracy, replace Google Speech Recognition with Groq Whisper:

python
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
Background Reminder System
The server includes a background task that checks reminders every 10 seconds and sends notifications when they're due.

👨‍💻 Development
Running in Development Mode
bash
# Start server with debug logging
python server.py

# Open browser console for frontend debugging
# Press F12 in browser
Testing
Test the assistant with various commands:

bash
# Test reminder function
python -c "from server import *; print(set_reminder('Test', 5))"

# Test message function
python -c "from server import *; print(send_message('Hello World'))"

# Test time function
python -c "from server import *; print(get_current_time())"
Debug Mode
Enable detailed logging by checking server console output:

bash
[CONNECT] Client connected: ('127.0.0.1', 52841)
[INFO] Initialized conversation history
[RECEIVED] Raw message: {...}
[PARSE] JSON parsed successfully: type=audio
[DEBUG] Starting audio processing...
[TRANSCRIPTION] Recognized text: Hello
[AI RESPONSE] Hi! How can I help you?
📝 Notes
bash
- Audio recording maximum length is 5 seconds by default
- The frontend converts audio to Base64 before sending to server
- Backend saves temporary audio files for processing and deletes them after transcription
- AI responses can include TTS audio which plays automatically in the browser
- Conversation history is maintained per WebSocket connection
- History is limited to last 20 messages to manage memory
🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

bash
1. Fork the repository
2. Create your feature branch: git checkout -b feature/AmazingFeature
3. Commit your changes: git commit -m 'Add some AmazingFeature'
4. Push to the branch: git push origin feature/AmazingFeature
5. Open a Pull Request
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Groq for fast LLM inference
Google for Speech Recognition API
SpeechRecognition library
pyttsx3 for TTS
pydub for audio processing
WebSocket protocol for real-time communication
Python community for excellent libraries
📞 Support
If you encounter any issues:

bash
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Check browser console for frontend errors (F12)
4. Create an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - System information (OS, Python version, browser)
Common Support Channels:

bash
- GitHub Issues: For bug reports and feature requests
- Documentation: Check this README for solutions
- Server Logs: Review console output for detailed errors
Made with ❤️ using Python and JavaScript

