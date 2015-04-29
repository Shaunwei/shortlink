import redis
import json
from operator import itemgetter

from utils import Dencoder
from flask import Flask
from flask import request
app = Flask(__name__)
app.redis = redis.Redis()


def set_visit(shorturl):
    visited = json.loads(app.redis.get('visited'))
    if len(visited) == 100:
        visited.pop(0)
    visited.append(shorturl)

    counts = json.loads(app.redis.get('counts'))
    if shorturl in counts:
        counts[shorturl] += 1
    else:
        counts[shorturl] = 1
    app.redis.set('counts', json.dumps(counts))
    app.redis.set('visited', json.dumps(visited))


@app.route('/get/<key>')
def get_value(key):
    return 'Key %s' % app.redis.get(key)


@app.route('/short', methods=['POST'])
def get_shorturl():
    if request.method == 'POST':
        url = request.args.get('url', '')
        if app.redis.get(url):
            print 'cache'
            shorturl = app.redis.get(url)
            set_visit(shorturl)
            return shorturl

        decoder = Dencoder()
        # import debug
        shorturl = str(decoder.decode(url))
        app.redis.set(url, shorturl)
        set_visit(shorturl)
        return shorturl


@app.route('/visited')
def get_visited():
    return app.redis.get('visited')


@app.route('/most_visited')
def get_most_visited():
    counts = json.loads(app.redis.get('counts'))
    most_visited = list(sorted(counts.items(), key=itemgetter(1)))[:10]
    return str(most_visited)

if __name__ == "__main__":
    app.run()
