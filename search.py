from flask import request, flash
import requests
import os
from datetime import datetime, timedelta
from fetch import filter_articles

# API Keys for News APIs
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  

# Function to search for news articles
def search_news(query):
    search_results = []
    keywords = query.lower().split()

    try:
        # Fetch recent and older articles from NewsAPI
        newsapi_url = f'https://newsapi.org/v2/everything?q={query}&from={(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}&to={(datetime.now()).strftime("%Y-%m-%d")}&language=en&apiKey={NEWS_API_KEY}'
        response = requests.get(newsapi_url)
        data = response.json()
        if response.status_code == 200 and 'articles' in data:
            search_results.extend(data['articles'])
        else:
            print(f"NewsAPI Search Error: {data.get('message', 'No articles returned')}")

        # Fetch news from GNews API
        gnews_url = f'https://gnews.io/api/v4/search?q={query}&token={GNEWS_API_KEY}&lang=en&sortBy=relevance'
        response = requests.get(gnews_url)
        data = response.json()
        if response.status_code == 200 and 'articles' in data:
            search_results.extend(data['articles'])
        else:
            print(f"GNewsAPI Search Error: {data.get('message', 'No articles returned')}")

        # Fetch from MediaStack API (older articles)
        mediastack_url = f'http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&keywords={query}&languages=en'
        response = requests.get(mediastack_url)
        data = response.json()
        if response.status_code == 200 and 'data' in data:
            search_results.extend(data['data'])
        else:
            print(f"MediaStack Search Error: {data.get('error', 'No articles returned')}")

        # Fetch news from NewsData API
        newsdata_url = f'https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q={query}&language=en&'
        response = requests.get(newsdata_url)
        data = response.json()
        if response.status_code == 200 and 'results' in data:
            search_results.extend(data['results'])
        else:
            print(f"NewsData Search Error: {data.get('message', 'No articles returned')}")

        # Fetch news from Tavily API
        tavily_url = f'https://api.tavily.com/v1/search?query={query}&apiKey={TAVILY_API_KEY}&language=en'
        response = requests.get(tavily_url)
        data = response.json()
        if response.status_code == 200 and 'articles' in data:
            search_results.extend(data['articles'])
        else:
            print(f"Tavily Search Error: {data.get('message', 'No articles returned')}")

        # Filter out duplicates and articles without images or titles
        search_results = filter_articles(search_results)
        return search_results

    except Exception as e:
        print(f"Exception during news search: {e}")
        return []
