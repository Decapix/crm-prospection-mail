import random
from datetime import datetime

from app.services.scheduler import generate_send_times


def test_generate_send_times_count():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    times = generate_send_times(5, start, end)
    assert len(times) == 5


def test_generate_send_times_within_range():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    random.seed(42)
    times = generate_send_times(10, start, end)
    for t in times:
        assert start <= t <= end


def test_generate_send_times_sorted():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    random.seed(42)
    times = generate_send_times(10, start, end)
    assert times == sorted(times)


def test_generate_send_times_multi_day():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 3, 18, 0)
    times = generate_send_times(20, start, end)
    assert len(times) == 20
    for t in times:
        assert start <= t <= end
