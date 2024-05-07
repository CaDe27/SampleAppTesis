from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import json 
import random
from pathlib import Path

top10ids_df = None
movie_info_df = None
config = None

def load_movie_data(app):
    global top10ids_df
    top10ids_path = os.path.join(app.root_path, 'static', 'data', 'csv', 'content_top10_df.csv')
    top10ids_df = pd.read_csv(top10ids_path)

    movie_info_1_path = os.path.join(app.root_path, 'static', 'data', 'csv', 'movie_info.csv')
    movie_info_1_df = pd.read_csv(movie_info_1_path)

    movie_info_2_path = os.path.join(app.root_path, 'static', 'data', 'csv', 'movie_info_stats.csv')
    movie_info_2_df = pd.read_csv(movie_info_2_path)

    global movie_info_df
    movie_info_df = pd.merge(movie_info_1_df, movie_info_2_df, on='movieId', how='inner')
    movie_info_df['title'] = movie_info_df['title'].str.replace(r" \(\d{4}\)", "", regex=True)

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

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    load_movie_data(app)
    load_config()

    @app.route('/api/top10', methods=['GET'])
    def get_top10():
        service_url = get_service_url("product_catalog")
        top10_ids = top10ids_df['id'].tolist()
        top10_movies = movie_info_df[movie_info_df['movieId'].isin(top10_ids)]

        # Convert DataFrame to a list of dictionaries
        top10_movies_list = top10_movies.to_dict(orient='records')
        
        # Correctly add movie_url to each dictionary in the list
        for movie in top10_movies_list:
            movie['movie_url'] = f"{service_url}/static/data/movie_images/{movie['movieId']}.jpg"
        # Use jsonify to send the list of dictionaries as a JSON response
        return jsonify(top10_movies_list)

    @app.route('/api/search', methods=['GET'])
    def search_movies():
        # Get the search query from URL parameters
        search_query = request.args.get('query', '').lower()  
        if not search_query:
            return jsonify({"error": "No search query provided"}), 400

        service_url = get_service_url("product_catalog")

        # Filter movies that contain the search_query in their name
        filtered_movies = movie_info_df[movie_info_df['title'].str.lower().str.contains(search_query)]

        # Convert DataFrame to a list of dictionaries
        filtered_movies_list = filtered_movies.to_dict(orient='records')

        # Correctly add movie_url and price to each dictionary in the list
        for movie in filtered_movies_list:
            movie['movie_url'] = f"{service_url}/static/data/movie_images/{movie['movieId']}.jpg"
        
        return jsonify(filtered_movies_list)

    @app.route('/api/get_price', methods=['GET'])
    def get_price():
        movie_id = int(request.args.get('movie_id'))
        if movie_id is not None:
            try:
                # Assuming movie_info_df is defined elsewhere and accessible here
                price = movie_info_df.loc[movie_info_df['movieId'] == movie_id, 'price_USD'].iloc[0]
                return jsonify({'price_USD': price}), 200
            except IndexError:
                # Handle case where the movie_id is not found
                return jsonify({'error': 'Movie ID not found'}), 404
        else:
            # Handle case where movie_id was not provided
            return jsonify({'error': 'No movie_id provided'}), 400

    return app

