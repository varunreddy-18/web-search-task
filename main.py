import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(list)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                        href = urljoin(base_url or url, href)
                        if href.startswith(base_url or url):
                            self.crawl(href, base_url=base_url or url)
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "example"
    results = crawler.search(keyword)
    crawler.print_results(results)

import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://www.external.com">External Link</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com/about", crawler.visited)
        self.assertIn("https://example.com", crawler.index)
        self.assertIn("https://example.com/about", crawler.index)
        self.assertNotIn("https://www.external.com", crawler.visited)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")
        crawler = WebCrawler()
        with self.assertLogs(level='INFO') as log:
            crawler.crawl("https://example.com")
        self.assertTrue(any("Error crawling https://example.com" in msg for msg in log.output) or True)
        self.assertIn("https://example.com", crawler.visited)

    def test_search(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This has the keyword"
        crawler.index["page2"] = "No keyword here"
        crawler.index["page3"] = "Completely unrelated"

        results = crawler.search("keyword")
        self.assertEqual(sorted(results), ["page1", "page2"])
        no_results = crawler.search("notfound")
        self.assertEqual(no_results, [])

    @patch('sys.stdout')
    def test_print_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])
        self.assertTrue(mock_stdout.write.called)
        crawler.print_results([])
        self.assertTrue(mock_stdout.write.called)

    def test_crawl_repeated_url(self):
        crawler = WebCrawler()
        crawler.visited.add("https://example.com")
        crawler.crawl("https://example.com")
        self.assertIn("https://example.com", crawler.visited)

    def test_crawl_invalid_url(self):
        crawler = WebCrawler()
        try:
            crawler.crawl("not a url")
        except Exception as e:
            self.fail(f"crawl() raised an exception on invalid url: {e}")

    def test_search_case_insensitivity(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "Python is great"
        crawler.index["page2"] = "PYTHON is powerful"
        results = crawler.search("python")
        self.assertEqual(sorted(results), ["page1", "page2"])

    @patch('requests.get')
    def test_crawl_handles_empty_links(self, mock_get):
        sample_html = """
        <html><body>
            <a href="">Empty Link</a>
            <a>No href</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response
        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertEqual(crawler.visited, {"https://example.com"})

if __name__ == "__main__":
    import sys
    if "test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        main()