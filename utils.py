from datetime import timedelta
import json

def next_week(today):
    """
    Gives back the week number and the days of the next week
    """
    next_weekday = (0 - today.weekday()) % 7  # 0 represents Monday
    next_monday = today + timedelta(days=next_weekday)
    _, week_number, _ = next_monday.isocalendar()
    return (week_number, map(lambda offset : next_monday + timedelta(offset), range(7)))

def load_config(file_name):
    with open(file_name) as f:
        return json.loads(f.read())

def load_jokes(file_name):
    with open(file_name) as f:
        return f.read().split('\n')
        
def modify_config(new_conf, file_name):
    with open(file_name, 'w') as f:
        f.write(json.dumps(new_conf))

def show_day(day):
    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[day]
