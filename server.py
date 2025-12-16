import asyncio
import json
import base64
import io
import os
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import websockets
import speech_recognition as sr
import pyttsx3
import threading
import tempfile  # ✅ FIXED: Added missing import
from pydub import AudioSegment
from openai import OpenAI
import wave
from groq import Groq
from dotenv import load_dotenv

# Load environment variables - THIS MUST BE BEFORE creating the client
load_dotenv()

# Initialize OpenAI client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

tts_engine = pyttsx3.init()

# Initialize text-to-speech engine
tts_lock = threading.Lock()


def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech using pyttsx3
    Returns WAV audio bytes (WebSocket-safe)
    """
    try:
        with tts_lock:
            buffer = io.BytesIO()

            # Save speech to temporary WAV file
            temp_file = "tts_output.wav"
            tts_engine.save_to_file(text, temp_file)
            tts_engine.runAndWait()

            # Read WAV bytes
            with open(temp_file, "rb") as f:
                audio_bytes = f.read()

            os.remove(temp_file)
            return audio_bytes

    except Exception as e:
        print(f"pyttsx3 TTS Error: {e}")
        return b""


# Data storage
reminders: List[Dict] = []
messages: List[Dict] = []
music_queue: List[Dict] = []
conversation_history: List[Dict] = []

# Define tools for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder for the user at a specific time or after a duration",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_text": {
                        "type": "string",
                        "description": "The content of the reminder"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration in minutes from now (default: 5)",
                        "default": 5
                    }
                },
                "required": ["reminder_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message or note",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "The recipient of the message"
                    },
                    "content": {
                        "type": "string",
                        "description": "The message content"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play music based on genre, mood, artist, or song name",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Genre, mood, artist, or song name to play"
                    },
                    "shuffle": {
                        "type": "boolean",
                        "description": "Whether to shuffle the playlist",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_reminders",
            "description": "Get all active reminders",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_messages",
            "description": "Get all sent messages",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reminder",
            "description": "Delete a specific reminder by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_id": {
                        "type": "integer",
                        "description": "The ID of the reminder to delete"
                    }
                },
                "required": ["reminder_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current date",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]



# Function implementations
def set_reminder(reminder_text: str, duration_minutes: int = 5) -> Dict:
    """Set a reminder"""
    reminder_time = datetime.now() + timedelta(minutes=duration_minutes)
    reminder = {
        "id": len(reminders) + 1,
        "text": reminder_text,
        "time": reminder_time.strftime("%Y-%m-%d %H:%M"),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True
    }
    reminders.append(reminder)
    return {
        "success": True,
        "message": f"Reminder set for {reminder_time.strftime('%I:%M %p')}",
        "data": reminder
    }


def send_message(content: str, recipient: str = "default") -> Dict:
    """Send a message"""
    message = {
        "id": len(messages) + 1,
        "recipient": recipient,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    return {
        "success": True,
        "message": f"Message sent to {recipient}",
        "data": message
    }


def play_music(query: str, shuffle: bool = False) -> dict:
    yt_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={yt_query}"
    webbrowser.open(url)

    return {
        "success": True,
        "message": f"Opening YouTube for {query}",
        "data": {
            "platform": "YouTube",
            "query": query
        }
    }


def get_reminders() -> Dict:
    """Get all reminders"""
    active_reminders = [r for r in reminders if r.get("active", True)]
    return {
        "success": True,
        "message": f"You have {len(active_reminders)} active reminder(s)",
        "data": active_reminders
    }


def get_messages() -> Dict:
    """Get all messages"""
    return {
        "success": True,
        "message": f"You have {len(messages)} message(s)",
        "data": messages
    }


def delete_reminder(reminder_id: int) -> Dict:
    """Delete a reminder"""
    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["active"] = False
            return {
                "success": True,
                "message": f"Reminder {reminder_id} deleted",
                "data": reminder
            }
    return {
        "success": False,
        "message": f"Reminder {reminder_id} not found"
    }


def get_current_time() -> Dict:
    """Get current time"""
    current_time = datetime.now().strftime("%I:%M %p")
    return {
        "success": True,
        "message": f"The current time is {current_time}",
        "data": {"time": current_time}
    }


def get_current_date() -> Dict:
    """Get current date"""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    return {
        "success": True,
        "message": f"Today is {current_date}",
        "data": {"date": current_date}
    }


async def check_reminders_background(websocket):
    """Background task to check and trigger reminders"""
    while True:
        try:
            current_time = datetime.now()
            for reminder in reminders:
                if reminder.get("active", True):
                    reminder_time = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M")

                    # Check if reminder time has passed
                    if current_time >= reminder_time:
                        # Mark as inactive
                        reminder["active"] = False

                        # Send reminder notification to client
                        await websocket.send(json.dumps({
                            'type': 'reminder',
                            'data': {
                                'message': f"⏰ Reminder: {reminder['text']}",
                                'reminder': reminder
                            }
                        }))

                        # Generate TTS for reminder
                        audio_content = text_to_speech(f"Reminder: {reminder['text']}")
                        if audio_content:
                            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                            await websocket.send(json.dumps({
                                'type': 'audio_response',
                                'audio': audio_base64
                            }))

            await asyncio.sleep(10)  # Check every 10 seconds

        except Exception as e:
            print(f"[ERROR] Reminder checker: {e}")
            await asyncio.sleep(10)


# Function mapping - ✅ FIXED: Removed search_information
function_map = {
    "set_reminder": set_reminder,
    "send_message": send_message,
    "play_music": play_music,
    "get_reminders": get_reminders,
    "get_messages": get_messages,
    "delete_reminder": delete_reminder,
    "get_current_time": get_current_time,
    "get_current_date": get_current_date
}


class AIVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

    async def process_command(self, user_message: str, conversation_history: List[Dict]) -> Dict:
        try:
            # Build messages (ONLY dicts)
            messages = conversation_history + [
                {"role": "user", "content": user_message}
            ]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )

            msg = response.choices[0].message
            tool_calls = msg.tool_calls

            # ✅ NO TOOL CALL
            if not tool_calls:
                assistant_dict = {
                    "role": "assistant",
                    "content": msg.content
                }

                return {
                    "status": "success",
                    "message": msg.content,
                    "function_called": None,
                    "conversation_update": assistant_dict
                }

            # ✅ TOOL CALL HANDLING
            function_results = []
            tool_messages = []

            for tc in tool_calls:
                function_name = tc.function.name
                # Handle empty/None arguments properly
                try:
                    function_args = json.loads(
                        tc.function.arguments) if tc.function.arguments and tc.function.arguments.strip() else {}
                except (json.JSONDecodeError, AttributeError):
                    function_args = {}

                # Ensure function_args is always a dict
                if function_args is None:
                    function_args = {}

                # Convert string "true"/"false" to boolean
                if function_args:
                    for key, value in function_args.items():
                        if isinstance(value, str) and value.lower() in ["true", "false"]:
                            function_args[key] = value.lower() == "true"

                if function_name in function_map:
                    result = function_map[function_name](**function_args)
                    function_results.append({
                        "tool_call_id": tc.id,
                        "function_name": function_name,
                        "result": result
                    })

                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result)
                    })

            # ✅ Add assistant tool-call message (DICT, not object)
            assistant_tool_call_message = {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            }

            messages.append(assistant_tool_call_message)
            messages.extend(tool_messages)

            # ✅ Final LLM response
            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )

            final_text = final_response.choices[0].message.content

            return {
                "status": "success",
                "message": final_text,
                "function_called": function_results[0]["function_name"] if function_results else None,
                "function_results": function_results,
                "conversation_update": (
                        [assistant_tool_call_message] +
                        tool_messages +
                        [{"role": "assistant", "content": final_text}]
                )
            }

        except Exception as e:
            print(f"Error processing command: {e}")
            return {
                "status": "error",
                "message": str(e),
                "function_called": None
            }

    def process_audio(self, base64_audio: str) -> str:
        """
        ✅ Use Groq Whisper instead of Google Speech Recognition
        """
        tmp_filename = None

        try:
            print("[DEBUG] Starting audio processing...")

            # Decode base64 audio from frontend
            audio_bytes = base64.b64decode(base64_audio)
            print(f"[DEBUG] Decoded {len(audio_bytes)} bytes of audio")

            # Save directly as webm (browser format)
            tmp_filename = tempfile.mktemp(suffix=".webm")
            with open(tmp_filename, "wb") as f:
                f.write(audio_bytes)

            print(f"[DEBUG] Saved to temp file: {tmp_filename}")

            # Use Groq Whisper API for transcription
            with open(tmp_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    response_format="text"
                )

            print(f"[DEBUG] Recognition successful: {transcription}")
            return transcription

        except Exception as e:
            print(f"[ERROR] Audio processing failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return f"[ERROR] {type(e).__name__}: {str(e)}"
        finally:
            # Clean up temp file
            if tmp_filename and os.path.exists(tmp_filename):
                try:
                    os.remove(tmp_filename)
                    print(f"[DEBUG] Cleaned up temp file: {tmp_filename}")
                except:
                    pass


# Global assistant instance
assistant = AIVoiceAssistant()

# System prompt for the assistant
SYSTEM_PROMPT = """You are a helpful, friendly voice assistant. You can:
- Set reminders and manage them
- Send messages
- Play music based on user preferences
- Answer questions and provide information
- Tell the current time and date

Be conversational, concise, and helpful. When users ask you to do something, use the appropriate function.
Keep responses brief for voice interaction (1-3 sentences unless more detail is requested).
Be proactive in suggesting related actions when appropriate."""


async def handle_client(websocket, path):
    """Handle WebSocket client connection with logging"""
    print(f"[CONNECT] Client connected: {websocket.remote_address}")

    # Initialize conversation history for this client
    client_conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    print("[INFO] Initialized conversation history")

    # Start reminder checker background task
    reminder_task = asyncio.create_task(check_reminders_background(websocket))

    try:
        async for message in websocket:
            try:
                print(f"[RECEIVED] Raw message: {message[:100]}...")  # truncated for readability
                data = json.loads(message)
                print(f"[PARSE] JSON parsed successfully: type={data.get('type')}")

                if data['type'] == 'audio':
                    print("[INFO] Audio message received")

                    # Process audio to text
                    text = assistant.process_audio(data['audio'])
                    print(f"[TRANSCRIPTION] Recognized text: {text}")

                    # Check if transcription was successful
                    if text and not text.startswith("[ERROR]") and not text.startswith("[WARN]"):
                        # Send transcription
                        await websocket.send(json.dumps({
                            'type': 'transcription',
                            'text': text
                        }))
                        print("[SEND] Transcription sent to client")

                        # Process command with AI
                        print("[INFO] Sending text to AI for processing")
                        response = await assistant.process_command(text, client_conversation)
                        print(f"[AI RESPONSE] {response['message']}")

                        # Update conversation history
                        print("[INFO] Updating conversation history")
                        client_conversation.append({"role": "user", "content": text})
                        if response.get("conversation_update"):
                            if isinstance(response["conversation_update"], list):
                                client_conversation.extend(response["conversation_update"])
                            else:
                                client_conversation.append(response["conversation_update"])
                        print(f"[INFO] Conversation history length: {len(client_conversation)}")

                        # Keep conversation history manageable (last 20 messages)
                        if len(client_conversation) > 21:
                            client_conversation = [client_conversation[0]] + client_conversation[-20:]
                            print("[INFO] Truncated conversation history to last 20 messages")

                        # Send response
                        await websocket.send(json.dumps({
                            'type': 'response',
                            'data': response
                        }))

                        print("[SEND] AI response sent to client")

                        # Generate and send speech audio
                        if response['message']:
                            print("[INFO] Generating TTS audio")
                            audio_content = text_to_speech(response['message'])
                            if audio_content:
                                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                                await websocket.send(json.dumps({
                                    'type': 'audio_response',
                                    'audio': audio_base64
                                }))
                                print("[SEND] TTS audio sent to client")
                    else:
                        # Send error to client
                        print(f"[WARN] Audio processing failed: {text}")
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Could not process audio. Please try again.'
                        }))

                elif data['type'] == 'text':
                    print("[INFO] Text message received")
                    text = data['text']
                    print(f"[USER MESSAGE] {text}")

                    response = await assistant.process_command(text, client_conversation)
                    print(f"[AI RESPONSE] {response['message']}")

                    # Update conversation history
                    client_conversation.append({"role": "user", "content": text})
                    if response.get("conversation_update"):
                        if isinstance(response["conversation_update"], list):
                            client_conversation.extend(response["conversation_update"])
                        else:
                            client_conversation.append(response["conversation_update"])
                    print(f"[INFO] Conversation history length: {len(client_conversation)}")

                    # Keep conversation history manageable
                    if len(client_conversation) > 21:
                        client_conversation = [client_conversation[0]] + client_conversation[-20:]
                        print("[INFO] Truncated conversation history to last 20 messages")

                    await websocket.send(json.dumps({
                        'type': 'response',
                        'data': response
                    }))
                    print("[SEND] AI response sent to client")

                    # Generate and send speech audio
                    if response['message']:
                        print("[INFO] Generating TTS audio")
                        audio_content = text_to_speech(response['message'])
                        if audio_content:
                            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                            await websocket.send(json.dumps({
                                'type': 'audio_response',
                                'audio': audio_base64
                            }))
                            print("[SEND] TTS audio sent to client")

            except json.JSONDecodeError:
                print("[ERROR] Invalid JSON format")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                print(f"[ERROR] Processing message failed: {e}")
                import traceback
                traceback.print_exc()
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))

    except websockets.exceptions.ConnectionClosed:
        print(f"[DISCONNECT] Client disconnected: {websocket.remote_address}")
    finally:
        # Cancel reminder task when client disconnects
        reminder_task.cancel()


async def main():
    """Start WebSocket server"""
    print("=" * 60)
    print("AI Voice Assistant WebSocket Server")
    print("=" * 60)
    print(f"Server starting on ws://localhost:8765")
    print(f"Make sure GROQ_API_KEY is set in environment variables")
    print("=" * 60)

    async with websockets.serve(handle_client, "localhost", 8765, max_size=10 ** 7):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())