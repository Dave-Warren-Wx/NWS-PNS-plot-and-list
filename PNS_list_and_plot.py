import csv
import os
import re

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "../../data/raw/PNS_metadata.txt"

OUTPUT_DIR = "../../data/output"

CSV_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "weather_observations.csv"
)

NAV_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "nav_weather_observations.csv"
)

# ============================================================
# FIND POSSIBLE LOCATION COMMAS
# ============================================================

def find_possible_location_commas(lines):
    """
    Look for commas inside the location field.

    A normal PNS line has:
        date,time,state,county,location, , ,lat,lon,...

    If there is another comma before the two blank fields,
    the location itself contains a comma.
    """

    problems = []

    for line_number, line in enumerate(lines, start=1):

        line = line.strip()

        if not line:
            continue

        if line.startswith(":"):
            line = line[1:]

        text = line

        # Look for the latitude/longitude portion.
        coord_match = re.search(
            r",\s*(-?\d+(?:\.\d+)?)\s*,\s*"
            r"(-?\d+(?:\.\d+)?)\s*,\s*RAIN\s*,",
            text
        )

        if not coord_match:
            continue

        before_coords = text[:coord_match.start()]

        # Remove the first four fields:
        # date, time, state, county
        first_four = before_coords.split(",", 4)

        if len(first_four) < 5:
            continue

        location_section = first_four[4]

        # A normal location has the two empty fields:
        # location, , ,
        #
        # If there is another comma before those empty fields,
        # flag it.
        parts = location_section.split(",")

        if len(parts) > 3:
            problems.append(
                (line_number, line)
            )

    return problems


# ============================================================
# PARSE PNS LINE
# ============================================================

def parse_line(line):
    """
    Parse one PNS metadata line.

    Uses the latitude/longitude position rather than assuming
    the location itself never contains a comma.
    """

    line = line.strip()

    if not line:
        return None

    if line.startswith(":"):
        line = line[1:]

    # Find latitude, longitude, phenomenon and rainfall.
    match = re.search(
        r"^(.*?),\s*(-?\d+(?:\.\d+)?)\s*,\s*"
        r"(-?\d+(?:\.\d+)?)\s*,\s*"
        r"([^,]+)\s*,\s*"
        r"([-+]?\d*\.?\d+)\s*,\s*"
        r"([^,]+)\s*,\s*"
        r"([^,]+)\s*,",
        line
    )

    if not match:
        return None

    before_coordinates = match.group(1)

    latitude = float(match.group(2))
    longitude = float(match.group(3))
    phenomenon = match.group(4).strip()
    amount = match.group(5).strip()
    amount_numeric = float(amount)
    unit = match.group(6).strip()
    source = match.group(7).strip()

    # Split the beginning into:
    # date, time, state, county, location
    fields = before_coordinates.split(",", 4)

    if len(fields) != 5:
        return None

    date = fields[0].strip()
    time = fields[1].strip()
    state = fields[2].strip()
    county = fields[3].strip()
    location = fields[4].strip()

    # Remove the two empty PNS fields after the location.
    location = re.sub(r",\s*,\s*$", "", location).strip()

    # Remove distance/direction from the beginning.
    # Example: "2 WSW Lighthouse Point" -> "Lighthouse Point"
    location = re.sub(
        r"^\d+(?:\.\d+)?\s+"
        r"(?:N|NNE|NE|ENE|E|ESE|SE|SSE|S|SSW|SW|WSW|W|WNW|NW|NNW)"
        r"\s+",
        "",
        location,
        flags=re.IGNORECASE
    )

    # Remove distance/direction from the end.
    # Example: "Lighthouse Point 2 WSW" -> "Lighthouse Point"
    location = re.sub(
        r"\s+\d+(?:\.\d+)?\s+"
        r"(?:N|NNE|NE|ENE|E|ESE|SE|SSE|S|SSW|SW|WSW|W|WNW|NW|NNW)$",
        "",
        location,
        flags=re.IGNORECASE
    ).strip()

    # Remove station codes from the beginning.
    # Example: "KB1DML-3 Rockport" -> "Rockport"
    location = re.sub(
        r"^[A-Z0-9]+(?:-[A-Z0-9]+)?\s+",
        "",
        location
    ).strip()

    return {
        "date": date,
        "time": time,
        "state": state,
        "county": county,
        "location": location,
        "lat": latitude,
        "lon": longitude,
        "phenomenon": phenomenon,
        "amount": amount,
        "amount_numeric": amount_numeric,
        "unit": unit,
        "source": source
    }


# ============================================================
# MAIN
# ============================================================

print()
print("==============================================")
print(" NWS PNS METADATA -> WEATHER CSV")
print("==============================================")
print()

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file was not found:")
    print(INPUT_FILE)
    print()
    input("Press ENTER to exit...")
    raise SystemExit


# ------------------------------------------------------------
# Read input
# ------------------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()


# ------------------------------------------------------------
# Check for unusual commas
# ------------------------------------------------------------

comma_problems = find_possible_location_commas(lines)

if comma_problems:

    print("WARNING: Possible comma inside a location field.")
    print()
    print("These lines should be checked before continuing:")
    print()

    for line_number, line in comma_problems:
        print(f"Line {line_number}:")
        print(line)
        print()

    print("----------------------------------------------")
    print("If these locations are correct, you can")
    print("continue.")
    print()
    print("If they need to be changed, edit:")
    print(INPUT_FILE)
    print()
    input("Press ENTER to continue...")
    print()


# ------------------------------------------------------------
# Parse records
# ------------------------------------------------------------

records = []

for line in lines:
    record = parse_line(line)

    if record is None:
        continue

    records.append(record)


# ---------------------------------------------
# Find available report types
# ---------------------------------------------
report_types = sorted(
    set(record["phenomenon"].upper() for record in records)
)

if len(report_types) == 0:
    print("No valid reports found.")
    raise SystemExit

if len(report_types) == 1:

    selected_type = report_types[0]

else:

    print("Available report types:")
    print()

    for number, report_type in enumerate(report_types, start=1):
        print(f"{number}. {report_type}")

    print()

    while True:

        choice = input(
            "What type of report do you want to plot? "
        )

        try:
            choice = int(choice)

            if 1 <= choice <= len(report_types):
                selected_type = report_types[choice - 1]
                break

        except ValueError:
            pass

        print("Please enter a valid number.")

    print()
    
# ---------------------------------------------
# Ask whether to include state abbreviations
# in the regular list CSV
# ---------------------------------------------
include_state = input(
    "Include state abbreviations in location names? (Y/N): "
).strip().upper()

include_state = include_state == "Y"

print()    

# ---------------------------------------------
# Keep only the selected report type
# ---------------------------------------------
records = [
    record
    for record in records
    if record["phenomenon"].upper() == selected_type
]

# ------------------------------------------------------------
# Sort by amount descending
# ------------------------------------------------------------

records.sort(
    key=lambda x: x["amount_numeric"],
    reverse=True
)


# ------------------------------------------------------------
# Make output directory
# ------------------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# REGULAR CSV - TOP 10 OVERALL
# ============================================================

top_10 = sorted(
    records,
    key=lambda x: x["amount_numeric"],
    reverse=True
)[:10]

with open(
    CSV_OUTPUT,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    f.write(
        "city_name," +
        selected_type +
        "\r\n"
    )

    for record in top_10:

        location = record["location"]

        if include_state:
            location = location + " " + record["state"]

        f.write(
            location +
            "," +
            record["amount"] +
            "\r\n"
        )

# ============================================================
# NAV CSV
# ============================================================

with open(
    NAV_OUTPUT,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
      "Station ID",
      "Name",
      "Lat",
      "Lon",
      selected_type
    ])

    report_number = 0

    for record in records:

        report_number += 1

        station_id = f"S{report_number:03d}"

        writer.writerow([
            station_id,
            record["location"],
            record["lat"],
            record["lon"],
            record["amount"]
        ])

# ============================================================
# SUMMARY
# ============================================================

print()
print("==============================================")
print(" COMPLETE")
print("==============================================")
print()
print(f"Records processed: {len(records)}")
print()

