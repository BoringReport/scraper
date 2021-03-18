# Scraper

## Required libraries
`pip install newspaper3k`

## Getting Started
These steps will create a folder data/ with article content, and fill meta.json with metadata about the articles including title, authors, and download status.

1. Create file meta.json at root of project
2. Populate meta.json with
    ```
    {"articles": []}
    ```
3. Run scrape.py
   ```
   python3 scrape.py
   ```