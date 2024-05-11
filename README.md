# BadminBot

Discord bot for automatically creating polls.

## Commands

*Every command requires the `!` prefix*

- `help`: Help message
- `poll`: Forces the poll manually
- `close_poll <id>`: Closes the poll given by its ID (the last part of the url)
- `schedule <weekday_nums>`: Reschedules the poll for the next week, weekdays are 0-6
- `schedule hours <start> <end>`: Reschedules the poll for the next week, `start` and `end` are hours
- `shutup`: Turns off the polls
- `get_schedule`: Sends back the days the next poll will be created with
- `get_timeslots`: Sends back the timeslots the next poll will be created with
- `joke`: **Very** funny
- `call <target>`: Calls target for booking a court
