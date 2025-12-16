from datetime import datetime, timedelta
from typing import List, Dict

reminders: List[Dict] = []

def set_reminder(reminder_text: str, duration_minutes: int = 5) -> Dict:
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

def get_reminders() -> Dict:
    active_reminders = [r for r in reminders if r.get("active", True)]
    return {
        "success": True,
        "message": f"You have {len(active_reminders)} active reminder(s)",
        "data": active_reminders
    }

def delete_reminder(reminder_id: int) -> Dict:
    for reminder in reminders:
        if reminder["id"] == reminder_id:
            reminder["active"] = False
            return {
                "success": True,
                "message": f"Reminder {reminder_id} deleted",
                "data": reminder
            }
    return {"success": False, "message": f"Reminder {reminder_id} not found"}
