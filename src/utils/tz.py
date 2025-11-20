import datetime
from typing import Optional, Union, Dict, Any
from zoneinfo import ZoneInfo
from src.config import TIMEZONE


def _to_zone(dt: datetime.datetime, tz_name: str = TIMEZONE) -> datetime.datetime:
    try:
        return dt.astimezone(ZoneInfo(tz_name))
    except Exception:
        return dt


def parse_event_datetime(date_obj: Optional[Union[Dict[str, Any], str, datetime.datetime]],
                         is_all_day: bool = False, tz_name: str = TIMEZONE) -> Optional[datetime.datetime]:
    if not date_obj:
        return None

    if isinstance(date_obj, datetime.datetime):
        dt = date_obj
        if dt.tzinfo is None:
            if is_all_day:
                dt = dt.replace(tzinfo=ZoneInfo(tz_name))
                return dt
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return _to_zone(dt, tz_name)

    if isinstance(date_obj, dict):
        if is_all_day and "date" in date_obj:
            try:
                d = datetime.date.fromisoformat(date_obj["date"])  # YYYY-MM-DD
                dt = datetime.datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=ZoneInfo(tz_name))
                return dt
            except Exception:
                return None
        if "dateTime" in date_obj:
            try:
                dt = datetime.datetime.fromisoformat(date_obj["dateTime"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return _to_zone(dt, tz_name)
            except Exception:
                return None
        return None

    if isinstance(date_obj, str):
        try:
            dt = datetime.datetime.fromisoformat(date_obj)
            if dt.tzinfo is None:
                if is_all_day:
                    return dt.replace(tzinfo=ZoneInfo(tz_name))
                return _to_zone(dt.replace(tzinfo=datetime.timezone.utc), tz_name)
            return _to_zone(dt, tz_name)
        except Exception:
            try:
                d = datetime.date.fromisoformat(date_obj)
                dt = datetime.datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=ZoneInfo(tz_name))
                return dt
            except Exception:
                return None

    return None


def format_datetime(dt: Optional[datetime.datetime], is_all_day: bool = False) -> Optional[str]:
    if not dt:
        return None

    try:
        if is_all_day:
            return dt.strftime("%Y-%m-%d")
        return dt.strftime("%H:%M")
    except Exception:
        return None
