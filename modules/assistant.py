import base64
import tempfile
import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
from .function import *
from .tools import tools, function_map
import json


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AIVoiceAssistant:
    def __init__(self):
        import speech_recognition as sr
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

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
            return f"[ERROR] {type(e).__name__}: {str(e)}"
        finally:
            if tmp_filename and os.path.exists(tmp_filename):
                os.remove(tmp_filename)



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

                # ✅ IMPROVED: Convert string booleans to actual booleans
                if function_args:
                    for key, value in list(function_args.items()):
                        if isinstance(value, str):
                            value_lower = value.lower()
                            if value_lower in ["true", "false"]:
                                function_args[key] = (value_lower == "true")
                            # Also handle "1" and "0" as booleans
                            elif value in ["1", "0"]:
                                function_args[key] = (value == "1")

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
            import traceback
            traceback.print_exc()
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

