from flask import Flask, jsonify, request
import redis
# import pandas as pd
# import os
import json 
# import random
from pathlib import Path
from cart_service.redis_client import make_api_get_request, make_api_post_request, make_fake_request

config = None
def load_config():
    current_script_path = Path(__file__).resolve()
    grandparent_directory = current_script_path.parent.parent.parent
    config_path = grandparent_directory / 'config.json'
    with open(config_path, 'r') as config_file:
        global config
        config = json.load(config_file)

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    load_config()

    host = config['host']
    redis_port = config['ports']['cart-redis']
    redis_client = redis.Redis(host=host, port=redis_port, db=0, decode_responses=True)
    make_fake_request(receiver_service_id=8, fake_status_code=200)

    def get_cart(user_id):
        cart_key = f"cart:{user_id}"
        total_key = f"total:{user_id}"
        cart_items = redis_client.hgetall(cart_key)
        make_fake_request(receiver_service_id=8, fake_status_code=200)

        total = redis_client.get(total_key)
        make_fake_request(receiver_service_id=8, fake_status_code=200)

        # Build the cart response
        cart_response = {}
        for movie_id, quantity in cart_items.items():
            price_key = f"price:{movie_id}"
            title_key = f"title:{movie_id}"
            price = redis_client.hget(price_key, 'price')
            make_fake_request(receiver_service_id=8, fake_status_code=200)
            if price is None:
                price = 0  # Default price if not found
            else:
                price = float(price)
            
            title = redis_client.hget(title_key, 'title')
            make_fake_request(receiver_service_id=8, fake_status_code=200)
            if title is None:
                title = 'undefined'

            cart_response[movie_id] = {
                'quantity': int(quantity),
                'price': price,
                'title': title
            }

        return jsonify({
            'cart': cart_response,
            'total': float(total) if total else 0.0
        })
    
    @app.route('/api/update_cart', methods=['POST'])
    def update_cart():
        user_id = request.json['user_id']
        movie_id = request.json['movie_id']
        price = request.json['price']
        change = request.json.get('change', 1)
        title = request.json['title']

        # Generate Redis keys
        cart_key = f"cart:{user_id}"
        total_key = f"total:{user_id}"
        price_key = f"price:{movie_id}"
        title_key = f"title:{movie_id}"

        current_quantity = redis_client.hget(cart_key, movie_id)
        make_fake_request(receiver_service_id=8, fake_status_code=200)
        if current_quantity is None:
            current_quantity = 0
        else:
            current_quantity = int(current_quantity)
        
        # Update the cart only if the final quantity is non-negative
        if current_quantity + change >= 0:
            redis_client.hincrby(cart_key, movie_id, change)
            make_fake_request(receiver_service_id=8, fake_status_code=200)
            redis_client.incrbyfloat(total_key, price * change)
            make_fake_request(receiver_service_id=8, fake_status_code=200)
            # Store/update the price in a separate hash
            redis_client.hset(price_key, 'price', price)
            make_fake_request(receiver_service_id=8, fake_status_code=200)
            redis_client.hset(title_key, 'title', title)
            make_fake_request(receiver_service_id=8, fake_status_code=200)
        else:
            return jsonify({'error': 'Cannot reduce quantity below zero'}), 400
        
        return get_cart(user_id)

    @app.route('/api/get_cart', methods=['GET'])
    def get_cart_api():
        user_id = request.json['user_id']
        return get_cart(user_id)
    
    @app.route('/', methods=['GET'])
    def hello_world():
        return "Hello World from Cart!"
    return app

