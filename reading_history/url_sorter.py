from urllib.parse import urlparse


class UrlSorter:
    def __init__(self):
        self.search_engines = self._helper_read_file('./config/search_engines.txt')
        try:
            self.blocklist = self._helper_read_file('./config/blocklist.txt')
        except FileNotFoundError:
            self.blocklist = []

    def filter_urls(self, urls):
        filtered = []
        for url in urls:
            try:
                filtered.append(self.is_valid(url))
            except ValueError:
                pass

        return filtered

    def _helper_read_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = [line.rstrip('\n') for line in file.readlines()]

        return lines

    def _is_search_engine(self, url: str):
        """Check if the given URL belongs to a known search engine."""
        if any(se for se in self.search_engines if url.startswith(se)):
            raise ValueError('Search Engine URL')

    def _is_root_domain(self, url: str):
        """Check if the URL is for the root domain (homepage)."""
        parsed_url = urlparse(url)
        if parsed_url.path in ('', '/', '/index.html'):
            raise ValueError('Root domain')

    def _is_local_domain(self, url: str):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc.split(':')[0]
        # Check if the domain is localhost, a bare IP address, or a .dev domain
        if netloc == 'localhost' or netloc.replace('.', '').isdigit():
            raise ValueError('Local/development domain or IP address')

    def _is_blocklisted(self, url: str):
        if any(blocked for blocked in self.blocklist if url.startswith(blocked)):
            raise ValueError('Manually blocklisted URL')

    def is_valid(self, url: str) -> str:
        # Remove search engine entries, root domain entries, local domains,
        # IP addresses and user-defined blocked items
        try:
            self._is_blocklisted(url)
            self._is_root_domain(url)
            self._is_local_domain(url)
            self._is_search_engine(url)

            return url
        except ValueError as e:
            raise ValueError(f'{url}: {e}')

    def is_valid_callback(self, url: str) -> bool:
        try:
            self.is_valid(url)
            return True
        except ValueError:
            return False
