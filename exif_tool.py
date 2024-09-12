import os
import argparse
import shutil
import math
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

# Config ---------------------------------------------------------
SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png']
UNIT_CONVERSIONS = {
    'm': 1,            # meters
    'km': 1000,        # kilometers
    'mi': 1609.34,     # miles
    'ft': 0.3048,      # feet
    'yd': 0.9144,      # yards
    'ac': 63.614907234075, # acres
    'ha': 10000,       # hectares
}
# ----------------------------------------------------------------

# Constants ------------------------------------------------------
EARTH_RADIUS = 6371000
# ----------------------------------------------------------------

# EXIF helper functions ------------------------------------------
def extract_exif_data(image_path):
    """Extract EXIF data including DateTime and GPS information from an image."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return None, None
        exif = {}
        gps_info = {}
        for tag, value in exif_data.items():
            decoded_tag = TAGS.get(tag, tag)
            if decoded_tag == "GPSInfo":
                for gps_tag, gps_value in value.items():
                    gps_info[GPSTAGS.get(gps_tag, gps_tag)] = gps_value
            else:
                exif[decoded_tag] = value
        return exif, gps_info
    except Exception as e:
        print(f"Error extracting EXIF data from {image_path}: {e}")
        return None, None

def format_exif_datetime(exif_datetime, date_format="%Y-%m-%d_%H-%M-%S"):
    """Format the EXIF DateTime into the specified format."""
    if exif_datetime:
        try:
            return datetime.strptime(exif_datetime, "%Y:%m:%d %H:%M:%S").strftime(date_format)
        except ValueError:
            print(f"Could not parse EXIF date-time: {exif_datetime}")
            return None
    return None

def extract_gps_coordinates(gps_info):
    """Convert the GPS EXIF information into latitude and longitude."""
    if not gps_info:
        return None
    def convert_to_degrees(value):
        d, m, s = value[0], value[1], value[2]
        return d + (m / 60.0) + (s / 3600.0)

    lat = convert_to_degrees(gps_info.get('GPSLatitude')) if 'GPSLatitude' in gps_info else None
    lon = convert_to_degrees(gps_info.get('GPSLongitude')) if 'GPSLongitude' in gps_info else None
    lat_ref = gps_info.get('GPSLatitudeRef')
    lon_ref = gps_info.get('GPSLongitudeRef')

    if lat and lon and lat_ref and lon_ref:
        lat = lat if lat_ref == 'N' else -lat
        lon = lon if lon_ref == 'E' else -lon
        return (lat, lon)
    return None
# ----------------------------------------------------------------

# Math helper functions ------------------------------------------
def calculate_distance(coord1, coord2):
    """Calculate approximate distance (in meters) between two GPS coordinates (lat, lon)."""
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)

    # Haversine formula to calculate the distance between two lat/lon points
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS * c

def parse_radius(radius_str):
    """Parse radius with units (e.g., '1000m', '1km', '1mi') and return the value in meters."""
    match = re.match(r"(\d+(?:\.\d+)?)([a-zA-Z]*)", radius_str)
    if not match:
        raise ValueError(f"Invalid radius format: {radius_str}")
    
    value = float(match.group(1))
    unit = match.group(2).lower() if match.group(2) else 'm'  # default to meters if no unit specified

    if unit not in UNIT_CONVERSIONS:
        raise ValueError(f"Unsupported unit: {unit}")

    return value * UNIT_CONVERSIONS[unit]

# ----------------------------------------------------------------

# Filesystem helper functions ------------------------------------
def is_valid_image(file):
    """Check if the file has a supported image extension."""
    _, ext = os.path.splitext(file)
    return ext.lower() in SUPPORTED_EXTENSIONS

def preserve_folder_structure(input_folder, output_folder, root, file):
    """Generate the corresponding path in the output folder, preserving the directory structure."""
    relative_path = os.path.relpath(root, input_folder)  # Get the relative path from the input folder
    destination_dir = os.path.join(output_folder, relative_path)
    os.makedirs(destination_dir, exist_ok=True)  # Create the directories if they don't exist
    return os.path.join(destination_dir, file)

def group_images_by_location(input_folder, output_folder, recursive=False, radius=None):
    """Group images into folders based on their GPS coordinates, considering a radius if specified,
    while keeping the original folder structure."""
    
    for root, dirs, files in os.walk(input_folder):
        gps_groups = []

        for file in files:
            if not is_valid_image(file):
                continue
            file_path = os.path.join(root, file)
            exif, gps_info = extract_exif_data(file_path)
            if gps_info:
                gps_coordinates = extract_gps_coordinates(gps_info)
                if gps_coordinates:
                    # If radius is specified, group within the radius for each folder separately
                    if radius is not None:
                        grouped = False
                        for group in gps_groups:
                            if calculate_distance(group[0], gps_coordinates) <= radius:
                                group[1].append(file_path)
                                grouped = True
                                break
                        if not grouped:
                            gps_groups.append((gps_coordinates, [file_path]))
                    else:
                        gps_groups.append((gps_coordinates, [file_path]))

        # Now create folders for each group within the same folder structure
        if len(gps_groups) == 1:
            gps_coords, file_list = gps_groups[0]
            # Create folder for all images if they're in one group
            relative_path = os.path.relpath(root, input_folder)
            gps_folder = os.path.join(output_folder, relative_path, f"all_images_{gps_coords[0]:.6f}_{gps_coords[1]:.6f}")
            os.makedirs(gps_folder, exist_ok=True)
            for file_path in file_list:
                shutil.copy(file_path, gps_folder)
        else:
            for gps_coords, file_list in gps_groups:
                # Create a folder for each group based on GPS coordinates, keeping original folder structure
                relative_path = os.path.relpath(root, input_folder)
                gps_folder = os.path.join(output_folder, relative_path, f"{gps_coords[0]:.6f}_{gps_coords[1]:.6f}")
                os.makedirs(gps_folder, exist_ok=True)
                for file_path in file_list:
                    shutil.copy(file_path, gps_folder)

        if not recursive:
            break

def rename_images_by_datetime(input_folder, output_folder, date_format, recursive=False):
    """Rename images based on their EXIF DateTime metadata, preserving the original folder structure."""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if not is_valid_image(file):
                continue
            file_path = os.path.join(root, file)
            exif, _ = extract_exif_data(file_path)
            if exif:
                exif_datetime = exif.get('DateTime')
                formatted_date = format_exif_datetime(exif_datetime, date_format)
                if formatted_date:
                    # Preserve folder structure when renaming
                    output_path = preserve_folder_structure(input_folder, output_folder, root, formatted_date + os.path.splitext(file)[1])
                    shutil.copy(file_path, output_path)

        if not recursive:
            break
# ----------------------------------------------------------------

# Main CLI function ----------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description=(
            "A command-line tool to process images using EXIF data.\n\n"
            "Features:\n"
            "  1. Rename images based on their EXIF date-time metadata.\n"
            "  2. Group images into folders by their GPS coordinates from EXIF data.\n"
            "  Operations are mutually exclusive: use either --rename or --group, not both."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Example usage:\n"
            "  Rename images based on EXIF DateTime:\n"
            "    python exif_tool.py input_folder output_folder --rename\n\n"
            "  Group images by GPS location:\n"
            "    python exif_tool.py input_folder output_folder --group --radius 1000m\n"
        )
    )
    
    parser.add_argument(
        'input_folder', 
        type=str, 
        help='Path to the input folder containing images.'
    )
    parser.add_argument(
        'output_folder', 
        type=str, 
        help='Path to the output folder where processed images will be saved.'
    )
    parser.add_argument(
        '-r', '--recursive', 
        action='store_true', 
        help='Process subfolders recursively.'
    )
    parser.add_argument(
        '-n', '--rename', 
        action='store_true', 
        help='Rename images based on their EXIF DateTime information.'
    )
    parser.add_argument(
        '-f', '--format', 
        type=str, 
        default="%Y-%m-%d_%H-%M-%S", 
        help='Specify the date format for renaming (default: "%%Y-%%m-%%d_%%H-%%M-%%S").'
    )
    parser.add_argument(
        '-g', '--group', 
        action='store_true', 
        help='Group images into folders based on GPS coordinates from EXIF data.'
    )
    parser.add_argument(
        '--radius', 
        type=str, 
        help='Specify the radius (e.g., "1000m", "1km", "0.5mi") to group images by location.'
    )
    
    args = parser.parse_args()

    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        return
    
    os.makedirs(args.output_folder, exist_ok=True)

    radius_in_meters = None
    if args.radius:
        try:
            radius_in_meters = parse_radius(args.radius)
        except ValueError as e:
            print(e)
            return

    if args.rename:
        print("Renaming images by EXIF date-time...")
        rename_images_by_datetime(args.input_folder, args.output_folder, args.format, args.recursive)
    
    elif args.group:
        print("Grouping images by location...")
        group_images_by_location(args.input_folder, args.output_folder, args.recursive, radius_in_meters)
    
    else:
        print("No operation specified. Use --rename or --group.")

# ----------------------------------------------------------------

if __name__ == "__main__":
    main()
