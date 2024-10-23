# src/data_parser.py

import os
import datetime
from dateutil import tz

weather_dict = {"rain": "\U0001F327", "clear-day": "\U0001F506", "partly-cloudy-day": "\U000026C5",  "snow": "\U000026C4", "cloudy": "\U00002601"}
   
country_dict = { #these countries denominations have been tested as used by PS in 2024/07
"Andorra":"\U0001F1E6\U0001F1E9","United Arab Emirates":"\U0001F1E6\U0001F1EA","Afghanistan":"\U0001F1E6\U0001F1EB","Antigua and Barbuda":"\U0001F1E6\U0001F1EC","Anguilla":"\U0001F1E6\U0001F1EE","Albania":"\U0001F1E6\U0001F1F1","Armenia":"\U0001F1E6\U0001F1F2","Angola":"\U0001F1E6\U0001F1F4","Antarctica":"\U0001F1E6\U0001F1F6","Argentina":"\U0001F1E6\U0001F1F7","Austria":"\U0001F1E6\U0001F1F9","Australia":"\U0001F1E6\U0001F1FA","Azerbaijan":"\U0001F1E6\U0001F1FF","Bosnia and Herzegovina":"\U0001F1E7\U0001F1E6","Barbados":"\U0001F1E7\U0001F1E7","Bangladesh":"\U0001F1E7\U0001F1E9","Belgium":"\U0001F1E7\U0001F1EA","Burkina Faso":"\U0001F1E7\U0001F1EB","Bulgaria":"\U0001F1E7\U0001F1EC","Bahrain":"\U0001F1E7\U0001F1ED","Burundi":"\U0001F1E7\U0001F1EE","Benin":"\U0001F1E7\U0001F1EF","Saint Barthelemy":"\U0001F1E7\U0001F1F1","Bermuda":"\U0001F1E7\U0001F1F2","Brunei":"\U0001F1E7\U0001F1F3","Bolivia":"\U0001F1E7\U0001F1F4","Brazil":"\U0001F1E7\U0001F1F7","Bahamas":"\U0001F1E7\U0001F1F8","Bhutan":"\U0001F1E7\U0001F1F9","Botswana":"\U0001F1E7\U0001F1FC","Belarus":"\U0001F1E7\U0001F1FE","Belize":"\U0001F1E7\U0001F1FF","Canada":"\U0001F1E8\U0001F1E6","Democratic Republic of the Congo":"\U0001F1E8\U0001F1E9","Central African Republic":"\U0001F1E8\U0001F1EB","Congo":"\U0001F1E8\U0001F1EC","Switzerland":"\U0001F1E8\U0001F1ED","Côte d'Ivoire":"\U0001F1E8\U0001F1EE","Cook Islands":"\U0001F1E8\U0001F1F0","Chile":"\U0001F1E8\U0001F1F1","Cameroon":"\U0001F1E8\U0001F1F2","China":"\U0001F1E8\U0001F1F3","Colombia":"\U0001F1E8\U0001F1F4","Costa Rica":"\U0001F1E8\U0001F1F7","Cuba":"\U0001F1E8\U0001F1FA","Cape Verde":"\U0001F1E8\U0001F1FB","Curacao":"\U0001F1E8\U0001F1FC","Cyprus":"\U0001F1E8\U0001F1FE","Czechia":"\U0001F1E8\U0001F1FF","Germany":"\U0001F1E9\U0001F1EA","Djibouti":"\U0001F1E9\U0001F1EF","Denmark":"\U0001F1E9\U0001F1F0","Dominica":"\U0001F1E9\U0001F1F2","Dominican Republic":"\U0001F1E9\U0001F1F4","Algeria":"\U0001F1E9\U0001F1FF","Ecuador":"\U0001F1EA\U0001F1E8","Estonia":"\U0001F1EA\U0001F1EA","Egypt":"\U0001F1EA\U0001F1EC","Sahrawi Arab Democratic Republic":"\U0001F1EA\U0001F1ED","Eritrea":"\U0001F1EA\U0001F1F7","Spain":"\U0001F1EA\U0001F1F8","Ethiopia":"\U0001F1EA\U0001F1F9","Finland":"\U0001F1EB\U0001F1EE","Fiji":"\U0001F1EB\U0001F1EF","Falkland Islands":"\U0001F1EB\U0001F1F0","Federated States of Micronesia":"\U0001F1EB\U0001F1F2","Faroe Islands":"\U0001F1EB\U0001F1F4","France":"\U0001F1EB\U0001F1F7","Gabon":"\U0001F1EC\U0001F1E6","United Kingdom":"\U0001F1EC\U0001F1E7","Grenada":"\U0001F1EC\U0001F1E9","Georgia":"\U0001F1EC\U0001F1EA","Guernsey":"\U0001F1EC\U0001F1EC","Ghana":"\U0001F1EC\U0001F1ED","Gibraltar":"\U0001F1EC\U0001F1EE","Greenland":"\U0001F1EC\U0001F1F1","The Gambia":"\U0001F1EC\U0001F1F2","Guinea":"\U0001F1EC\U0001F1F3","Equatorial Guinea":"\U0001F1EC\U0001F1F6","Greece":"\U0001F1EC\U0001F1F7","South Georgia and the South Sandwich Islands":"\U0001F1EC\U0001F1F8","Guatemala":"\U0001F1EC\U0001F1F9","Guinea-Bissau":"\U0001F1EC\U0001F1FC","Guyana":"\U0001F1EC\U0001F1FE","Hong Kong":"\U0001F1ED\U0001F1F0","Honduras":"\U0001F1ED\U0001F1F3","Croatia":"\U0001F1ED\U0001F1F7","Haiti":"\U0001F1ED\U0001F1F9","Hungary":"\U0001F1ED\U0001F1FA","Indonesia":"\U0001F1EE\U0001F1E9","Ireland":"\U0001F1EE\U0001F1EA","Israel":"\U0001F1EE\U0001F1F1","Isle of Man":"\U0001F1EE\U0001F1F2","India":"\U0001F1EE\U0001F1F3","British Indian Ocean Territory":"\U0001F1EE\U0001F1F4","Iraq":"\U0001F1EE\U0001F1F6","Iran":"\U0001F1EE\U0001F1F7","Iceland":"\U0001F1EE\U0001F1F8","Italy":"\U0001F1EE\U0001F1F9","Jersey":"\U0001F1EF\U0001F1EA","Jamaica":"\U0001F1EF\U0001F1F2","Jordan":"\U0001F1EF\U0001F1F4","Japan":"\U0001F1EF\U0001F1F5","Kenya":"\U0001F1F0\U0001F1EA","Kyrgyzstan":"\U0001F1F0\U0001F1EC","Cambodia":"\U0001F1F0\U0001F1ED","Kiribati":"\U0001F1F0\U0001F1EE","Comoros":"\U0001F1F0\U0001F1F2","Saint Kitts and Nevis":"\U0001F1F0\U0001F1F3","North Korea":"\U0001F1F0\U0001F1F5","South Korea":"\U0001F1F0\U0001F1F7","Kuwait":"\U0001F1F0\U0001F1FC","Cayman Islands":"\U0001F1F0\U0001F1FE","Kazakhstan":"\U0001F1F0\U0001F1FF","Laos":"\U0001F1F1\U0001F1E6","Lebanon":"\U0001F1F1\U0001F1E7","Saint Lucia":"\U0001F1F1\U0001F1E8","Liechtenstein":"\U0001F1F1\U0001F1EE","Sri Lanka":"\U0001F1F1\U0001F1F0","Liberia":"\U0001F1F1\U0001F1F7","Lesotho":"\U0001F1F1\U0001F1F8","Lithuania":"\U0001F1F1\U0001F1F9","Luxembourg":"\U0001F1F1\U0001F1FA","Latvia":"\U0001F1F1\U0001F1FB","Libya":"\U0001F1F1\U0001F1FE","Morocco":"\U0001F1F2\U0001F1E6","Monaco":"\U0001F1F2\U0001F1E8","Moldova":"\U0001F1F2\U0001F1E9","Montenegro":"\U0001F1F2\U0001F1EA","Saint Martin":"\U0001F1F2\U0001F1EB","Madagascar":"\U0001F1F2\U0001F1EC","Marshall Islands":"\U0001F1F2\U0001F1ED","North Macedonia":"\U0001F1F2\U0001F1F0","Mali":"\U0001F1F2\U0001F1F1","Myanmar":"\U0001F1F2\U0001F1F2","Mongolia":"\U0001F1F2\U0001F1F3","Mauritania":"\U0001F1F2\U0001F1F7","Montserrat":"\U0001F1F2\U0001F1F8","Malta":"\U0001F1F2\U0001F1F9","Mauritius":"\U0001F1F2\U0001F1FA","Maldives":"\U0001F1F2\U0001F1FB","Malawi":"\U0001F1F2\U0001F1FC","Mexico":"\U0001F1F2\U0001F1FD","Malaysia":"\U0001F1F2\U0001F1FE","Mozambique":"\U0001F1F2\U0001F1FF","Namibia":"\U0001F1F3\U0001F1E6","New Caledonia":"\U0001F1F3\U0001F1E8","Niger":"\U0001F1F3\U0001F1EA","Norfolk Island":"\U0001F1F3\U0001F1EB","Nigeria":"\U0001F1F3\U0001F1EC","Nicaragua":"\U0001F1F3\U0001F1EE","Netherlands":"\U0001F1F3\U0001F1F1","Norway":"\U0001F1F3\U0001F1F4","Nepal":"\U0001F1F3\U0001F1F5","Nauru":"\U0001F1F3\U0001F1F7","Niue":"\U0001F1F3\U0001F1FA","New Zealand":"\U0001F1F3\U0001F1FF","Oman":"\U0001F1F4\U0001F1F2","Panama":"\U0001F1F5\U0001F1E6","Peru":"\U0001F1F5\U0001F1EA","Papua New Guinea":"\U0001F1F5\U0001F1EC","Philippines":"\U0001F1F5\U0001F1ED","Pakistan":"\U0001F1F5\U0001F1F0","Poland":"\U0001F1F5\U0001F1F1","Pitcairn Islands":"\U0001F1F5\U0001F1F3","Puerto Rico":"\U0001F1F5\U0001F1F7","Palestinian Territory":"\U0001F1F5\U0001F1F8","Portugal":"\U0001F1F5\U0001F1F9","Palau":"\U0001F1F5\U0001F1FC","Paraguay":"\U0001F1F5\U0001F1FE","Qatar":"\U0001F1F6\U0001F1E6","Romania":"\U0001F1F7\U0001F1F4","Serbia":"\U0001F1F7\U0001F1F8","Russia":"\U0001F1F7\U0001F1FA","Rwanda":"\U0001F1F7\U0001F1FC","Saudi Arabia":"\U0001F1F8\U0001F1E6","Solomon Islands":"\U0001F1F8\U0001F1E7","Seychelles":"\U0001F1F8\U0001F1E8","Sudan":"\U0001F1F8\U0001F1E9","Sweden":"\U0001F1F8\U0001F1EA","Singapore":"\U0001F1F8\U0001F1EC","Saint Helena, Ascension and Tristan da Cunha":"\U0001F1F8\U0001F1ED","Slovenia":"\U0001F1F8\U0001F1EE","Slovakia":"\U0001F1F8\U0001F1F0","Sierra Leone":"\U0001F1F8\U0001F1F1","San Marino":"\U0001F1F8\U0001F1F2","Senegal":"\U0001F1F8\U0001F1F3","Somalia":"\U0001F1F8\U0001F1F4","Suriname":"\U0001F1F8\U0001F1F7","South Sudan":"\U0001F1F8\U0001F1F8","São Tomé and Príncipe":"\U0001F1F8\U0001F1F9","El Salvador":"\U0001F1F8\U0001F1FB","Sint Maarten":"\U0001F1F8\U0001F1FD","Syria":"\U0001F1F8\U0001F1FE","eSwatini":"\U0001F1F8\U0001F1FF","Turks and Caicos Islands":"\U0001F1F9\U0001F1E8","Chad":"\U0001F1F9\U0001F1E9","French Southern and Antarctic Lands":"\U0001F1F9\U0001F1EB","Togo":"\U0001F1F9\U0001F1EC","Thailand":"\U0001F1F9\U0001F1ED","Tajikistan":"\U0001F1F9\U0001F1EF","Tokelau":"\U0001F1F9\U0001F1F0","East Timor":"\U0001F1F9\U0001F1F1","Turkmenistan":"\U0001F1F9\U0001F1F2","Tunisia":"\U0001F1F9\U0001F1F3","Tonga":"\U0001F1F9\U0001F1F4","Turkey":"\U0001F1F9\U0001F1F7","Trinidad and Tobago":"\U0001F1F9\U0001F1F9","Tuvalu":"\U0001F1F9\U0001F1FB","Taiwan":"\U0001F1F9\U0001F1FC","Tanzania":"\U0001F1F9\U0001F1FF","Ukraine":"\U0001F1FA\U0001F1E6","Uganda":"\U0001F1FA\U0001F1EC","USA":"\U0001F1FA\U0001F1F8","Uruguay":"\U0001F1FA\U0001F1FE","Uzbekistan":"\U0001F1FA\U0001F1FF","Vatican City":"\U0001F1FB\U0001F1E6","Saint Vincent and the Grenadines":"\U0001F1FB\U0001F1E8","Venezuela":"\U0001F1FB\U0001F1EA","British Virgin Islands":"\U0001F1FB\U0001F1EC","US Virgin Islands":"\U0001F1FB\U0001F1EE","Vietnam":"\U0001F1FB\U0001F1F3","Vanuatu":"\U0001F1FB\U0001F1FA","Samoa":"\U0001F1FC\U0001F1F8","Kosovo":"\U0001F1FD\U0001F1F0","Yemen":"\U0001F1FE\U0001F1EA","South Africa":"\U0001F1FF\U0001F1E6","Zambia":"\U0001F1FF\U0001F1F2","Zimbabwe":"\U0001F1FF\U0001F1FC",
# additional denominations not identified as used by PS
"American Samoa":"\U0001F1E6\U0001F1F8","Aruba":"\U0001F1E6\U0001F1FC","Åland Islands":"\U0001F1E6\U0001F1FD","Bonaire, Sint Eustatius and Saba":"\U0001F1E7\U0001F1F6","Bouvet Island":"\U0001F1E7\U0001F1FB","Cocos (Keeling) Islands":"\U0001F1E8\U0001F1E8","Christmas Island":"\U0001F1E8\U0001F1FD","French Guiana":"\U0001F1EC\U0001F1EB","Guadeloupe":"\U0001F1EC\U0001F1F5","Guam":"\U0001F1EC\U0001F1FA","Heard Island and Mcdonald Islands":"\U0001F1ED\U0001F1F2","Macao":"\U0001F1F2\U0001F1F4","Northern Mariana Islands":"\U0001F1F2\U0001F1F5","Martinique":"\U0001F1F2\U0001F1F6","French Polynesia":"\U0001F1F5\U0001F1EB","Saint Pierre and Miquelon":"\U0001F1F5\U0001F1F2","Réunion":"\U0001F1F7\U0001F1EA","Svalbard and Jan Mayen":"\U0001F1F8\U0001F1EF","United States Minor Outlying Islands":"\U0001F1FA\U0001F1F2","Wallis and Futuna":"\U0001F1FC\U0001F1EB","Mayotte":"\U0001F1FE\U0001F1F9"}
 

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

        if step['country'] in country_dict:
            step['flag'] = country_dict[step['country']]
            print(step['flag'])
        else: 
            print(f"DEBUG: {location_country} not in country_dict")
            print(f"! Flag for country '{location_country}' not present !")

        step['weather'] = entry.get('weather_condition', '')
        step['temperature'] = entry.get('weather_temperature', '')

        if step['weather'] in weather_dict:
            step['weather_emoji'] = weather_dict[step['weather']]
        else:
            print(f"DEBUG: {step['weather']} not in weather_dict")
            print(f"! Emoji for weather '{step['weather']}' not present !")

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
