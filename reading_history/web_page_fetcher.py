import os
import shutil
import traceback
from datetime import datetime, timedelta
from hashlib import md5

import requests
from newsplease import NewsPlease, NewsArticle


class WebPageFetcher:
    def __init__(self):
        self.cache = CachePageFetcher();

    def get_article(self, url: str) -> NewsArticle:
        content = self.get_content_for_url(url)
        article = NewsPlease.from_html(content)

        return article

    def get_content_for_url(self, url: str) -> str:
        try:
            cached_content = self.cache.fetch_from_cache(url)
            return cached_content
        except ValueError as e:
            print(e)

            try:
                response = requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0'
                })
            # noinspection PyBroadException
            except:
                print("Failed to fetch URL:", url)
                print(traceback.format_exc())  # Save details about the exception
                response = None  # Set response as None

            if response is None or response.status_code != 200:
                self.cache.save_to_cache(url, '')
                raise ValueError(f'Failed to fetch web page {url}')

            if 'text/html' in response.headers.get('Content-Type'):
                try:
                    self.cache.save_to_cache(url, response.text)
                    return response.text
                except Exception as e:
                    raise RuntimeError(f"Failed to process URL {url} due to error: {e}")
            else:
                self.cache.save_to_cache(url, '')
                raise ValueError(f'This is not HTML content {url}')

    def get_website_data(self, url):
        data = {}
        article = self.get_article(url)
        if not article:
            raise ValueError('No article found at {}'.format(url))

        data['url'] = url
        data['title'] = article.title

        if article.maintext:
            data['content'] = article.maintext[:2000]
        else:
            raise ValueError('No article found at {}'.format(url))

        return data


class CachePageFetcher:
    def __init__(self, cache_base_dir='cache'):
        self.cache_base_dir = cache_base_dir

        # Create a new cache directory for today's date
        today = datetime.now().strftime('%Y%m%d')
        self.cache_today_dir = os.path.join(cache_base_dir, today)
        os.makedirs(self.cache_today_dir, exist_ok=True)

        self._delete_caches()

    def _get_cache_path(self, url):
        """Generate a unique file path for caching based on the URL."""
        url_hash = md5(url.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_today_dir, url_hash + '.cache')

    def fetch_from_cache(self, url) -> str:
        """Try to fetch the cached content of a URL."""
        cache_path = self._get_cache_path(url)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as file:
                return file.read()

        raise ValueError('No cache file found for URL {}'.format(url))

    def save_to_cache(self, url, content):
        """Save the content of a URL to the cache."""
        cache_path = self._get_cache_path(url)
        with open(cache_path, 'w') as file:
            file.write(content)

    def _delete_caches(self):
        cache_lifetime_in_days = 7

        # Get the date for outdated cache
        outdated = datetime.now() - timedelta(days=cache_lifetime_in_days)

        # Go through each directory in the cache base directory
        for dir_name in os.listdir(self.cache_base_dir):
            # Construct the full path
            dir_path = os.path.join(self.cache_base_dir, dir_name)

            # Ignore files and non-dated directories
            if not os.path.isdir(dir_path) or not dir_name.isdigit():
                continue

            # Parse the directory name to a date
            dir_date = datetime.strptime(dir_name, '%Y%m%d')

            # If the directory date is earlier than the outdated date, delete the cache directory
            if dir_date < outdated:
                shutil.rmtree(dir_path)
