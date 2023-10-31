from datetime import time, datetime, timedelta
import json

import requests

API_ENDPOINT = 'https://api.strawpoll.com/v3/polls'

def create_poll(title, days, hours):
    options = [e for es in days for e in create_events(es, hours)]
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

def create_events(day, hours):
    """
    Creates the events for a given day
    """
    create_slot = lambda h: time(h, 0)
    time_slots = map(create_slot, hours)
    return map(lambda slot : create_event(day, slot), time_slots)

def create_event(day, time):
    """
    Creates a single event option in the poll
    """
    start = datetime.combine(day, time)
    end = start + timedelta(hours=1) # Length of each option duration
    return {
            "end_time": int(end.timestamp()),
            "start_time": int(start.timestamp()),
            "type": "time_range"
            }


def send_poll_req(f, poll):
    """
    Sends the poll request
    f is the function that will be called with the response
    """
    poll_json = json.dumps(poll)
    resp = requests.post(API_ENDPOINT, poll_json)
    return f(resp)
