# PNS Weather Observation Converter

A Python utility for converting observation data from **National Weather Service (NWS) Public Information Statements (PNS)** into CSV files for broadcast weather graphics.

The script was developed to solve a practical broadcast workflow problem: taking observation data contained in an NWS PNS product and quickly converting it into formats that can be used for weather graphics and navigation.

## What It Does

The script can:

* Read PNS observation metadata from a text file
* Process data from **multiple NWS offices in the same input file**
* Automatically identify the available report types
* Allow the user to select which report type to output
* Preserve the original observation value formatting
* Identify and help locate possible comma problems in location names
* Clean common station identifiers from displayed location names
* Optionally add the state abbreviation to locations in the regular list CSV
* Create a ranked list of the highest observations
* Create a full Navigated (NAV) CSV containing all observations
* Automatically copy the output files to configured network destinations

The same script can be used for rainfall, peak wind gusts, and other observation types contained in PNS products.

---

## Input

The input is a text file containing the observation metadata from an NWS PNS product.

For example:

```text
**METADATA**

09/26/2026, 0853 PM, MA, Norfolk, Norwood, Norwood Memorial Airport, , , 42.19083, -71.17389, RAIN, 2.003, Inch, ASOS/AWOS, Storm total rainfall,
```

The script does not require the `**METADATA**` heading to be removed. It is automatically ignored.

The input file can contain observations from **multiple NWS offices and multiple states**.

For example, observations from Boston, New York, and Philadelphia can be combined into one input file and processed together.

---

## Selecting the Report Type

After reading the input, the script identifies the available observation types.

Example:

```text
Available report types:

1. PKGUST
2. RAIN
3. RAIN_24

What type of report do you want to plot?
```

The user selects the desired report type.

This allows the same input file to be used for different graphics without changing the code.

---

## State Abbreviations

The script optionally asks:

```text
Include state abbreviations in location names? (Y/N):
```

If enabled, the regular list CSV can produce:

```text
city_name,PKGUST
Montauk Point NY,81
New Shoreham RI,71
Wellfleet MA,70
Nantucket MA,62
```

If disabled:

```text
city_name,PKGUST
Montauk Point,81
New Shoreham,71
Wellfleet,70
Nantucket,62
```

The state abbreviation comes directly from the NWS observation data.

This option applies to the **regular list CSV only**. The NAV CSV is not modified by this setting.

---

## Location Comma Detection

PNS observation data is comma-delimited. Occasionally, a location name can also contain a comma, which can make it difficult to determine where the location field ends and the remaining observation fields begin.

For example:

```text
Nantucket, Nantucket Memorial Airport
```

The script includes a check for possible extra commas in location fields.

When a possible problem is identified, the location can be manually cleaned in the source `PNS_metadata.txt` file before running the script.

For example:

```text
Nantucket, Nantucket Memorial Airport
```

can be changed to:

```text
Nantucket - Nantucket Memorial Airport
```

This keeps the location as a single field while preserving the useful location information.

The same approach can be used for other locations where the name itself contains a comma.

The parser does not attempt to automatically guess how every unusual location name should be interpreted. Instead, questionable locations can be identified and corrected in the source data, keeping the processing logic simple and predictable.

---

## Location Cleanup

The script removes common station identifiers from the beginning of location names when a recognizable location follows.

For example:

```text
FW8194 New Shoreham
```

becomes:

```text
New Shoreham
```

and:

```text
KB1DML-3 Rockport
```

becomes:

```text
Rockport
```

Other station identifiers may be handled in the same way when they appear before a human-readable location.

Standalone identifiers are not given invented names. If the input only provides something such as:

```text
WFT46484
```

the script leaves it as-is rather than guessing the location.

---

## Observation Precision

The script preserves the value formatting supplied by the NWS data.

For example:

```text
2.003
2.94
41
49
```

are not automatically converted to two decimal places.

The numeric value is also retained internally so observations can be properly ranked.

---

## Output 1 — Regular List CSV

The regular CSV is designed for quick use in broadcast graphics.

It contains the **top 10 observations**, ranked from highest to lowest.

Example:

```text
city_name,PKGUST
Montauk Point NY,81
New Shoreham RI,71
Wellfleet MA,70
Nantucket MA,62
Rockport MA,61
```

The number of observations can be easily changed in the script if needed.

The regular CSV is intended to provide a clean, concise list for a graphic.

---

## Output 2 — Navigated (NAV) CSV

The NAV CSV contains **all observations**, rather than just the top 10.

It is intended for use with navigation-based weather graphics systems.

The NAV CSV must follow a specific column structure:

```text
Station ID,Name,Lat,Lon,PKGUST
S001,Montauk Point,41.07,-71.86,81
S002,New Shoreham,41.15,-71.55,71
S003,Wellfleet,41.94,-69.98,70
```

The report type becomes the final column heading automatically.

For example:

```text
Station ID,Name,Lat,Lon,RAIN
```

or:

```text
Station ID,Name,Lat,Lon,PKGUST
```

### NAV CSV Requirements

The NAV output uses:

* `Station ID`
* `Name`
* `Lat`
* `Lon`
* Selected report type

Station IDs are generated automatically:

```text
S001
S002
S003
...
```

The NAV observations are ranked from highest to lowest value.

This makes it easy to remove observations below a desired threshold before importing the file into the graphics system.

For example, if only observations of 50 mph or greater are wanted, lower observations can simply be removed from the NAV CSV.

Multiple observations from the same station are preserved when they occur in the source PNS data.

---

## Testing Multiple NWS Offices

The parser is designed to treat the input as one observation pool, even when data from multiple NWS offices is combined into a single file.

During testing, observation data from:

* Boston
* New York
* Philadelphia

was combined into one `PNS_metadata.txt` file.

The combined test contained hundreds of source lines and successfully processed more than 200 valid observations.

The test included:

* Multiple NWS offices
* Multiple states
* Multiple report types
* Different station identifiers
* Different location formats
* Peak wind gust observations
* Rainfall observations
* Locations with and without station identifiers
* Different observation value precision

This demonstrated that the parser is not limited to a single NWS office or a single geographic area.

---

## File Setup

The basic project structure is:

```text
project/
│
├── data/
│   ├── raw/
│   │   └── PNS_metadata.txt
│   │
│   └── output/
│       ├── weather_observations.csv
│       └── nav_weather_observations.csv
│
└── src/
    └── weather_graphics/
        └── pns_rainfall.py
```

The script uses relative paths so the project can be moved to another computer without changing hard-coded local paths.

---

## Using the Script

1. Obtain the observation metadata from an NWS PNS product.
2. Place the metadata in:

```text
data/raw/PNS_metadata.txt
```

3. Run the Python script.
4. Select the desired report type when prompted.
5. Choose whether state abbreviations should be included in the regular list CSV.
6. The script creates both CSV outputs.
7. Review the NAV CSV and remove observations below any desired threshold.
8. The output files can then be used by the broadcast graphics system.

---

## Broadcast Workflow

The resulting workflow is:

```text
NWS PNS
   ↓
PNS Metadata
   ↓
PNS Metadata Text File
   ↓
Python Parser
   ↓
┌─────────────────────────┬─────────────────────────┐
│ Regular CSV             │ NAV CSV                 │
│                         │                         │
│ Top 10                  │ All observations        │
│ Ranked                  │ Ranked                  │
│ Optional state          │ Station IDs             │
│ Broadcast list          │ Latitude / Longitude    │
└─────────────────────────┴─────────────────────────┘
             ↓                       ↓
      Broadcast List          Weather Graphics
```

The goal is not to replace the NWS product.

The goal is to automate the conversion of useful observation data into formats that can be quickly used in a broadcast graphics workflow.

---

## Why This Tool Was Built

NWS PNS products contain valuable real-time observation information, but the data is not always immediately formatted for use in a broadcast graphics system.

This tool bridges that gap by:

* Parsing the PNS observation metadata
* Identifying the desired observation type
* Cleaning common formatting issues
* Ranking observations
* Preserving useful geographic information
* Producing a simple broadcast list
* Producing a structured navigation CSV

The project demonstrates how Python can be used to automate a specific meteorological and broadcast workflow rather than requiring the data to be manually reformatted each time.
