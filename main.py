import argparse
import asyncio
from datetime import datetime

import dateparser
from dotenv import load_dotenv

from reading_history import app
from reading_history.firefox import Firefox
from reading_history.run_config import RunConfig, RunCache

load_dotenv()


def parse_arguments() -> dict:
    parser = argparse.ArgumentParser(description='This script parses the history.')
    parser.add_argument('--date', type=str, help='Optional. Add a custom date for which to parse the history. '
                                                 'Strings like "yesterday" will work.')
    args = parser.parse_args()

    return {"date": dateparser.parse(args.date) if args.date else datetime.now()}


def cleanup_cache(cache: RunCache) -> None:
    print('Cleaning up...')
    cache.delete_caches()


async def main():
    args = parse_arguments()
    run_config = RunConfig(date=args['date'])
    cache = RunCache(run_config.run_id)

    await app.run()
    cleanup_cache(cache)


if __name__ == '__main__':
    asyncio.run(main())
