from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv
from search import search_news
from summarization import summarize
from question_answering import ask_question
from fake_news_detection import detect_fake_news 

app = Flask(__name__)
app.secret_key = "Nagendra048"

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

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
            newsapi_url = f'https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}&pageSize=50'
            newsapi_response = requests.get(newsapi_url)
            newsapi_data = newsapi_response.json()
            print(f"NewsAPI Response: {newsapi_data}")

            if newsapi_response.status_code != 200 or 'articles' not in newsapi_data:
                print(f"NewsAPI Error: {newsapi_data.get('message', 'No articles returned')}")
                newsapi_articles = []
            else:
                newsapi_articles = filter_articles(newsapi_data['articles'])
            
            # Fetch news from GNewsAPI
            gnewsapi_url = f'https://gnews.io/api/v4/top-headlines?token={GNEWS_API_KEY}&lang=en&max=50'
            gnewsapi_response = requests.get(gnewsapi_url)
            gnewsapi_data = gnewsapi_response.json()
            print(f"GNewsAPI Response: {gnewsapi_data}")

            if gnewsapi_response.status_code != 200 or 'articles' not in gnewsapi_data:
                print(f"GNewsAPI Error: {gnewsapi_data.get('message', 'No articles returned')}")
                gnewsapi_articles = []
            else:
                gnewsapi_articles = filter_articles(gnewsapi_data['articles'])
            
            # Fetch news from MediaStack API
            mediastack_url = f'http://api.mediastack.com/v1/news?access_key={MEDIASTACK_API_KEY}&languages=en&limit=50'
            mediastack_response = requests.get(mediastack_url)
            mediastack_data = mediastack_response.json()
            print(f"MediaStack Response: {mediastack_data}")

            if mediastack_response.status_code != 200 or 'data' not in mediastack_data:
                print(f"MediaStack API Error: {mediastack_data.get('error', 'No articles returned')}")
                mediastack_articles = []
            else:
                mediastack_articles = filter_articles(mediastack_data['data'])
                
            # Fetch news from NewsData API
            newsdata_url = f'https://newsdata.io/api/1/sources?country=in&apikey={NEWSDATA_API_KEY}'
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
            cached_news = cached_news[:200]  
            # Print total number of articles fetched
            print(f"Total articles fetched and combined: {len(cached_news)}")

            
            if not cached_news:
                print("No news articles available from any source.")

        except Exception as e:
            print(f"Exception fetching news: {e}")
            cached_news = []  # Reset cached news in case of an error

        last_fetch_time = datetime.now()


@app.route('/')
def home():
    fetch_news()
    return render_template('home.html', news_data=cached_news,active_page="home")


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        search_results = search_news(query)
        return render_template('home.html', news_data=search_results,is_search=True,query=query)

    flash("Please enter a search query.")
    return redirect(url_for('home'))

@app.route('/category/<category>')
def category(category):
    search_results = search_news(category)
    return render_template('home.html', news_data=search_results, category=category)

@app.route('/summarization')
def summarization():
    return render_template('summarization.html',active_page="summarization")

@app.route('/summarize', methods=['POST'])
def summarize_article():
    input_text = request.form.get('text', '')
    uploaded_file = request.files.get('file')
    summary_type = request.form.get('summary_type', 'abstractive')

    if uploaded_file and uploaded_file.filename:
        files = {'file': uploaded_file}
    else:
        files = None

    summary = summarize(input_text, summary_type, files)
    return render_template('summarization.html', summary=summary)

@app.route('/qa')
def qa():
    return render_template('qa.html',active_page="qa")

@app.route('/ask_question', methods=['POST'])
def ask():
    # Get question and text input from user
    question = request.form.get('question', '')
    input_text = request.form.get('text', '')
    uploaded_file = request.files.get('file')

    # Process file input if provided
    if uploaded_file and uploaded_file.filename:
        answer = ask_question("", question, {'file': uploaded_file})
    elif input_text:
        # Process user-input text if provided
        answer = ask_question(input_text, question, {})
    else:
        answer = "Please provide text or upload a file to ask a question."
    
    return render_template('qa.html', answer=answer)

@app.route('/fake_news_detection')
def fake_news_detection():
    return render_template('fake_news_detection.html',active_page="fake_news_detection")

@app.route('/detect_fake_news', methods=['POST'])
def detect():
    title = request.form.get('title', '')
    text = request.form.get('text', '')
    file = request.files.get('file')
    
    if file and file.filename:
        detection_result = detect_fake_news(input_title="", input_text="", file=file)
        title, text = "", ""  
    else:
        detection_result = detect_fake_news(input_title=title, input_text=text)

    return render_template('fake_news_detection.html', detection_result=detection_result, title=title, text=text)


if __name__ == '__main__':
    app.run(debug=True)

