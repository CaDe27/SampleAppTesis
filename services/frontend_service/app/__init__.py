from flask import Flask, render_template, request, jsonify, session
from flask_caching import Cache
import requests
import json
import os
import uuid
import random
import redis
import time
from datetime import datetime
from pathlib import Path
import importlib.util
import sys
from frontend_service.redis_client import make_api_get_request, make_api_post_request, make_fake_request

config = None
def load_config():
    current_script_path = Path(__file__).resolve()
    grandparent_directory = current_script_path.parent.parent.parent
    config_path = grandparent_directory / 'config.json'
    with open(config_path, 'r') as config_file:
        global config
        config = json.load(config_file)

def get_service_url(service_name):
    host = config['host']
    service_port = config['ports'][service_name]
    return f"http://{host}:{service_port}"

def generate_unique_user_id():
    return str(uuid.uuid4())

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = os.urandom(16).hex()

    # set up Cache
    app.config['CACHE_TYPE'] = 'SimpleCache'
    global cache
    cache = Cache(app)
    @cache.memoize(timeout=10)
    def request_new_ad():
        try:
            ad_service_url = f'{get_service_url("ad")}/api/ad'
            response = make_api_get_request(ad_service_url, json=None, params=None, receiver_service_id=1)
            ad_content = response.json()
        except requests.RequestException as e:
            print(e)
            ad_content = {}
        return ad_content
    # end cache setup

    load_config()

    # set up routes
    @app.route('/')
    def home():
        if 'user_id' not in session:
            session['user_id'] = generate_unique_user_id()
        movie_service_url = f"{get_service_url('product_catalog')}/api/top10"
        try:
            response = make_api_get_request(movie_service_url, json=None, params=None, receiver_service_id=7)
            movies = response.json()
        except requests.RequestException as e:
            print(e)
            movies = []  # If there's an error, default to an empty list
        return render_template('index.html', movies=movies)

    @app.route('/api/get_ad', methods=['GET'])
    def get_ad():
        return jsonify(request_new_ad())
    
    @app.route('/update_cart', methods=['POST'])
    def update_cart():
        cart_service_url = f"{get_service_url('cart')}/api/update_cart"
        data = request.json
        movie_id = int(data['movie_id'])
        change = int(data['change'])
        movie_price = float(data['price'])
        movie_title = data['title']

        try:
            params = {'user_id': session['user_id'], 
                      'movie_id': movie_id,
                      'price': movie_price, 
                      'title': movie_title,
                      'change': change}
            response = make_api_post_request(cart_service_url, params=params, receiver_service_id=2)
            data = response.json()  
            cart = data.get('cart', {})  # Provide default empty dict if key doesn't exist
            total = data.get('total', 0)  # Provide default 0 if key doesn't exist
        except requests.RequestException as e:
            print(e)
            cart = {}
            total = 0

        return jsonify({'cart':cart, 'total': total})
    
    @app.route('/get_cart')
    def get_cart():
        cart_service_url = f"{get_service_url('cart')}/api/get_cart"
        params = {'user_id': session['user_id']}
        try:
            response = make_api_get_request(cart_service_url, json=params, params=None,receiver_service_id=2)
            data = response.json()  # Get the whole response as a JSON object
            # Access the cart and total using keys
            cart = data.get('cart', {})  # Provide default empty dict if key doesn't exist
            total = data.get('total', 0)  # Provide default 0 if key doesn't exist
        except requests.RequestException as e:
            print(e)
            cart, total = {}, 0
        # Correctly format the return object
        return jsonify({'cart': cart, 'total': total})
    
    @app.route('/search_movies', methods=['GET'])
    def search_movies_proxy():
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Assuming get_service_url is a function you have defined to get the URL of the microservice
        service_url = get_service_url("product_catalog")  
        search_url = f"{service_url}/api/search?query={query}"
        
        try:
            response = make_api_get_request(search_url, json=None, params=None,receiver_service_id=7)
            # Forward the JSON response from the /api/search service to the client
            return jsonify(response.json())
        except requests.RequestException as e:
            # Handle any errors that occur during the request to the search service
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/get_conversion', methods=['GET'])
    def get_conversion():
        currency = request.args.get('currency')
        if not currency:
            return jsonify({'error': 'Currency parameter is required'}), 400
        
        currency_service_url = f"{get_service_url('currency')}/api/get_conversion"
        params = {'currency': currency}
        try:
            response = make_api_get_request(currency_service_url, json=None, params=params,receiver_service_id=3)
            response_json = response.json() 
            if 'error' in response_json:
                return jsonify({'error': f"Unsupported currency: {currency}"}), 404
            conversion = response_json.get('conversion') if 'conversion' in response_json else None
            if conversion is None:
                return jsonify({'error': 'Currency not found'}), 404
        except requests.RequestException as e:
            print(e)
            return jsonify({'error': 'Failed to fetch conversion rate'}), 500
        return jsonify({'conversion': conversion})

    @app.route('/api/process_payment', methods=['POST'])
    def process_payment():
        data = request.json
        card_number = data['cardNumber']
        cvv =  data['cvv']
        params = { "card_number":card_number, "cvv":cvv}
        try:
            if random.random() <= 0.5:
                response_json = {'message':"Success"}
                make_fake_request(receiver_service_id=6, fake_status_code=200)
            else:
                response_json = {'message':"Failure"}
                make_fake_request(receiver_service_id=6, fake_status_code=500)
            
            if 'error' in response_json:
                return jsonify({'error': f"Card Payment error: {card_number}, {cvv}"}), 404
            message = response_json.get('message') if 'message' in response_json else None
            if message is None:
                return jsonify({'error': f"Card Payment error: {card_number}, {cvv}"}), 404
        except requests.RequestException as e:
            print(e)
            return jsonify({'error': f"Card Payment error: {card_number}, {cvv}"}), 500
        return jsonify({'message': message})
    
    @app.route('/api/send_email', methods=['POST'])
    def send_email():
        data = request.json
        email = data['email']
        params = {"email":email}
        try:
            if random.random() <= 0.8:
                response_json = {'message':"email sent"}
                make_fake_request(receiver_service_id=4, fake_status_code=200)
            else:
                response_json = {'message':"Failure"}
                make_fake_request(receiver_service_id=4, fake_status_code=500)
            
            if 'error' in response_json:
                return jsonify({'error': f"Emailing failed: {email}"}), 404
            message = response_json.get('message') if 'message' in response_json else None
            if message is None:
                return jsonify({'error': f"Emailing failed: {email}"}), 404
        except requests.RequestException as e:
            print(e)
            return jsonify({'error': f"Mailing error: {email}"}), 500
        return jsonify({'message': message})
    return app