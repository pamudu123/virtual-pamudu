# Experiment Notes

## Scraping Attempts

### Libraries Tested
- `newspaper`
- `newspaper3k`
- `requests`
- `cloudscraper`

### Results
**Failures:**
- Most libraries failed to retrieve the article, returning `Status code: 403`.

**Successes:**
- `curl-cffi`: Was able to scrape Medium articles.

### Issues with `newspaper3k`
The target URL is not recognized as an "Article". The `newspaper3k` library is designed to find long-form stories (like news or blogs). The specific URL tested is a Portfolio/Landing Page containing very little text (mostly navigation buttons like "About", "Journal", and a generic "Hey there" greeting). Consequently, `newspaper3k` analyzes the page, finds no paragraphs of text, decides "there is no article here," and returns only the title.


## 22nd Nov 2025
## MCP Client
- The MCP client should not be able to connect if it is already acting as a server.
- Need to experiment further on this.
- **Action Item:** Connect YouTube videos as a tool for now.