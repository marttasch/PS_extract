#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script to extract data from Polarsteps JSON files and generate outputs.
"""
import sys
import os
from pathlib import Path
import json
import gpxpy
import geojson
from src.data_parser import parse_data
from src.output_generator import generate_html, generate_jekyll
from src.email_utils import email_steps, send_trip_email

# Global parameters
extract_dir = "Extracts"
data_dir = "data"
trip_filename = 'trip.json'
map_filename = 'locations.json'

# Set all specific run modes of the script to False; will be modified through command-line arguments
mail = False
local = False
jekyll = False
convert_gpx = False
merge_geojson = False
interactive = False
verbose = False
exclude = False
dest_email = ''

def print_instructions():
    print("""
Usage: python main.py [options]

Options:
    -v, --verbose                  Add additional information in the generated text file
    -l, --local                    Generate local HTML files to navigate the steps
    -j, --jekyll                   Generate Jekyll-compatible markdown files
    -e, --email address@domain.com Send emails containing descriptions, images, and videos to the given address
    -i, --interactive              Display an analysis and interactively ask what to do for each step
    -x, --exclude                  Exclude the first and last steps from generated maps
    
    -f, --folder                   Specify the folder containing the data files (default: 'data')
    -g, --geojson                  Merge all GeoJSON (Folder 'geojson') files into a single file for the webpage
    -c, --convert-gpx              Convert GPX files in the 'gpx' folder to GeoJSON format
    -h, --help                     Display this help message
""")

def main():
    global mail, local, jekyll, interactive, verbose, exclude, dest_email, merge_geojson, convert_gpx
    global data_dir, trip_dir, trip_filename, map_filename

    # Analyze command-line arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ('-e', '--email'):
            mail = True
            i += 1
            if i < len(args):
                dest_email = args[i]
                print(f"Email option activated (sending to {dest_email}).")
            else:
                print("Error: Missing destination email address.")
                print_instructions()
                return
        elif arg in ('-l', '--local'):
            local = True
            print("Local HTML option activated.")
        elif arg in ('-j', '--jekyll'):
            jekyll = True
            print("Jekyll option activated.")
        elif arg in ('-i', '--interactive'):
            interactive = True
            print("Interactive option activated.")
        elif arg in ('-v', '--verbose'):
            verbose = True
            print("Verbose option activated.")
        elif arg in ('-x', '--exclude'):
            exclude = True
            print("Exclude option activated.")
        elif arg in ('-f', '--folder'):
            i += 1
            if i < len(args):
                data_dir = args[i]
                print(f"Data folder set to '{data_dir}'.")
            else:
                print("Error: Missing data folder.")
                print_instructions()
                return
        elif arg in ('-c', '--convert-gpx'):
            convert_gpx = True
            print("GPX to GeoJSON conversion option activated.")
        elif arg in ('-g', '--geojson'):
            merge_geojson = True
            print("GeoJSON merge option activated.")
        else:
            print(f"Unknown option: {arg}")
            print_instructions()
            return
        i += 1

    # Create extraction directory
    extract_dir_jekyll = os.path.join(extract_dir, 'jekyll')
    extract_dir_html = os.path.join(extract_dir, 'html')
    try:
        Path(extract_dir).mkdir(parents=True, exist_ok=True)
        Path(extract_dir_jekyll).mkdir(parents=True, exist_ok=True)
        Path(extract_dir_html).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Could not create directory. {e}")
        return

    # Load trip data
    trip_file = os.path.join(data_dir, trip_filename)
    if not os.path.exists(trip_file):
        print(f"Error: Trip file '{trip_file}' not found.")
        print_instructions()
        return

    with open(trip_file, 'r', encoding='utf-8') as f:
        trip_data = json.load(f)

    # Convert GPX to GeoJSON if the option is activated
    if convert_gpx:
        gpx_dir = os.path.join(data_dir, 'gpx')
        geojson_dir = os.path.join(data_dir, 'geojson')
        convert_gpx_to_geojson(gpx_dir, geojson_dir)
        print(f"Converted GPX files in '{gpx_dir}' to GeoJSON format in '{geojson_dir}'.")
    if merge_geojson:
        geojson_dir = os.path.join(data_dir, 'geojson')
        merged_geojson_file = os.path.join(extract_dir_jekyll, trip_data['slug'], 'route.geojson')
        merge_geojson_files(geojson_dir, merged_geojson_file)
        print(f"Merged GeoJSON files into '{merged_geojson_file}'.")


    # Load location data
    map_file = os.path.join(data_dir, map_filename)
    loc_data = None
    if os.path.exists(map_file):
        with open(map_file, 'r', encoding='utf-8') as f:
            loc_data = json.load(f)
            print("Loaded location data for route mapping.")
    else:
        print(f"Warning: Locations file '{map_file}' not found. Route mapping will be unavailable.")

    # ###### Parse data ######
    steps_info = parse_data(trip_data, data_dir, extract_dir, verbose)

    # ###### Generate outputs ######
    if local:
        generate_html(trip_data, steps_info, loc_data, data_dir, extract_dir_html, verbose)
    if jekyll:
        generate_jekyll(trip_data, steps_info, loc_data, data_dir, extract_dir_jekyll, verbose)
    if mail or interactive:
        email_steps(trip_data, steps_info, dest_email, interactive)

def merge_geojson_files(geojson_dir, output_file):
    """Merge all GeoJSON files in a directory into a single GeoJSON file."""
    features = []
    for filename in os.listdir(geojson_dir):
        if filename.endswith('.geojson'):
            filepath = os.path.join(geojson_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                features.extend(data.get('features', []))

    # Sort features by time
    features.sort(key=lambda feature: feature['properties']['time'])

    merged_geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_geojson, f, ensure_ascii=False, indent=4)

def convert_gpx_to_geojson(gpx_dir, geojson_dir):
    """Convert all GPX files in a directory to GeoJSON format."""
    for filename in os.listdir(gpx_dir):
        if filename.endswith('.gpx'):
            filepath = os.path.join(gpx_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)
                features = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            feature = geojson.Feature(
                                geometry=geojson.Point((point.longitude, point.latitude)),
                                properties={
                                    "time": point.time.isoformat() if point.time else None,
                                    "elevation": point.elevation
                                }
                            )
                            features.append(feature)
                geojson_data = geojson.FeatureCollection(features)
                output_filename = os.path.splitext(filename)[0] + '.geojson'
                output_filepath = os.path.join(geojson_dir, output_filename)
                with open(output_filepath, 'w', encoding='utf-8') as out_f:
                    geojson.dump(geojson_data, out_f, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    main()
