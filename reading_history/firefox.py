import os
import shutil
import sqlite3
from datetime import datetime, timedelta

from reading_history.run_config import RunCache


class Firefox():
    def __init__(self, cache: RunCache):
        # Define the target directory
        self.target_dir = cache.cache
        self.db_path = os.path.join(self.target_dir, 'places.sqlite')

    def copy_places_db(self):
        # Verify the environment variable is set
        if 'FIREFOX_PROFILE_DIR' not in os.environ:
            print("FIREFOX_PROFILE_DIR is not set. Please set it and try again.")
            exit(1)

        places_db = os.path.join(os.environ["FIREFOX_PROFILE_DIR"], "places.sqlite")

        # Copy the new file to the target directory
        shutil.copy2(places_db, self.target_dir)

    def _get_time_range(self, day_timestamp: datetime) -> tuple:
        """Get the Firefox timestamps for the start and end of the specified day."""
        # Get the timestamp for "day_timestamp" at midnight (00:00:00)
        day_start = datetime.combine(day_timestamp, datetime.min.time())
        # Get the timestamp for "day_timestamp" at end of the day (23:59:59)
        day_end = datetime.combine(day_timestamp, datetime.max.time()) - timedelta(microseconds=1)
        # Convert day_start and day_end to Firefox's timestamp format (microseconds since epoch)
        firefox_start_ts = int(day_start.timestamp()) * 1_000_000
        firefox_end_ts = int(day_end.timestamp()) * 1_000_000
        # Return the Firefox timestamps as a tuple
        return firefox_start_ts, firefox_end_ts

    def read_history(self, day_timestamp: datetime) -> list:
        # Connect to the copied SQLite database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get the Firefox timestamps for the start and end of today
        today_start_ts, today_end_ts = self._get_time_range(day_timestamp)

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
