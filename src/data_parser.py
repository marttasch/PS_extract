# src/data_parser.py

import os
import datetime
from dateutil import tz

def get_modif_time(entry):
    return entry.stat().st_mtime

def parse_data(trip_data, data_dir, extract_dir, verbose=False):
    """
    Parses the trip data and returns a list of steps with their information.
    """
    steps_info = []
    timezone_id = trip_data.get('timezone_id', 'UTC')
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(timezone_id)

    for entry in trip_data['all_steps']:
        step = {}
        step['id'] = entry['id']
        step['slug'] = entry['slug']
        step['name'] = entry['display_name']
        creation_time = datetime.datetime.fromtimestamp(entry['start_time'])
        creation_time = creation_time.replace(tzinfo=from_zone)
        adjusted_time = creation_time.astimezone(to_zone)
        step['date'] = adjusted_time.strftime('%Y-%m-%d')
        step['datetime'] = adjusted_time

        location = entry['location']
        step['location_name'] = location['name']
        step['lat'] = location['lat']
        step['lon'] = location['lon']
        step['country'] = location['detail']
        step['full_detail'] = location['full_detail']

        step['weather'] = entry.get('weather_condition', '')
        step['temperature'] = entry.get('weather_temperature', '')

        step['description'] = entry['description'] if entry['description'] else ''

        # Collect and sort media paths
        photos_path = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "photos")
        step['photos'] = []
        if os.path.isdir(photos_path):
            with os.scandir(photos_path) as entries:
                sorted_entries = sorted(entries, key=get_modif_time)
                sorted_photos = [entry.name for entry in sorted_entries if entry.name != 'Thumbs.db']
                step['photos'] = sorted_photos

        videos_path = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "videos")
        step['videos'] = []
        if os.path.isdir(videos_path):
            with os.scandir(videos_path) as entries:
                sorted_entries = sorted(entries, key=get_modif_time)
                sorted_videos = [entry.name for entry in sorted_entries if entry.name != 'Thumbs.db']
                step['videos'] = sorted_videos

        steps_info.append(step)

    return steps_info
