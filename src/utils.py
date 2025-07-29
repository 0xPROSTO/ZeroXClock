import re

def parse_shutdown_time(time_str: str) -> int:
    """Parse string like '1h 30m 15s' into total seconds."""
    pattern = r'(\d+)([dhms])'
    seconds = 0

    for value, unit in re.findall(pattern, time_str.lower()):
        value = int(value)
        seconds += value * {'d': 86400, 'h': 3600, 'm': 60, 's': 1}[unit]

    if seconds == 0:
        raise ValueError('Invalid time format. Use format like "1h 30m 15s".')

    return seconds

def hide_cursor():
    print('\033[?25l', end='')
