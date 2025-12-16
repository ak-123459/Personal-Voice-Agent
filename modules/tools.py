from function import *
from reminders import *

tools = [
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder",
            "parameters": {"type": "object", "properties": {"reminder_text": {"type": "string"}, "duration_minutes": {"type": "integer", "default": 5}}, "required": ["reminder_text"]}
        }
    },
    {
        "type": "function",
        "function": {"name": "send_message", "description": "Send message", "parameters": {"type": "object", "properties": {"recipient": {"type": "string"}, "content": {"type": "string"}}, "required": ["content"]}}
    },
    {
        "type": "function",
        "function": {"name": "play_music", "description": "Play music", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "shuffle": {"type": "boolean", "default": False}}, "required": ["query"]}}
    },
    {
        "type": "function",
        "function": {"name": "get_reminders", "description": "Get reminders", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "get_messages", "description": "Get messages", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "delete_reminder", "description": "Delete reminder", "parameters": {"type": "object", "properties": {"reminder_id": {"type": "integer"}}, "required": ["reminder_id"]}}
    },
    {
        "type": "function",
        "function": {"name": "get_current_time", "description": "Get current time", "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function",
        "function": {"name": "get_current_date", "description": "Get current date", "parameters": {"type": "object", "properties": {}}}
    }
]

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
