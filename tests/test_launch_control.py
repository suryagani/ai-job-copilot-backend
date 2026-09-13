from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from launch_control import get_launch_status, is_launched


LAUNCH_AT = datetime(2026, 9, 14, 12, 14, tzinfo=timezone.utc)


def test_launch_boundary_is_inclusive():
    assert is_launched(LAUNCH_AT.replace(minute=13, second=59)) is False
    assert is_launched(LAUNCH_AT) is True
    assert is_launched(LAUNCH_AT.replace(second=1)) is True


def test_launch_uses_one_absolute_instant_across_timezones():
    assert is_launched(datetime(2026, 9, 14, 13, 14, tzinfo=ZoneInfo("Europe/London"))) is True
    assert is_launched(datetime(2026, 9, 14, 17, 44, tzinfo=ZoneInfo("Asia/Kolkata"))) is True
    assert get_launch_status(LAUNCH_AT) == {
        "launch_at": "2026-09-14T12:14:00Z",
        "is_launched": True,
    }
