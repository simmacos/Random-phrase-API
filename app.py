from flask import Flask, jsonify
import random
import os
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configurazione del logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Configurazione del rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "10 per hour"]
)

# Array di frasi
frasi = [
    "Write everything you want",
    "Something like that",
    "GO build smth!",
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome this API returns casual phrases!",
        "how-to": "Use /casual-phrase to retrieve a casual phrase"
    })

@app.route('/casual-phrase', methods=['GET'])
@limiter.limit("1 per 5 seconds")
def get_frase_casuale():
    try:
        frase = random.choice(frasi)
        app.logger.info(f"phrase {frase}")
        return jsonify({'phrase': frase})
    except Exception as e:
        app.logger.error(f"Errore retrieving the phrase: {str(e)}")
        return jsonify({'error': 'Internal error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Limite di richieste superato. Riprova più tardi.'}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
