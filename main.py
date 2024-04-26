import asyncio

from dotenv import load_dotenv

from reading_history import app, firefox
from reading_history.run_config import RunConfig, RunCache

load_dotenv()


async def main():
    run_id = RunConfig().run_id
    cache = RunCache(run_id)
    firefox.copy_places_db()

    await app.run()

    print('Cleaning up...')
    cache.delete_caches()


if __name__ == '__main__':
    asyncio.run(main())
