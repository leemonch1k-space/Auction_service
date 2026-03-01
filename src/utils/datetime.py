from datetime import timedelta, timezone, datetime


# Support methods with datatime

def get_24h_from_now():
    """Support method for getting datetime instance with additional 24 hours."""
    return datetime.now(timezone.utc) + timedelta(hours=24)
