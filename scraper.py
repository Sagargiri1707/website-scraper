#!/usr/bin/env python3
"""
Website Content Scraper
Crawls a website and saves each page's content to separate text files.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import os
import time
import re
from pathlib import Path
import logging
from urllib.robotparser import RobotFileParser
from typing import Set, List
import argparse

class WebsiteScraper:
    def __init__(self, base_url: str, output_dir: str = "scraped_content", 
                 delay: float = 1.0, max_pages: int = 100):
        """
        Initialize the website scraper.
        
        Args:
            base_url: The base URL to start scraping from
            output_dir: Directory to save text files
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to scrape
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.max_pages = max_pages
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Track visited URLs
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        
        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Check robots.txt
        self.robots_parser = self._check_robots_txt()
    
    def _check_robots_txt(self) -> RobotFileParser:
        """Check and parse robots.txt file."""
        robots_url = urljoin(self.base_url, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
            self.logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            self.logger.warning(f"Could not load robots.txt: {e}")
        return rp
    
    def _can_fetch(self, url: str) -> bool:
        """Check if we can fetch the URL according to robots.txt."""
        try:
            return self.robots_parser.can_fetch('*', url)
        except:
            return True  # If we can't check, assume we can fetch
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and sorting query parameters."""
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, parsed.query, ''
        ))
        return normalized
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for scraping."""
        parsed = urlparse(url)
        
        # Must be same domain
        if parsed.netloc != self.domain:
            return False
        
        # Skip common non-content files
        skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', 
                          '.zip', '.rar', '.exe', '.doc', '.docx', '.xls', '.xlsx'}
        
        if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip common non-content paths
        skip_paths = {'/wp-admin', '/admin', '/login', '/logout', '/search', 
                     '/wp-content', '/wp-includes'}
        
        if any(parsed.path.startswith(path) for path in skip_paths):
            return False
        
        return True
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all links from the page."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            full_url = urljoin(current_url, href)
            normalized_url = self._normalize_url(full_url)
            
            if (self._is_valid_url(normalized_url) and 
                normalized_url not in self.visited_urls and 
                normalized_url not in self.to_visit):
                links.append(normalized_url)
        
        return links
    
    def _clean_text(self, soup: BeautifulSoup) -> str:
        """Extract and clean text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _get_page_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled Page"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for saving."""
        # Replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        filename = filename[:100]
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        if not filename:
            filename = "page"
        
        return filename
    
    def _save_content(self, url: str, title: str, content: str) -> None:
        """Save page content to a text file."""
        # Create filename from URL path and title
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part]
        
        if path_parts:
            filename = f"{'-'.join(path_parts)}_{self._sanitize_filename(title)}"
        else:
            filename = f"home_{self._sanitize_filename(title)}"
        
        filename = f"{filename}.txt"
        filepath = self.output_dir / filename
        
        # Handle duplicate filenames
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            stem = original_filepath.stem
            suffix = original_filepath.suffix
            filepath = self.output_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Save content
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Title: {title}\n")
                f.write("=" * 80 + "\n\n")
                f.write(content)
            
            self.logger.info(f"Saved: {filepath}")
        except Exception as e:
            self.logger.error(f"Error saving {filepath}: {e}")
    
    def scrape_page(self, url: str) -> bool:
        """Scrape a single page."""
        try:
            # Check robots.txt
            if not self._can_fetch(url):
                self.logger.warning(f"Robots.txt disallows: {url}")
                return False
            
            # Make request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Skipping non-HTML content: {url}")
                return False
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            title = self._get_page_title(soup)
            content = self._clean_text(soup)
            
            # Save content
            self._save_content(url, title, content)
            
            # Extract new links
            new_links = self._extract_links(soup, url)
            self.to_visit.extend(new_links)
            
            self.logger.info(f"Scraped: {url} (found {len(new_links)} new links)")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Request error for {url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {e}")
            return False
    
    def scrape_website(self) -> None:
        """Scrape the entire website."""
        self.logger.info(f"Starting to scrape: {self.base_url}")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Max pages: {self.max_pages}")
        
        scraped_count = 0
        
        while self.to_visit and scraped_count < self.max_pages:
            url = self.to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            if self.scrape_page(url):
                scraped_count += 1
            
            # Be respectful - add delay between requests
            if self.delay > 0:
                time.sleep(self.delay)
        
        self.logger.info(f"Scraping completed. Scraped {scraped_count} pages.")
        self.logger.info(f"Files saved in: {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Scrape website content to text files')
    parser.add_argument('url', help='Base URL to scrape')
    parser.add_argument('-o', '--output', default='scraped_content',
                       help='Output directory (default: scraped_content)')
    parser.add_argument('-d', '--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('-m', '--max-pages', type=int, default=100,
                       help='Maximum number of pages to scrape (default: 100)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    # Create scraper and run
    scraper = WebsiteScraper(
        base_url=args.url,
        output_dir=args.output,
        delay=args.delay,
        max_pages=args.max_pages
    )
    
    try:
        scraper.scrape_website()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()