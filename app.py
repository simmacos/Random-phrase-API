from flask import Flask, jsonify
import random
import os
import logging
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Logging configuration
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Rate limiting configuration
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "10 per hour"],
    storage_uri="memory://"
)
limiter.init_app(app)

# Read phrases from environment variable
phrases_json = os.environ.get('PHRASES', '[]')
phrases = json.loads(phrases_json)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome! This API returns casual phrases!",
        "how-to": "Use /casual-phrase to retrieve a casual phrase"
    })

@app.route('/casual-phrase', methods=['GET'])
@limiter.limit("200 per day")
@limiter.limit("10 per hour")
@limiter.limit("1 per 5 seconds")
def get_casual_phrase():
    try:
        if phrases:
            phrase = random.choice(phrases)
            app.logger.info(f"Phrase returned: {phrase}")
            return jsonify({'phrase': phrase})
        else:
            app.logger.warning("No phrases available")
            return jsonify({'error': 'No phrases available'}), 404
    except Exception as e:
        app.logger.error(f"Error retrieving the phrase: {str(e)}")
        return jsonify({'error': 'Internal error'}), 500

@limiter.request_filter
def log_limiter_hit():
    app.logger.info(f"Rate limit hit for IP: {get_remote_address()}")
    return False

@app.errorhandler(429)
def ratelimit_handler(e):
    app.logger.warning(f"Rate limit exceeded for IP: {get_remote_address()}")
    return jsonify({'error': 'Request limit reached, try again later!'}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
