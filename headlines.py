import feedparser
import json
from flask import Flask
from flask import render_template
import flask
from urllib import parse, request

app = Flask(__name__)

RSS_FEEDS = {
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'оон': 'https://news.un.org/feed/subscribe/ru/news/all/rss.xml',
    'npr': 'https://rss2.feedspot.com/https://www.npr.org/sections/national/',
    'sky': 'https://feeds.skynews.com/feeds/rss/world.xml'
}

DEFAULTS = {
    'publication': 'cnn',
    'city': 'Saint-Petersburg'
}

@app.route('/')
def home():
    publication = flask.request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    city = flask.request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    return render_template('home.html', articles=articles, weather=weather)

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    query = parse.quote(query)
    api_url = f'http://api.weatherapi.com/v1/current.json?key=c60b3b20a7f14529866163025221307&q={query}&aqi=no'
    url = api_url.format(query)
    data = request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('current'):
        weather = {
            'description': parsed['current']['condition']['text'],
            'temperature': parsed['current']['temp_c'],
            'city': parsed['location']['name'],
            'country': parsed['location']['country'],
            'image': parsed['current']['condition']['icon']
        }
    return weather

if __name__ == '__main__':
    app.run(port=8001, debug=True)
