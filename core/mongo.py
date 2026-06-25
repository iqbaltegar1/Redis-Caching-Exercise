from django.conf import settings
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]


def log_activity(event: str, payload: dict):
    payload = payload.copy()
    payload.update({
        'event': event,
        'timestamp': datetime.utcnow(),
    })
    db.activity_logs.insert_one(payload)
    return payload
