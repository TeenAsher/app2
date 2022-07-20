import datetime
import feedparser
import flask
import json
from flask import Flask
from flask import make_response
from flask import render_template
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
    'city': 'Saint-Petersburg',
    'currency_from': 'USD',
    'currency_to': 'RUB'
}

CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=0b0c3a8e4e4243d48c89316d6cba8c84'

def get_value_with_fallback(key):
    if flask.request.args.get(key):
        return flask.request.args.get(key)
    if flask.request.cookies.get(key):
        return flask.request.cookies.get(key)
    return DEFAULTS[key]

@app.route('/')
def home():
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)
    city = get_value_with_fallback('city')
    weather = get_weather(city)
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rates(currency_from, currency_to)
    response = make_response(
        render_template('home.html', articles=articles, weather=weather,
                        currency_from=currency_from, currency_to=currency_to,
                        rate=rate, currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie('publication', publication, expires=expires)
    response.set_cookie('city', city, expires=expires)
    response.set_cookie('currency_from', currency_from, expires=expires)
    response.set_cookie('currency_to', currency_to, expires=expires)
    return response

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

def get_rates(frm, to):
    all_currency = request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())

if __name__ == '__main__':
    app.run(port=8001, debug=True)
