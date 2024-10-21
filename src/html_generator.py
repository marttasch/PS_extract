# src/html_generator.py

import os
import json
from jinja2 import Environment, FileSystemLoader
import shutil

def generate_html(trip_data, steps_info, loc_data, extract_dir, verbose=False):
    """
    Generates HTML files for the trip and steps.
    """
    templates_dir = os.path.join('src', 'templates')
    static_src_dir = os.path.join('src', 'static')  # Source directory for static assets
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Load templates
    index_template = env.get_template('index_template.html')
    step_template = env.get_template('step_template.html')
    
    # Prepare data for index.html
    trip_info = {
        'trip_name': trip_data['name'].strip(),
        'trip_summary': trip_data['summary'],
        'trip_start_date': trip_data['start_date'],
        'trip_end_date': trip_data.get('end_date', None),
        'total_distance': trip_data['total_km'],
        'total_entries': trip_data['step_count'],
        'timezone_id': trip_data.get('timezone_id', 'UTC')
    }

    # Copy static assets to the Extracts folder
    static_extract_dir = os.path.join(extract_dir, 'static')
    if not os.path.exists(static_extract_dir):
        shutil.copytree(static_src_dir, static_extract_dir)
    else:
        # If static directory already exists, update its contents
        shutil.rmtree(static_extract_dir)
        shutil.copytree(static_src_dir, static_extract_dir)

    # Process steps_info to copy media files and update paths
    for step in steps_info:
        # Define source and destination directories for photos
        photos_src_dir = os.path.join('data', f"{step['slug']}_{step['id']}", "photos")
        photos_dest_dir = os.path.join(extract_dir, f"{step['slug']}_{step['id']}", "photos")
        if os.path.exists(photos_src_dir):
            os.makedirs(photos_dest_dir, exist_ok=True)
            for photo in step['photos']:
                shutil.copy(os.path.join(photos_src_dir, photo), photos_dest_dir)
            # Update the paths in step['photos'] to point to the new location relative to the Extracts folder
            step['photos'] = [os.path.join(f"{step['slug']}_{step['id']}", "photos", photo) for photo in step['photos']]
        else:
            step['photos'] = []

        # Similarly, copy videos if needed
        videos_src_dir = os.path.join('data', f"{step['slug']}_{step['id']}", "videos")
        videos_dest_dir = os.path.join(extract_dir, f"{step['slug']}_{step['id']}", "videos")
        if os.path.exists(videos_src_dir):
            os.makedirs(videos_dest_dir, exist_ok=True)
            for video in step['videos']:
                shutil.copy(os.path.join(videos_src_dir, video), videos_dest_dir)
            # Update the paths in step['videos'] to point to the new location relative to the Extracts folder
            step['videos'] = [os.path.join(f"{step['slug']}_{step['id']}", "videos", video) for video in step['videos']]
        else:
            step['videos'] = []

     # Prepare step coordinates for the map
    step_coords = []
    for step in steps_info:
        coord = {
            'lat': step['lat'],
            'lon': step['lon'],
            'name': step['name'].replace("'", "\\'"),
            'date': step['date'].replace("'", "\\'"),
            'id': step['id']
        }
        step_coords.append(coord)

    # Prepare route coordinates from loc_data if available
    route_coords = []
    if loc_data and 'locations' in loc_data:
        sorted_locs = sorted(loc_data['locations'], key=lambda x: x['time'])
        for loc in sorted_locs:
            lat = loc['lat']
            lon = loc['lon']
            route_coords.append([lat, lon])

    # Now generate index.html with updated step paths and map data
    index_html = index_template.render(
        trip_info=trip_info,
        steps_info=steps_info,
        step_coords=json.dumps(step_coords),
        route_coords=json.dumps(route_coords)
    )
    with open(os.path.join(extract_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

    # Generate step pages
    for step in steps_info:
        step_html = step_template.render(step=step, lat=step['lat'], lon=step['lon'])
        step_filename = f"{step['slug']}_{step['id']}.html"
        with open(os.path.join(extract_dir, step_filename), 'w', encoding='utf-8') as f:
            f.write(step_html)
