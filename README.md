# Kleinanzeigen Web Scraper

A Python-based web scraping tool that monitors [Kleinanzeigen](https://www.kleinanzeigen.de/) listings for specific items and tracks their availability and price changes. The scraper is particularly useful exploring a 'real' price of a specific Item, by checking availability of once uploaded Items.

## Features

- Automated scraping of Kleinanzeigen listings at configurable intervals
- Tracking of item status (sold, paused, deleted, expired)
- SQLite database storage for historical data
- Configurable blacklist to filter unwanted listings
- Special handling for vehicle listings (including mileage tracking)
- Webapp for Configuration and Visaulizing scraped Data

## Prerequisites

- Python 3.x
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  - `schedule`
  - `streamlit`
  - `sqlite3` (typically included with Python)

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install requests beautifulsoup4 schedule
```

## Configuration

### traced_objects.json

Configure the items you want to track in `traced_objects.json`. Example structure:

```json
[
    {
        "name": "ducati_hypermotard",
        "url": "https://www.kleinanzeigen.de/s-motorraeder-roller/hypermotard-1100/...",
        "checks_per_day": 1,
        "kfz": true,
        "blacklist": ["SP", "EVO", "bastler", "defekt", "teileträger", "suche"]
    }
]
```

Parameters:
- `name`: Unique identifier for the tracked item (used in database tables)
- `url`: Kleinanzeigen search URL
- `checks_per_day`: Number of times to check the listings per day
- `kfz`: Set to `true` for vehicle listings (enables mileage tracking)
- `blacklist`: List of keywords to filter out unwanted listings

**You can also use the Configuration Interface via browser. For more information jump to `Webinterface`**

## Project Structure

- `index.py`: Main Page for Webinterface
  - `config_generator.py`: Page for editing the Scraper Configuartion
  - `Visualizer.py`: Page for Visualizing DB Entries
- `scraper.py`: Web scraping implementation
- `traced_objects.json`: Configuration file
- `db_utils.py`: Database operations and management

## Usage

### Run the scraper:

```bash
python main.py
```

The scraper will:
1. Initialize database tables for each tracked item
2. Set up scheduled checks based on `checks_per_day`
3. Continuously monitor listings and update the database
4. Track when items are sold/removed and store duration information

### Run Webinterface:

```bash
streamlit run index.py
```
By using this command, a local webserver is initialized. The console will present the local IP for accessing via browser.

## Database Structure

For each tracked item, a table is created, with following columns:

- ID
- Title
- Price
- User ID
- sold
- Timestamp
- Days online
- Kilometers (for vehicles)

## Webinterface

After starting the Webserver, there are different utilities available.

### Scraper Configuration

Selecting the Scraper Configuration window, you have the oppotunity for editing the `traced_objects.json`. The suraface is self-declaring...

### Visualizing Data

In this Tab you're able to choose one of the traced objects, plot the corresponding stats. Below the plot are the most important statistical measures listed.

## Notes

- Please respect Kleinanzeigen's terms of service and rate limits
- The scraper uses a desktop browser User-Agent to avoid blocking
- Consider adding proxy support for extensive scraping
