import datetime
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now():
    return datetime.datetime.utcnow()