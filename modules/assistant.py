import base64
import json
import tempfile
import os
from typing import List, Dict
import speech_recognition as sr
from openai import OpenAI
from groq import Groq
from tts import text_to_speech
from function import *
from reminders import *
import threading
from tools import tools

# Initialize Groq client
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AIVoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

    async def process_command(self, user_message: str, conversation_history: List[Dict]) -> Dict:
        try:
            messages_hist = conversation_history + [{"role": "user", "content": user_message}]
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_hist,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )

            msg = response.choices[0].message
            tool_calls = msg.tool_calls
            if not tool_calls:
                assistant_dict = {"role": "assistant", "content": msg.content}
                return {"status": "success", "message": msg.content, "function_called": None, "conversation_update": assistant_dict}

            function_results = []
            tool_messages = []
            for tc in tool_calls:
                function_name = tc.function.name
                try:
                    function_args = json.loads(tc.function.arguments) if tc.function.arguments and tc.function.arguments.strip() else {}
                except (json.JSONDecodeError, AttributeError):
                    function_args = {}

                if function_args is None:
                    function_args = {}

                if function_args:
                    for key, value in function_args.items():
                        if isinstance(value, str) and value.lower() in ["true", "false"]:
                            function_args[key] = value.lower() == "true"

                if function_name in function_map:
                    result = function_map[function_name](**function_args)
                    function_results.append({"tool_call_id": tc.id, "function_name": function_name, "result": result})
                    tool_messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

            assistant_tool_call_message = {
                "role": "assistant",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in tool_calls
                ]
            }

            messages_hist.append(assistant_tool_call_message)
            messages_hist.extend(tool_messages)

            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_hist,
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
                "conversation_update": ([assistant_tool_call_message] + tool_messages + [{"role": "assistant", "content": final_text}])
            }

        except Exception as e:
            print(f"Error processing command: {e}")
            return {"status": "error", "message": str(e), "function_called": None}

    def process_audio(self, base64_audio: str) -> str:
        tmp_filename = None
        try:
            audio_bytes = base64.b64decode(base64_audio)
            tmp_filename = tempfile.mktemp(suffix=".webm")
            with open(tmp_filename, "wb") as f:
                f.write(audio_bytes)

            with open(tmp_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    response_format="text"
                )
            return transcription
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"[ERROR] {type(e).__name__}: {str(e)}"
        finally:
            if tmp_filename and os.path.exists(tmp_filename):
                os.remove(tmp_filename)

# Global assistant instance
assistant = AIVoiceAssistant()
