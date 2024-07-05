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
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "10 per hour"]
)

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

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Request limit reached, try again later!'}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
