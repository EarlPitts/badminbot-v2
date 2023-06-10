import datetime
import json
import requests

API_ENDPOINT = 'https://api.strawpoll.com/v3/polls'
FIRST_HOUR = 7
LAST_HOUR = 19

def create_poll(title, days, timezone):
    options = [e for es in days for e in create_events(es, timezone)]
    return {
            "title": title,
            "type": "meeting",
            "poll_config": {
                "vote_type": "participant_grid",
                "is_private": True,
                "is_multiple_choice": True,
                "edit_vote_permissions": "admin_voter",
                "allow_indeterminate": True,
                "duplication_checking": "ip"

                },
            "poll_options": options
            }

def create_events(day, timezone):
    time_slots = range(FIRST_HOUR, LAST_HOUR + 1)
    return map(lambda slot : create_event(day, slot, timezone), time_slots)

def create_event(day, hour, timezone):
    date_with_time = datetime.datetime.combine(day, datetime.time(0,0, tzinfo=timezone))
    offset = datetime.timedelta(hours=hour)
    duration = datetime.timedelta(hours=1)
    start = date_with_time + offset
    end = date_with_time + offset + duration
    return {
            "end_time": int(end.timestamp()),
            "start_time": int(start.timestamp()),
            "type": "time_range"
            }


def send_poll_req(f, poll):
    poll_json = json.dumps(poll)
    resp = requests.post(API_ENDPOINT, poll_json)
    return f(resp)
