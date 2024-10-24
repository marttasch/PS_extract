# src/html_generator.py

import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader
from collections import OrderedDict  # Import OrderedDict to maintain order

def generate_html(trip_data, steps_info, loc_data, extract_dir, verbose=False):
    """
    Generates HTML files for the trip and steps.
    """
    # Set up paths and Jinja2 environment
    templates_dir = os.path.join('src', 'templates')
    static_src_dir = os.path.join('src', 'static')  # Source directory for static assets
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Load templates
    index_template = env.get_template('index_template.html')
    step_template = env.get_template('step_template.html')

    # Prepare trip information for index.html
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
    copy_static_assets(static_src_dir, extract_dir)

    # Process media files for steps
    process_media_files(steps_info, extract_dir)

    # Prepare step coordinates and route data for maps
    step_coords = prepare_step_coords(steps_info)
    route_coords = prepare_route_coords(loc_data)

    # Collect unique countries and their flags
    countries_visited = collect_countries(steps_info)

    # Generate index.html
    generate_index_html(index_template, trip_info, steps_info, step_coords, route_coords, countries_visited, extract_dir)

    # Generate step pages
    generate_step_pages(step_template, steps_info, step_coords, route_coords, extract_dir)

def copy_static_assets(static_src_dir, extract_dir):
    """
    Copies static assets (CSS, JS, images) to the Extracts folder.
    """
    static_extract_dir = os.path.join(extract_dir, 'static')
    if not os.path.exists(static_extract_dir):
        shutil.copytree(static_src_dir, static_extract_dir)
    else:
        # If static directory already exists, update its contents
        shutil.rmtree(static_extract_dir)
        shutil.copytree(static_src_dir, static_extract_dir)

def process_media_files(steps_info, extract_dir):
    """
    Copies media files (photos and videos) for each step and updates their paths.
    """
    for step in steps_info:
        # Define source and destination directories for photos
        photos_src_dir = os.path.join('data', f"{step['slug']}_{step['id']}", "photos")
        photos_dest_dir = os.path.join(extract_dir, f"{step['slug']}_{step['id']}", "photos")

        # Copy photos if available and update paths
        if os.path.exists(photos_src_dir):
            os.makedirs(photos_dest_dir, exist_ok=True)
            for photo in step['photos']:
                shutil.copy(os.path.join(photos_src_dir, photo), photos_dest_dir)
            # Update photo paths relative to the Extracts folder
            step['photos'] = [os.path.join(f"{step['slug']}_{step['id']}", "photos", photo) for photo in step['photos']]
        else:
            step['photos'] = []

        # Define source and destination directories for videos
        videos_src_dir = os.path.join('data', f"{step['slug']}_{step['id']}", "videos")
        videos_dest_dir = os.path.join(extract_dir, f"{step['slug']}_{step['id']}", "videos")

        # Copy videos if available and update paths
        if os.path.exists(videos_src_dir):
            os.makedirs(videos_dest_dir, exist_ok=True)
            for video in step['videos']:
                shutil.copy(os.path.join(videos_src_dir, video), videos_dest_dir)
            # Update video paths relative to the Extracts folder
            step['videos'] = [os.path.join(f"{step['slug']}_{step['id']}", "videos", video) for video in step['videos']]
        else:
            step['videos'] = []

def prepare_step_coords(steps_info):
    """
    Prepares step coordinates for mapping.
    """
    step_coords = []
    for step in steps_info:
        coord = {
            'lat': step['lat'],
            'lon': step['lon'],
            'name': step['name'].replace("'", "\\'"),
            'date': step['date'].replace("'", "\\'"),
            'id': step['id'],
            'slug': step['slug']
        }
        step_coords.append(coord)
    return step_coords

def prepare_route_coords(loc_data):
    """
    Prepares route coordinates from location data if available.
    """
    route_coords = []
    if loc_data and 'locations' in loc_data:
        sorted_locs = sorted(loc_data['locations'], key=lambda x: x['time'])
        for loc in sorted_locs:
            lat = loc['lat']
            lon = loc['lon']
            route_coords.append([lat, lon])
    return route_coords

def collect_countries(steps_info):
    """
    Collects unique countries visited and their flags, maintaining the order of first visit.
    """
    from collections import OrderedDict
    countries_visited = OrderedDict()
    for step in steps_info:
        country = step['country']
        flag = step.get('flag', '')
        if country not in countries_visited:
            countries_visited[country] = flag
    return countries_visited

def generate_index_html(index_template, trip_info, steps_info, step_coords, route_coords, countries_visited, extract_dir):
    """
    Generates the index.html file with the trip overview, map, and country flags.
    """
    # Render the index.html template
    index_html = index_template.render(
        trip_info=trip_info,
        steps_info=steps_info,
        step_coords=json.dumps(step_coords),
        route_coords=json.dumps(route_coords),
        countries_visited=countries_visited
    )

    # Write the rendered HTML to the index.html file
    with open(os.path.join(extract_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

def generate_step_pages(step_template, steps_info, step_coords, route_coords, extract_dir):
    """
    Generates the individual step pages with details and media.
    """
    total_steps = len(steps_info)
    for i, step in enumerate(steps_info):
        # Determine previous and next steps for navigation
        prev_step = steps_info[i - 1] if i > 0 else None
        next_step = steps_info[i + 1] if i < total_steps - 1 else None

        # Prepare data for the template
        step_html = step_template.render(
            step=step,
            lat=step['lat'],
            lon=step['lon'],
            step_coords=json.dumps(step_coords),
            route_coords=json.dumps(route_coords),
            current_step_id=step['id'],
            prev_step=prev_step,
            next_step=next_step
        )

        # Generate the filename for the step page
        step_filename = f"{step['slug']}_{step['id']}.html"

        # Write the rendered HTML to the step page file
        with open(os.path.join(extract_dir, step_filename), 'w', encoding='utf-8') as f:
            f.write(step_html)
