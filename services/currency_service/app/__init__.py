from flask import Flask, jsonify, request
import json 
from pathlib import Path

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    currency_database = {
        "USD": 1,
        "MXN": 17.00,
        "EUR": 0.94,
        "JPY": 154.81
    }

    # returns the equivalent of one dollar in the desired currency
    @app.route('/api/get_conversion', methods=['GET'])
    def get_conversion():
        currency = request.args.get('currency')
        return jsonify({'conversion' : currency_database[currency]})
    return app

