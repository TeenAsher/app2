import feedparser
import json
from flask import Flask
from flask import render_template
import flask
from urllib import parse, request

app = Flask(__name__)

RSS_FEEDS = {
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest'
}

@app.route('/')
def get_news():
    query = flask.request.args.get('publication')
    if not query or query.lower() not in RSS_FEEDS:
        publication = 'fox'
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    weather = get_weather()
    return render_template('home.html', articles=feed['entries'], weather=weather)

def get_weather():
    api_url = 'http://api.weatherapi.com/v1/current.json?key=c60b3b20a7f14529866163025221307&q=London&aqi=no'
    data = request.urlopen(api_url).read()
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
