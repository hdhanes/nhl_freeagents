'''
Scraping the data - run this file to populate the scraped data
'''

from nhl_scraping.scraper import NHLSeasonScraper

#run this file to populate/scrape the data
if __name__ == "__main__":
    scraped = NHLSeasonScraper()
    scraped.scraperosters("2021")
    scraped.scrapeFA("2021")
    scraped.save_df()