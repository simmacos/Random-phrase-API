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
    default_limits=["200 per day", "50 per hour"]
)

# Array di frasi
frasi = [
    "La vita è ciò che ti accade mentre sei occupato a fare altri progetti.",
    "Il modo migliore per predire il futuro è crearlo.",
    "La felicità non è qualcosa di già pronto. Nasce dalle tue azioni.",
    "Il successo è la somma di piccoli sforzi ripetuti giorno dopo giorno.",
    "La creatività è l'intelligenza che si diverte.",
    "Non aspettare. Il tempo non sarà mai giusto.",
    "La semplicità è la massima sofisticazione.",
    "Fai quello che puoi, con quello che hai, nel posto in cui sei.",
    "Il viaggio di mille miglia inizia con un singolo passo.",
    "La conoscenza parla, ma la saggezza ascolta."
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Benvenuto all'API delle frasi casuali!",
        "istruzioni": "Usa /frase-casuale per ottenere una frase casuale."
    })

@app.route('/frase-casuale', methods=['GET'])
@limiter.limit("1 per 5 seconds")
def get_frase_casuale():
    try:
        frase = random.choice(frasi)
        app.logger.info(f"Frase restituita: {frase}")
        return jsonify({'frase': frase})
    except Exception as e:
        app.logger.error(f"Errore nel recupero della frase: {str(e)}")
        return jsonify({'errore': 'Si è verificato un errore interno'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'errore': 'Limite di richieste superato. Riprova più tardi.'}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
