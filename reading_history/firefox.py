import os
import shutil
import sqlite3
from datetime import datetime

# Define the target directory
target_dir = os.path.realpath('./places')
db_path = os.path.join(target_dir, 'places.sqlite')


def copy_places_db():
    # Verify the environment variable is set
    if 'FIREFOX_PROFILE_DIR' not in os.environ:
        print("FIREFOX_PROFILE_DIR is not set. Please set it and try again.")
        exit(1)

    # Backup the existing file if it exists
    if os.path.isfile(db_path):
        # Define the backup file path
        backup_file_path = os.path.join(target_dir, f"places.sqlite.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        # Rename (move) the old file to the backup file
        shutil.move(db_path, backup_file_path)

    places_db = os.path.join(os.environ["FIREFOX_PROFILE_DIR"], "places.sqlite")

    # Copy the new file to the target directory
    shutil.copy2(places_db, target_dir)


def read_history():
    # Connect to the copied SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get the timestamp for "today" at midnight (00:00:00)
    today_midnight = datetime.combine(datetime.today(), datetime.min.time())
    # Convert today_midnight to Firefox's timestamp format (microseconds since epoch)
    today_midnight_ts = int(today_midnight.timestamp()) * 1_000_000

    cur.execute("""
        SELECT DISTINCT url, title, description
        FROM moz_places
            Left Join main.moz_places_metadata mpm on moz_places.id = mpm.place_id
        WHERE last_visit_date >= ?
            AND mpm.scrolling_time > 0
        ORDER BY length(url), url DESC
    """, (today_midnight_ts,))

    urls = cur.fetchall()

    # Close the connection
    cur.close()
    conn.close()

    return urls
