import os
import random
import shutil
import string
from datetime import datetime, timedelta


class RunConfig:
    _instance = None

    def __new__(cls, date: datetime=None):
        print(type(date), 'hello')
        if cls._instance is None:
            cls._instance = super(RunConfig, cls).__new__(cls)
            cls._instance._run_id = cls._generate_run_id()
            cls._instance._date = date
        return cls._instance

    @staticmethod
    def _generate_run_id():
        time = datetime.now().strftime('%Y%m%d%H%M%S')
        # generate a random 6 character alphanumeric string
        suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        # append to the run id
        return time + '_' + suffix

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def date(self) -> datetime:
        return self._date


class RunCache:
    _instance = None

    def __new__(cls, run_id: str = None):
        if cls._instance is None:
            RunCache._instance = super(RunCache, cls).__new__(cls)

            cls._instance._cache = os.path.join('cache', run_id)
            cls._instance._documents_cache = 'cache/documents'
            cls._instance._educational_cache = os.path.join(cls._instance._cache, 'educational')
            cls._instance._summaries_cache = os.path.join(cls._instance._cache, 'summaries')
            os.makedirs(cls._instance._documents_cache, exist_ok=True)
            os.makedirs(cls._instance._educational_cache, exist_ok=True)
            os.makedirs(cls._instance._summaries_cache, exist_ok=True)

        return RunCache._instance

    @property
    def cache(self) -> str:
        return self._cache

    @property
    def documents_cache(self) -> str:
        return self._documents_cache

    @property
    def educational_cache(self) -> str:
        return self._educational_cache

    @property
    def summaries_cache(self) -> str:
        return self._summaries_cache

    def delete_caches(self):
        # Get the date for outdated cache
        outdated = datetime.now() - timedelta(days=7)
        self.delete_run_caches(outdated)

    @staticmethod
    def delete_run_caches(outdated):
        # Go through each directory in the cache base directory
        for dir_name in os.listdir('cache'):
            # Construct the full path
            dir_path = os.path.join('cache', dir_name)

            try:
                # Parse the directory name to a date
                dir_date = datetime.strptime(dir_name[:14], '%Y%m%d%H%M%S')
            except ValueError:
                continue

            # If the directory date is earlier than the outdated date, delete the cache directory
            if dir_date < outdated:
                shutil.rmtree(dir_path)

    @staticmethod
    def delete_documents_caches(outdated):
        cache_dir = 'cache/documents'
        # Go through each directory in the cache base directory
        for file_name in os.listdir(cache_dir):
            # Construct the full path
            file_path = os.path.join(cache_dir, file_name)

            if not os.path.isfile(file_path):
                continue

            if os.path.getctime(file_path) < outdated:
                os.remove(file_path)
