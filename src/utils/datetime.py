from datetime import timedelta, timezone, datetime


def get_24h_from_now():
    return datetime.now(timezone.utc) + timedelta(hours=24)
