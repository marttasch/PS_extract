#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script to extract data from Polarsteps JSON files and generate outputs.
"""
import sys
import os
from pathlib import Path
import json
from src.data_parser import parse_data
from src.html_generator import generate_html
from src.email_utils import email_steps, send_trip_email

# Global parameters
extract_dir = "Extracts"
data_dir = "data"
trip_file = os.path.join(data_dir, 'trip.json')
map_file = os.path.join(data_dir, 'locations.json')

# Set all specific run modes of the script to False; will be modified through command-line arguments
mail = False
local = False
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
    -e, --email address@domain.com Send emails containing descriptions, images, and videos to the given address
    -i, --interactive              Display an analysis and interactively ask what to do for each step
    -x, --exclude                  Exclude the first and last steps from generated maps
    -h, --help                     Display this help message
""")

def main():
    global mail, local, interactive, verbose, exclude, dest_email

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
        elif arg in ('-i', '--interactive'):
            interactive = True
            print("Interactive option activated.")
        elif arg in ('-v', '--verbose'):
            verbose = True
            print("Verbose option activated.")
        elif arg in ('-x', '--exclude'):
            exclude = True
            print("Exclude option activated.")
        elif arg in ('-h', '--help'):
            print_instructions()
            return
        else:
            print(f"Unknown option: {arg}")
            print_instructions()
            return
        i += 1

    # Create extraction directory
    try:
        Path(extract_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error: Could not create directory '{extract_dir}'. {e}")
        return

    # Load trip data
    if not os.path.exists(trip_file):
        print(f"Error: Trip file '{trip_file}' not found.")
        print_instructions()
        return

    with open(trip_file, 'r', encoding='utf-8') as f:
        trip_data = json.load(f)

    # Load location data
    loc_data = None
    if os.path.exists(map_file):
        with open(map_file, 'r', encoding='utf-8') as f:
            loc_data = json.load(f)
            print("Loaded location data for route mapping.")
    else:
        print(f"Warning: Locations file '{map_file}' not found. Route mapping will be unavailable.")

    # Parse data
    steps_info = parse_data(trip_data, data_dir, extract_dir, verbose)

    # Generate outputs
    if local:
        generate_html(trip_data, steps_info, loc_data, extract_dir, verbose)
    if mail or interactive:
        email_steps(trip_data, steps_info, dest_email, interactive)

if __name__ == "__main__":
    main()
