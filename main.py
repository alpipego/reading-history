import asyncio

from dotenv import load_dotenv

from reading_history import app, firefox

load_dotenv()


async def main():
    firefox.copy_places_db()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
