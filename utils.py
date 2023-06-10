from datetime import timedelta

def next_week(today):
    next_weekday = (0 - today.weekday()) % 7  # 0 represents Monday
    next_monday = today + timedelta(days=next_weekday)
    _, week_number, _ = next_monday.isocalendar()
    return (week_number, map(lambda offset : next_monday + timedelta(offset), range(7)))
