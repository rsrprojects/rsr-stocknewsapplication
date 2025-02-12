from flask import Flask, render_template
from .news_scraper import get_magnificent_seven_news


app = Flask(__name__)


@app.route('/')
def index():
    news_items = get_magnificent_seven_news()
    return render_template('index.html', news_items=news_items)


if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=False)
