# Plex Watchlist to ICS

Convert your Plex watchlist into an iCalendar (.ics) file with randomly scheduled movie nights.

## What it does

This script:
1. Fetches movies from your Plex watchlist RSS feed
2. Randomly selects a specified number of movies (default: 2)
3. Schedules them on random days of the week
4. Exports the schedule to an `.ics` file compatible with Calendar, Google Calendar, Outlook, etc.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/the8thsign/plex_watchlist_to_ics.git
cd plex_watchlist_to_ics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Getting your Plex Watchlist Feed URL

1. Go to [https://rss.plex.tv/](https://rss.plex.tv/)
2. Sign in with your Plex account
3. Select your library to generate your personal RSS feed URL
4. Copy the URL (it will look like `https://rss.plex.tv/YOUR_ID`)

## Usage

### Basic usage
```bash
python3 plex_watchlist_to_ics.py --feed "https://rss.plex.tv/YOUR_ID" --out plex_movies.ics
```

### Optional parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--feed` | (required) | Your Plex watchlist RSS feed URL |
| `--out` | `plex_movies.ics` | Output .ics file path |
| `--count` | `2` | Number of movies to schedule |
| `--start` | `20:30` | Start time in 24-hour format (HH:MM) |
| `--duration` | `120` | Movie duration in minutes |
| `--week` | `this` | Schedule in `this` or `next` week |
| `--tzid` | `America/New_York` | Timezone for events (IANA timezone format) |
| `--seed` | (none) | Optional random seed for reproducible results |

### Examples

Schedule 3 movies for next week, starting at 7 PM, 2.5 hours each:
```bash
python3 plex_watchlist_to_ics.py \
  --feed "https://rss.plex.tv/YOUR_ID" \
  --out plex_movies.ics \
  --count 3 \
  --start "19:00" \
  --duration 150 \
  --week next
```

Schedule movies in Pacific time:
```bash
python3 plex_watchlist_to_ics.py \
  --feed "https://rss.plex.tv/YOUR_ID" \
  --out plex_movies.ics \
  --tzid "America/Los_Angeles"
```

## Output

The generated `.ics` file can be imported into:
- Apple Calendar
- Google Calendar
- Microsoft Outlook
- Any application that supports iCalendar format

Each event includes:
- Movie title with 🎬 emoji
- Scheduled date and time
- Duration
- Movie description and link (if available)

## License

See LICENSE file for details.
