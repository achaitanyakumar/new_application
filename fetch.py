from datetime import datetime, timedelta
import requests

# API Keys for News APIs
NEWS_API_KEY = "8c8d614b4e90480e98e06f429bc2d0e2"
GNEWS_API_KEY = "f6ad2a1680d3b1162ac0ade8e878992c"
MEDIASTACK_API_KEY = "b017130c62747fa2c77ab25998779058"
NEWSDATA_API_KEY = "pub_57310ebbe1a2085698784530e71ae2d879ea7"

# Global variables for caching news articles and last fetch time
cached_news = []
last_fetch_time = datetime.min

# Function to filter articles, checking for essential fields
def filter_articles(articles):
    return [
        article for article in articles
        if article.get('urlToImage') and article.get('title') and '[Removed]' not in article['title']
    ]

# Function to fetch news from APIs and cache results
def fetch_news():
    global cached_news, last_fetch_time
    if datetime.now() - last_fetch_time > timedelta(hours=1):  # Refresh every hour
        try:
            print("Fetching news...")
            # Fetch news from NewsAPI
            newsapi_url = f'https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}'
            newsapi_response = requests.get(newsapi_url)
            newsapi_data = newsapi_response.json()
            print(f"NewsAPI Response: {newsapi_data}")

            if newsapi_response.status_code != 200 or 'articles' not in newsapi_data:
                print(f"NewsAPI Error: {newsapi_data.get('message', 'No articles returned')}")
                newsapi_articles = []
            else:
                newsapi_articles = filter_articles(newsapi_data['articles'])
            
            # Fetch news from GNewsAPI
            gnewsapi_url = f'https://gnews.io/api/v4/top-headlines?token={GNEWS_API_KEY}&lang=en'
            gnewsapi_response = requests.get(gnewsapi_url)
            gnewsapi_data = gnewsapi_response.json()
            print(f"GNewsAPI Response: {gnewsapi_data}")

            if gnewsapi_response.status_code != 200 or 'articles' not in gnewsapi_data:
                print(f"GNewsAPI Error: {gnewsapi_data.get('message', 'No articles returned')}")
                gnewsapi_articles = []
            else:
                gnewsapi_articles = filter_articles(gnewsapi_data['articles'])
            
            # Fetch news from MediaStack API
            mediastack_url = f'http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&languages=en'
            mediastack_response = requests.get(mediastack_url)
            mediastack_data = mediastack_response.json()
            print(f"MediaStack Response: {mediastack_data}")

            if mediastack_response.status_code != 200 or 'data' not in mediastack_data:
                print(f"MediaStack API Error: {mediastack_data.get('error', 'No articles returned')}")
                mediastack_articles = []
            else:
                mediastack_articles = filter_articles(mediastack_data['data'])
                
            # Fetch news from NewsData API
            newsdata_url = f'https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&language=en'
            newsdata_response = requests.get(newsdata_url)
            newsdata_data = newsdata_response.json()
            print(f"NewsData Response: {newsdata_data}")

            if newsdata_response.status_code != 200 or 'results' not in newsdata_data:
                print(f"NewsData API Error: {newsdata_data.get('message', 'No articles returned')}")
                newsdata_articles = []
            else:
                newsdata_articles = filter_articles(newsdata_data['results'])
            
            # Combine articles from all APIs
            cached_news = newsapi_articles + gnewsapi_articles + mediastack_articles + newsdata_articles
            cached_news = cached_news[:50]  
            
            if not cached_news:
                print("No news articles available from any source.")

        except Exception as e:
            print(f"Exception fetching news: {e}")
            cached_news = []  # Reset cached news in case of an error

        last_fetch_time = datetime.now()
