from datetime import datetime, timedelta
import webbrowser
import urllib.parse


reminders = []
messages = []

def set_reminder(reminder_text: str, duration_minutes: int = 5) -> dict:
    reminder_time = datetime.now() + timedelta(minutes=duration_minutes)
    reminder = {
        "id": len(reminders) + 1,
        "text": reminder_text,
        "time": reminder_time.strftime("%Y-%m-%d %H:%M"),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active": True
    }
    reminders.append(reminder)
    return {"success": True, "message": f"Reminder set for {reminder_time.strftime('%I:%M %p')}", "data": reminder}

def send_message(content: str, recipient: str = "default") -> dict:
    message = {
        "id": len(messages) + 1,
        "recipient": recipient,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    messages.append(message)
    return {"success": True, "message": f"Message sent to {recipient}", "data": message}

def play_youtube(query: str) -> dict:
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return {"success": True, "message": f"Opening YouTube to play: {query}", "data": {"platform": "YouTube", "query": query, "url": url}}

def get_reminders() -> dict:
    active_reminders = [r for r in reminders if r.get("active", True)]
    return {"success": True, "message": f"You have {len(active_reminders)} active reminder(s)", "data": active_reminders}

def get_messages() -> dict:
    return {"success": True, "message": f"You have {len(messages)} message(s)", "data": messages}

def delete_reminder(reminder_id: int) -> dict:
    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["active"] = False
            return {"success": True, "message": f"Reminder {reminder_id} deleted", "data": reminder}
    return {"success": False, "message": f"Reminder {reminder_id} not found"}

def get_current_time() -> dict:
    current_time = datetime.now().strftime("%I:%M %p")
    return {"success": True, "message": f"The current time is {current_time}", "data": {"time": current_time}}

def get_current_date() -> dict:
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    return {"success": True, "message": f"Today is {current_date}", "data": {"date": current_date}}
