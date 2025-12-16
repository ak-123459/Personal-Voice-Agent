from datetime import datetime
from typing import Dict, List
import webbrowser
import urllib.parse

messages: List[Dict] = []
music_queue: List[Dict] = []

def send_message(content: str, recipient: str = "default") -> Dict:
    message = {
        "id": len(messages) + 1,
        "recipient": recipient,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    return {"success": True, "message": f"Message sent to {recipient}", "data": message}

def get_messages() -> Dict:
    return {"success": True, "message": f"You have {len(messages)} message(s)", "data": messages}

def play_music(query: str, shuffle: bool = False) -> Dict:
    yt_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={yt_query}"
    webbrowser.open(url)
    return {"success": True, "message": f"Opening YouTube for {query}", "data": {"platform": "YouTube", "query": query}}

def get_current_time() -> Dict:
    current_time = datetime.now().strftime("%I:%M %p")
    return {"success": True, "message": f"The current time is {current_time}", "data": {"time": current_time}}

def get_current_date() -> Dict:
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    return {"success": True, "message": f"Today is {current_date}", "data": {"date": current_date}}
