import os
import shutil
import sqlite3
from datetime import datetime, timedelta

from reading_history.run_config import RunConfig, RunCache

# Define the target directory
target_dir = RunCache(RunConfig().run_id).cache
db_path = os.path.join(target_dir, 'places.sqlite')


def copy_places_db():
    # Verify the environment variable is set
    if 'FIREFOX_PROFILE_DIR' not in os.environ:
        print("FIREFOX_PROFILE_DIR is not set. Please set it and try again.")
        exit(1)

    places_db = os.path.join(os.environ["FIREFOX_PROFILE_DIR"], "places.sqlite")

    # Copy the new file to the target directory
    shutil.copy2(places_db, target_dir)


def read_history(day_timestamp: datetime = datetime.today()) -> list:
    # Connect to the copied SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get the timestamp for "today" at midnight (00:00:00)
    today_midnight = datetime.combine(day_timestamp, datetime.min.time())
    # Get the timestamp for "today" at end of the day (23:59:59)
    today_end = datetime.combine(day_timestamp, datetime.max.time()) - timedelta(microseconds=1)

    # Convert today_midnight to Firefox's timestamp format (microseconds since epoch)
    today_start_ts = int(today_midnight.timestamp()) * 1_000_000
    # Convert today_end to Firefox's timestamp format (microseconds since epoch)
    today_end_ts = int(today_end.timestamp()) * 1_000_000

    cur.execute("""
        SELECT DISTINCT url
        FROM moz_places
            Left Join main.moz_places_metadata mpm on moz_places.id = mpm.place_id
        WHERE last_visit_date >= ?
            AND last_visit_date < ?
            AND mpm.scrolling_time > 0
        ORDER BY length(url), url DESC
    """, (today_start_ts, today_end_ts))

    urls = [url[0] for url in cur]

    # Close the connection
    cur.close()
    conn.close()

    return urls
