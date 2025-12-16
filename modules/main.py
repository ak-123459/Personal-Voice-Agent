import asyncio
import websockets
import json
from assistant import assistant
from tts import text_to_speech
from tools import tools
from reminders import reminders
from datetime import datetime, timedelta
import base64
SYSTEM_PROMPT = """You are a helpful, friendly voice assistant. You can:
- Set reminders and manage them
- Send messages
- Play music
- Answer questions
- Tell current time and date
Keep responses brief for voice interaction."""

async def check_reminders_background(websocket):
    while True:
        try:
            current_time = datetime.now()
            for reminder in reminders:
                if reminder.get("active", True):
                    reminder_time = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M")
                    if current_time >= reminder_time:
                        reminder["active"] = False
                        await websocket.send(json.dumps({'type': 'reminder', 'data': {'message': f"⏰ Reminder: {reminder['text']}", 'reminder': reminder}}))
                        audio_content = text_to_speech(f"Reminder: {reminder['text']}")
                        if audio_content:
                            await websocket.send(json.dumps({'type': 'audio_response', 'audio': base64.b64encode(audio_content).decode('utf-8')}))
            await asyncio.sleep(10)
        except Exception as e:
            print(f"[ERROR] Reminder checker: {e}")
            await asyncio.sleep(10)

# Include handle_client() logic here as is, using assistant.process_command() and assistant.process_audio()





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
    async with websockets.serve(handle_client, "localhost", 8765, max_size=10 ** 7):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
