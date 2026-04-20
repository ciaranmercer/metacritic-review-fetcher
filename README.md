# metacritic-review-fetcher

A small Python project for scraping Metacritic movie reviews as listed in an input Excel sheet.

The script reads in movie title, director, and year row by row from the Excel sheet, builds the corresponding Metacritic URL and extracts the score value.

Designed to amass Metacritic scores for small, personal movie libraries in order to add detail for movies on your watchlist.

## Features

- Builds movie URLs automatically from title (or title + year in the case of identical movie names)
- Scrapes movie metadata from Metacritic
- Handles HTTP errors like 404 pages
- Handles interrupted responses with retry logic
- Uses randomized delays between requests to reduce blocking risk
- Exports results into a pandas DataFrame, then a new Excel sheet

## Installation

Clone the repository:
```
git clone https://github.com/ciaranmercer/metacritic-review-fetcher.git
cd metacritic-review-fetcher
```
Install dependencies:
```
pip install pandas requests beautifulsoup4
```

## Usage

Run the script with:
```
python metacritic_scraper.py <file_name> <sheet_number>
```
### Notes

- Please ensure the Excel sheet you are using is located in the same directory as the script
- Sheet number is indexed starting at 0
- Entires that could not be retrieved are assigned a value of -1
- Output filename is `output.xlsx`

### Disclaimer

This project has been created for educational and learning purposes. It is not designed to be ran at scale. Always respect rate limits.
