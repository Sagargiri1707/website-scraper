# Website Content Scraper

A comprehensive Python tool that crawls websites and extracts clean text content from each page, saving it to individual text files. Perfect for content analysis, research, documentation, or creating local backups of website content.

## Features

- 🕷️ **Comprehensive Crawling**: Automatically discovers and follows internal links
- 📄 **Clean Text Extraction**: Removes HTML tags and extracts readable content
- 🗂️ **Organized Output**: Saves each page to a separate, well-named text file
- 🤖 **Respectful Scraping**: Follows robots.txt rules and includes rate limiting
- 🛡️ **Smart Filtering**: Skips non-content files (PDFs, images, admin pages)
- 📊 **Progress Logging**: Detailed logging of scraping progress and errors
- ⚙️ **Configurable**: Customizable delays, output directory, and page limits

## Installation

1. **Clone or download** the script
2. **Install required dependencies**:
```bash
pip install requests beautifulsoup4
```

## Quick Start

```bash
# Basic usage - scrape a website with default settings
python scraper.py https://example.com

# Scrape with custom settings
python scraper.py https://example.com -o my_content -d 2.0 -m 50
```

## Usage

### Command Line Options

```bash
python scraper.py <URL> [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `URL` | Base URL to scrape (required) | - |
| `-o, --output` | Output directory for text files | `scraped_content` |
| `-d, --delay` | Delay between requests (seconds) | `1.0` |
| `-m, --max-pages` | Maximum number of pages to scrape | `100` |

### Examples

```bash
# Basic scraping
python scraper.py https://docs.python.org

# Custom output directory
python scraper.py https://example.com --output ./website_backup

# Slower scraping (2 second delay) with more pages
python scraper.py https://blog.example.com -d 2.0 -m 200

# Quick scraping for small sites
python scraper.py https://smallsite.com -d 0.5 -m 20
```

## Output Format

Each scraped page creates a text file with the following structure:

```
URL: https://example.com/page
Title: Page Title Here
================================================================================

Clean text content of the page goes here...
All HTML tags are removed and text is properly formatted.
```

### File Naming Convention

Files are automatically named based on:
- URL path structure
- Page title
- Automatic deduplication for similar names

Examples:
- `home_Welcome_to_Example.txt` (homepage)
- `about-us_About_Our_Company.txt` (about page)
- `blog-post-title_Blog_Post_Title.txt` (blog post)

## Configuration

### Customizing Behavior

You can modify the `WebsiteScraper` class to customize behavior:

```python
scraper = WebsiteScraper(
    base_url="https://example.com",
    output_dir="custom_output",
    delay=1.5,  # 1.5 second delay
    max_pages=250  # Scrape up to 250 pages
)
scraper.scrape_website()
```

### Filtering Content

The scraper automatically skips:
- **File types**: PDFs, images, documents, archives
- **Paths**: Admin panels, login pages, WordPress admin
- **External links**: Only scrapes the same domain

## Technical Details

### How It Works

1. **Initialization**: Sets up session, checks robots.txt, creates output directory
2. **URL Discovery**: Starts with base URL, extracts links from each page
3. **Content Extraction**: Downloads HTML, parses with BeautifulSoup, extracts clean text
4. **File Saving**: Saves content to organized text files
5. **Respectful Crawling**: Follows robots.txt, implements delays, avoids duplicates

### Dependencies

- **requests**: HTTP library for downloading pages
- **beautifulsoup4**: HTML parsing and content extraction
- **urllib**: URL parsing and robots.txt handling
- **pathlib**: Modern file path handling

### Robots.txt Compliance

The scraper automatically:
- Downloads and parses robots.txt
- Respects crawl delays and disallowed paths
- Falls back gracefully if robots.txt is unavailable

## Troubleshooting

### Common Issues

**Permission Denied Errors**
```bash
# Make sure you have write permissions in the output directory
mkdir scraped_content
chmod 755 scraped_content
```

**Timeout Errors**
```bash
# Increase delay for slow websites
python scraper.py https://slow-site.com -d 3.0
```

**Too Many Pages**
```bash
# Limit scraping for large sites
python scraper.py https://large-site.com -m 50
```

### Debugging

Enable detailed logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### Ethical Scraping

- ✅ **Check robots.txt**: Always respect website crawling rules
- ✅ **Use delays**: Don't overwhelm servers with rapid requests
- ✅ **Limit scope**: Set reasonable page limits for large sites
- ✅ **Check terms of service**: Ensure scraping is allowed
- ✅ **Be respectful**: Use for research/personal use, not commercial exploitation

### Performance Tips

- **Adjust delays**: Balance between speed and server load
- **Filter URLs**: Customize URL filtering for specific sites
- **Monitor output**: Check logs for errors or issues
- **Test first**: Try small limits before full scraping

## Use Cases

- 📚 **Documentation Backup**: Create local copies of documentation sites
- 🔍 **Content Analysis**: Extract text for analysis or processing
- 📖 **Research**: Gather content from multiple pages for study
- 💾 **Archival**: Preserve website content for future reference
- 📊 **Data Collection**: Gather structured text data from websites

## Contributing

Feel free to contribute improvements:

1. **Bug fixes**: Report and fix issues
2. **Features**: Add new functionality
3. **Documentation**: Improve this README
4. **Testing**: Add test cases for different websites

## License

This tool is provided as-is for educational and research purposes. Please use responsibly and in accordance with website terms of service and applicable laws.

## Changelog

### Version 1.0
- Initial release
- Basic crawling and content extraction
- Robots.txt compliance
- Configurable delays and limits
- Clean text output

---

**Disclaimer**: This tool is for educational and research purposes. Always respect website terms of service, robots.txt files, and applicable laws when scraping content. The authors are not responsible for any misuse of this tool.