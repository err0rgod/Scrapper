import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import os

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'news_sources': {
                'cybersecurity': [
                    'https://www.securityweek.com/',
                    'https://cybersecuritynews.com/',
                    'https://thehackernews.com/'
                ],
                'electronics': [
                    'https://www.electronicdesign.com/news',
                    'https://www.eetimes.com/news/'
                ]
            }
        }

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.config = load_config()
        self.news_sources = self.config['news_sources']

    def scrape_news(self):
        all_news = []
        
        for category, sources in self.news_sources.items():
            for source in sources:
                try:
                    response = requests.get(source, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        articles = soup.find_all(['h1', 'h2', 'h3'], class_=['title', 'headline', 'entry-title'])
                        
                        for article in articles[:5]:
                            title = article.text.strip()
                            link = article.find('a')['href'] if article.find('a') else ''
                            if not link.startswith('http'):
                                link = source + link
                            
                            news_item = {
                                'category': category,
                                'title': title,
                                'link': link,
                                'source': source,
                                'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            all_news.append(news_item)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error scraping {source}: {str(e)}")
        
        return all_news

    def save_news(self, news_items):
        if not news_items:
            raise Exception("No news items to save")
            
        filename = f"news_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, indent=4, ensure_ascii=False)
        return filename

def main():
    try:
        scraper = NewsScraper()
        news = scraper.scrape_news()
        if news:
            filename = scraper.save_news(news)
            print(f"Scraped {len(news)} news items successfully and saved to {filename}!")
            return True
        else:
            print("No news items were scraped.")
            return False
    except Exception as e:
        print(f"Error in main scraper function: {str(e)}")
        return False

if __name__ == "__main__":
    main()