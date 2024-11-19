# src/html_generator.py

import os
import json
import shutil
import io
from ruamel.yaml import YAML
import textwrap
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from collections import OrderedDict  # Import OrderedDict to maintain order


# ##############################################################################
# ############################### HTML GENERATION ##############################
# ##############################################################################
def generate_html(trip_data, steps_info, loc_data, data_dir, extract_dir, verbose=False):
    """
    Generates HTML files for the trip and steps.
    """
    extract_dir = os.path.join(extract_dir, 'html')
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
    process_media_files(steps_info, data_dir, extract_dir)

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

def process_media_files(steps_info, data_dir, extract_dir):
    """
    Copies media files (photos and videos) for each step and updates their paths.
    """
    for step in steps_info:
        # Define source and destination directories for photos
        photos_src_dir = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "photos")
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
        videos_src_dir = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "videos")
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
    countrieCode_visited = []

    for step in steps_info:
        country = step['country']
        flag = step.get('flag', '')
        code = step.get('country_code')
        if country not in countries_visited:
            countries_visited[country] = flag
            countrieCode_visited.append(code)

    return countries_visited, countrieCode_visited

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

# ##############################################################################
# ############################### JEKYLL GENERATION #############################
# ##############################################################################
def generate_jekyll(trip_data, steps_info, loc_data, data_dir, trips_dir, verbose=False):
    """
    Generates Markdown files with front matter for Jekyll.
    """
    
    # Copy static assets (if needed)
    # You can copy any static assets required for your Jekyll site here
    
    # Generate trip index
    generate_jekyll_trip_index(trip_data, steps_info, loc_data, trips_dir)
    
    # Generate individual step pages
    for step in steps_info:
        generate_jekyll_step_page(step, trip_data, steps_info, loc_data, data_dir, trips_dir)

def generate_jekyll_trip_index(trip_data, steps_info, loc_data, trips_dir):
    """
    Generates the trip index page for Jekyll.
    """
    trip_slug = trip_data['slug']
    trip_dir = os.path.join(trips_dir, trip_slug)
    os.makedirs(trip_dir, exist_ok=True)

    start_date = datetime.fromtimestamp(trip_data['start_date']).strftime('%Y-%m-%d')

    # Prepare steps info for front matter
    steps_list = []
    for step in steps_info:
        step_info = {
            'title': step['name'],
            'url': f"/trips/{trip_slug}/{step['slug']}_{step['id']}.html",
            'date': step['date'],
            'slug': step['slug'],
            'id': step['id']
        }
        steps_list.append(step_info)

    visited_countries, visited_countrieCodes = collect_countries(steps_info)

    front_matter = {
        'layout': 'trip',
        'title': trip_data['name'].strip(),
        'summary': trip_data['summary'],
        'total_distance': trip_data['total_km'],
        'total_entries': trip_data['step_count'],
        'date': start_date,
        'permalink': f'/trips/{trip_slug}/',
        'steps': steps_list,
        #'step_coords': prepare_step_coords(steps_info),
        #'route_coords': prepare_route_coords(loc_data),
        'countries_visited': dict(visited_countries),
        'countrie_codes_visited': visited_countrieCodes,
        'trip_slug': trip_slug
    }

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.allow_unicode = True

    content_stream = io.StringIO()
    yaml.dump(front_matter, content_stream)
    content = '---\n' + content_stream.getvalue() + '---\n'

    with open(os.path.join(trip_dir, 'index.md'), 'w', encoding='utf-8') as f:
        f.write(content)

def generate_jekyll_step_page(step, trip_data, steps_info, loc_data, data_dir, trips_dir):
    """
    Generates individual step pages for Jekyll.
    """
    trip_slug = trip_data['slug']
    step_filename = f"{step['slug']}_{step['id']}.md"
    step_dir = os.path.join(trips_dir, trip_slug)
    os.makedirs(step_dir, exist_ok=True)

    # Media destination directory: _trips/<trip_slug>/media/<step_slug>/
    media_dest_dir = os.path.join(trips_dir, trip_slug, 'media', step['slug'])
    os.makedirs(media_dest_dir, exist_ok=True)

    # Copy photos, update paths, and add descriptions
    photos_src_dir = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "photos")
    step_photos = []
    if os.path.exists(photos_src_dir):
        for photo in step['photos']:
            src_photo_path = os.path.join(photos_src_dir, photo)
            dest_photo_path = os.path.join(media_dest_dir, photo)
            shutil.copy(src_photo_path, dest_photo_path)
            # Update photo path relative to the site root
            photo_url = f"/trips/{trip_slug}/media/{step['slug']}/{photo}"
            # Add a placeholder for photo description
            photo_description = step.get('photo_descriptions', {}).get(photo, '')
            step_photos.append({'url': photo_url, 'description': photo_description})
    else:
        step_photos = []

    # Copy videos, update paths, and add descriptions
    videos_src_dir = os.path.join(data_dir, f"{step['slug']}_{step['id']}", "videos")
    step_videos = []
    if os.path.exists(videos_src_dir):
        for video in step['videos']:
            src_video_path = os.path.join(videos_src_dir, video)
            dest_video_path = os.path.join(media_dest_dir, video)
            shutil.copy(src_video_path, dest_video_path)
            # Update video path relative to the site root
            video_url = f"/trips/{trip_slug}/media/{step['slug']}/{video}"
            # Add a placeholder for video description
            video_description = step.get('video_descriptions', {}).get(video, '')
            step_videos.append({'url': video_url, 'description': video_description})
    else:
        step_videos = []

    # Add clean multiline description
    description = step.get('description', '').strip()

    # Prepare front matter
    front_matter = {
        'layout': 'step',
        'title': step['name'],
        'date': step['date'],
        'permalink': f"/trips/{trip_slug}/{step['slug']}_{step['id']}.html",
        'location_name': step['location_name'],
        'trip_slug': trip_slug,
        'lat': step['lat'],
        'lon': step['lon'],
        'country': step['country'],
        'flag': step.get('flag', ''),
        'country_code': step.get('country_code'),
        'weather': step.get('weather', ''),
        'weather_emoji': step.get('weather_emoji', ''),
        'weather_temperature': step.get('temperature', ''),
        'description': description,
        'photos': step_photos,
        'videos': step_videos,
        'current_step_id': step['id'],
    }

    def multiline_str_presenter(dumper, data):
        if isinstance(data, str) and '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.allow_unicode = True

    def multiline_str_presenter(dumper, data):
        if isinstance(data, str) and '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.representer.add_representer(str, multiline_str_presenter)

    content_stream = io.StringIO()
    yaml.dump(front_matter, content_stream)
    content = '---\n' + content_stream.getvalue() + '---\n'

    with open(os.path.join(step_dir, step_filename), 'w', encoding='utf-8') as f:
        f.write(content)
