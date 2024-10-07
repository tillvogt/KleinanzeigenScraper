# Kleinanzeigen Web Scraper

A Python-based web scraping tool that monitors [Kleinanzeigen](https://www.kleinanzeigen.de/) listings for specific items and tracks their availability and price changes. The scraper is particularly useful for monitoring vehicle listings (cars and motorcycles) but can be adapted for other categories.

## Features

- Automated scraping of Kleinanzeigen listings at configurable intervals
- Tracking of item status (sold, paused, deleted, expired)
- SQLite database storage for historical data
- Configurable blacklist to filter unwanted listings
- Special handling for vehicle listings (including mileage tracking)
- Multiple item tracking through JSON configuration

## Prerequisites

- Python 3.x
- Required Python packages:
  - `requests`
  - `beautifulsoup4`
  - `schedule`
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

## Project Structure

- `main.py`: Entry point and scheduling logic
- `scraper.py`: Web scraping implementation
- `data_manager.py`: Database operations and management
- `traced_objects.json`: Configuration file

## Usage

Run the scraper:

```bash
python main.py
```

The scraper will:
1. Initialize database tables for each tracked item
2. Set up scheduled checks based on `checks_per_day`
3. Continuously monitor listings and update the database
4. Track when items are sold/removed and store duration information

## Database Structure

For each tracked item, two tables are created:
1. Main table (`{name}`): Current active listings
2. Sold table (`{name}_sold`): Historical data of sold/removed items

Fields include:
- ID
- Title
- Price
- Price Type
- User ID
- Kilometers (for vehicles)
- Timestamp
- Duration (for sold items)

## Error Handling

The scraper includes:
- Request rate limiting (2-second delay between requests)
- Error logging
- Exception handling for network issues
- Duplicate entry prevention

## Notes

- Please respect Kleinanzeigen's terms of service and rate limits
- The scraper uses a desktop browser User-Agent to avoid blocking
- Consider adding proxy support for extensive scraping
